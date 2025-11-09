"""
Web scraper for Amazon bestseller lists with anti-scraping measures
"""
import time
import random
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from tqdm import tqdm

from config import (
    SCRAPING_CONFIG,
    AMAZON_CATEGORIES,
    BESTSELLER_URL_TEMPLATE,
    AMAZON_BASE_URL,
    USER_AGENTS
)
from database import BookDatabase


class AmazonScraper:
    """
    Scraper for Amazon bestseller lists with responsible scraping practices

    Features:
    - Random delays between requests
    - User agent rotation
    - Proxy support (optional)
    - Retry logic with exponential backoff
    """

    def __init__(self, use_proxies: bool = False):
        self.config = SCRAPING_CONFIG
        self.use_proxies = use_proxies
        self.ua = UserAgent()
        self.session = requests.Session()
        self.db = BookDatabase()

    def get_headers(self) -> Dict[str, str]:
        """Generate request headers with random user agent"""
        return {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def random_delay(self):
        """Add random delay between requests"""
        delay = random.uniform(self.config['delay_min'], self.config['delay_max'])
        time.sleep(delay)

    def fetch_page(self, url: str, retries: int = None) -> Optional[BeautifulSoup]:
        """
        Fetch a page with retry logic

        Args:
            url: URL to fetch
            retries: Number of retries (defaults to config value)

        Returns:
            BeautifulSoup object or None if failed
        """
        if retries is None:
            retries = self.config['max_retries']

        for attempt in range(retries):
            try:
                self.random_delay()

                response = self.session.get(
                    url,
                    headers=self.get_headers(),
                    timeout=self.config['timeout']
                )

                if response.status_code == 200:
                    return BeautifulSoup(response.content, 'lxml')
                elif response.status_code == 503:
                    # Amazon is blocking, wait longer
                    print(f"⚠️  Rate limited (503), waiting {2 ** attempt * 5} seconds...")
                    time.sleep(2 ** attempt * 5)
                else:
                    print(f"❌ HTTP {response.status_code} for {url}")

            except requests.RequestException as e:
                print(f"❌ Request failed (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)

        return None

    def parse_bestseller_page(self, soup: BeautifulSoup, category: str) -> List[Dict]:
        """
        Parse bestseller page and extract book information

        Args:
            soup: BeautifulSoup object of the page
            category: Category name

        Returns:
            List of book dictionaries
        """
        books = []

        # Find all book items on the page
        # Note: Amazon's HTML structure changes frequently, this is a general approach
        book_items = soup.find_all('div', {'class': re.compile(r'zg-grid-general-faceout')}) or \
                     soup.find_all('div', {'id': re.compile(r'gridItemRoot')})

        for item in book_items:
            try:
                book_data = {}

                # Extract ASIN (Amazon Standard Identification Number)
                asin_tag = item.find('a', href=re.compile(r'/dp/[A-Z0-9]{10}'))
                if asin_tag:
                    match = re.search(r'/dp/([A-Z0-9]{10})', asin_tag['href'])
                    book_data['asin'] = match.group(1) if match else None

                # Extract title
                title_tag = item.find('div', {'class': re.compile(r'_cDEzb_p13n-sc-css-line-clamp-1')}) or \
                           item.find('img', alt=True)
                if title_tag:
                    book_data['title'] = title_tag.get('alt') if title_tag.name == 'img' else title_tag.get_text(strip=True)

                # Extract author
                author_tag = item.find('div', {'class': re.compile(r'a-row a-size-small')}) or \
                            item.find('a', {'class': re.compile(r'a-size-small')})
                if author_tag:
                    book_data['author'] = author_tag.get_text(strip=True)

                # Extract price
                price_tag = item.find('span', {'class': re.compile(r'_cDEzb_p13n-sc-price')}) or \
                           item.find('span', {'class': 'a-price-whole'})
                if price_tag:
                    price_text = price_tag.get_text(strip=True).replace('$', '').replace(',', '')
                    try:
                        book_data['price'] = float(price_text)
                    except ValueError:
                        book_data['price'] = None

                # Extract rating
                rating_tag = item.find('span', {'class': re.compile(r'a-icon-alt')})
                if rating_tag:
                    rating_text = rating_tag.get_text(strip=True)
                    match = re.search(r'([\d.]+)', rating_text)
                    if match:
                        book_data['rating'] = float(match.group(1))

                # Extract review count
                review_tag = item.find('span', {'class': re.compile(r'a-size-small')})
                if review_tag:
                    review_text = review_tag.get_text(strip=True).replace(',', '')
                    match = re.search(r'(\d+)', review_text)
                    if match:
                        book_data['review_count'] = int(match.group(1))

                # Extract rank
                rank_tag = item.find('span', {'class': re.compile(r'zg-badge-text')})
                if rank_tag:
                    rank_text = rank_tag.get_text(strip=True).replace('#', '')
                    try:
                        book_data['rank'] = int(rank_text)
                    except ValueError:
                        book_data['rank'] = None

                book_data['category'] = category

                # Only add if we have at least title and ASIN
                if book_data.get('title') and book_data.get('asin'):
                    books.append(book_data)

            except Exception as e:
                print(f"⚠️  Error parsing book item: {e}")
                continue

        return books

    def scrape_category(self, category: str, max_pages: int = 1) -> List[Dict]:
        """
        Scrape books from a specific category

        Args:
            category: Category identifier
            max_pages: Maximum number of pages to scrape

        Returns:
            List of book dictionaries
        """
        print(f"\n📚 Scraping category: {category}")
        all_books = []

        for page in range(1, max_pages + 1):
            # Construct URL for the category bestsellers
            url = f"{BESTSELLER_URL_TEMPLATE}/{category}"
            if page > 1:
                url += f"?pg={page}"

            print(f"  Fetching page {page}...")
            soup = self.fetch_page(url)

            if soup:
                books = self.parse_bestseller_page(soup, category)
                all_books.extend(books)
                print(f"  ✓ Found {len(books)} books on page {page}")
            else:
                print(f"  ✗ Failed to fetch page {page}")
                break

        return all_books

    def scrape_all_categories(self, categories: List[str] = None, max_pages_per_category: int = 1) -> Dict[str, List[Dict]]:
        """
        Scrape multiple categories

        Args:
            categories: List of category identifiers (defaults to AMAZON_CATEGORIES)
            max_pages_per_category: Maximum pages per category

        Returns:
            Dictionary mapping category to list of books
        """
        if categories is None:
            categories = AMAZON_CATEGORIES

        results = {}

        print(f"\n🚀 Starting scrape of {len(categories)} categories...")

        for category in tqdm(categories, desc="Categories"):
            books = self.scrape_category(category, max_pages_per_category)
            results[category] = books
            print(f"✓ Completed {category}: {len(books)} books")

        print(f"\n✅ Scraping complete! Total books: {sum(len(b) for b in results.values())}")
        return results

    def save_to_database(self, books: List[Dict], snapshot_date: str = None):
        """
        Save scraped books to database

        Args:
            books: List of book dictionaries
            snapshot_date: Date of the snapshot (defaults to today)
        """
        if snapshot_date is None:
            snapshot_date = datetime.now().strftime('%Y-%m-%d')

        print(f"\n💾 Saving {len(books)} books to database...")

        for book in tqdm(books, desc="Saving books"):
            try:
                # Insert book
                book_id = self.db.insert_book(
                    asin=book.get('asin', ''),
                    title=book.get('title', 'Unknown'),
                    author=book.get('author', 'Unknown'),
                    category=book.get('category', 'Unknown'),
                    subcategory=book.get('subcategory'),
                    publication_date=book.get('publication_date')
                )

                # Insert snapshot
                self.db.insert_snapshot(
                    book_id=book_id,
                    snapshot_date=snapshot_date,
                    sales_rank=book.get('sales_rank'),
                    category_rank=book.get('rank'),
                    price=book.get('price'),
                    review_count=book.get('review_count'),
                    rating=book.get('rating')
                )
            except Exception as e:
                print(f"⚠️  Error saving book {book.get('title', 'Unknown')}: {e}")

        print("✅ Database save complete!")

    def generate_sample_historical_data(self, months: int = 12):
        """
        Generate sample historical data for testing

        This creates simulated monthly snapshots for the past N months
        with realistic variations in rankings, prices, and reviews.

        Args:
            months: Number of months of historical data to generate
        """
        print(f"\n🔄 Generating {months} months of sample historical data...")

        # Define sample books for each category
        sample_books = {
            'mystery-thriller-suspense': [
                {'asin': 'B001', 'title': 'The Silent Patient', 'author': 'Alex Michaelides', 'base_rank': 15, 'base_price': 14.99, 'base_reviews': 45000},
                {'asin': 'B002', 'title': 'Gone Girl', 'author': 'Gillian Flynn', 'base_rank': 25, 'base_price': 12.99, 'base_reviews': 65000},
                {'asin': 'B003', 'title': 'The Guest List', 'author': 'Lucy Foley', 'base_rank': 35, 'base_price': 13.99, 'base_reviews': 35000},
            ],
            'science-fiction-fantasy': [
                {'asin': 'B101', 'title': 'Project Hail Mary', 'author': 'Andy Weir', 'base_rank': 10, 'base_price': 15.99, 'base_reviews': 55000},
                {'asin': 'B102', 'title': 'The Name of the Wind', 'author': 'Patrick Rothfuss', 'base_rank': 20, 'base_price': 16.99, 'base_reviews': 48000},
                {'asin': 'B103', 'title': 'Dune', 'author': 'Frank Herbert', 'base_rank': 12, 'base_price': 18.99, 'base_reviews': 72000},
            ],
            'romance': [
                {'asin': 'B201', 'title': 'It Ends with Us', 'author': 'Colleen Hoover', 'base_rank': 5, 'base_price': 11.99, 'base_reviews': 125000},
                {'asin': 'B202', 'title': 'People We Meet on Vacation', 'author': 'Emily Henry', 'base_rank': 18, 'base_price': 12.99, 'base_reviews': 42000},
                {'asin': 'B203', 'title': 'The Love Hypothesis', 'author': 'Ali Hazelwood', 'base_rank': 22, 'base_price': 10.99, 'base_reviews': 38000},
            ],
            'self-help': [
                {'asin': 'B301', 'title': 'Atomic Habits', 'author': 'James Clear', 'base_rank': 3, 'base_price': 16.99, 'base_reviews': 95000},
                {'asin': 'B302', 'title': 'The 7 Habits of Highly Effective People', 'author': 'Stephen Covey', 'base_rank': 8, 'base_price': 14.99, 'base_reviews': 88000},
                {'asin': 'B303', 'title': 'Mindset', 'author': 'Carol Dweck', 'base_rank': 28, 'base_price': 15.99, 'base_reviews': 52000},
            ],
            'business-money': [
                {'asin': 'B401', 'title': 'Rich Dad Poor Dad', 'author': 'Robert Kiyosaki', 'base_rank': 7, 'base_price': 8.99, 'base_reviews': 110000},
                {'asin': 'B402', 'title': 'The Lean Startup', 'author': 'Eric Ries', 'base_rank': 32, 'base_price': 17.99, 'base_reviews': 46000},
                {'asin': 'B403', 'title': 'Think and Grow Rich', 'author': 'Napoleon Hill', 'base_rank': 19, 'base_price': 9.99, 'base_reviews': 76000},
            ],
        }

        # Generate snapshots for each month
        end_date = datetime.now()

        for month_offset in range(months):
            snapshot_date = (end_date - timedelta(days=30 * month_offset)).strftime('%Y-%m-%d')
            print(f"  Generating data for {snapshot_date}...")

            for category, books in sample_books.items():
                for book in books:
                    # Add realistic variations
                    rank_variance = random.randint(-5, 10)
                    price_variance = random.uniform(-2, 2)
                    review_growth = random.randint(100, 1000) * month_offset

                    # Calculate trending factor (some books improve over time)
                    trend_factor = 1 - (month_offset * 0.05) if random.random() > 0.5 else 1 + (month_offset * 0.03)

                    book_id = self.db.insert_book(
                        asin=book['asin'],
                        title=book['title'],
                        author=book['author'],
                        category=category
                    )

                    self.db.insert_snapshot(
                        book_id=book_id,
                        snapshot_date=snapshot_date,
                        sales_rank=int(book['base_rank'] * trend_factor) + rank_variance,
                        category_rank=int(book['base_rank'] * trend_factor) + rank_variance,
                        price=round(book['base_price'] + price_variance, 2),
                        review_count=book['base_reviews'] + review_growth,
                        rating=round(random.uniform(4.0, 4.8), 1)
                    )

        print("✅ Sample historical data generated!")


def main():
    """Example usage of the scraper"""
    scraper = AmazonScraper()

    # Option 1: Generate sample data for testing
    print("Generating sample historical data for testing...")
    scraper.generate_sample_historical_data(months=12)

    # Option 2: Scrape live data (uncomment to use)
    # results = scraper.scrape_all_categories(categories=['mystery-thriller-suspense'], max_pages_per_category=1)
    # scraper.save_to_database(sum(results.values(), []))


if __name__ == '__main__':
    main()
