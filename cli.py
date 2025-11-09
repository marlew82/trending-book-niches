"""
Command-line interface for Amazon Book Trends Analyzer
"""
import json
from datetime import datetime
from pathlib import Path
import click
from tabulate import tabulate
from colorama import init, Fore, Style

from analyzer import TrendAnalyzer
from scraper import AmazonScraper
from database import BookDatabase
from config import EXPORTS_DIR, AMAZON_CATEGORIES

# Initialize colorama for colored terminal output
init(autoreset=True)


class BookTrendsCLI:
    """CLI application for book trends analysis"""

    def __init__(self):
        self.analyzer = TrendAnalyzer()
        self.scraper = AmazonScraper()
        self.db = BookDatabase()

    def print_header(self, text: str):
        """Print formatted header"""
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'=' * 60}")
        print(f"{text.center(60)}")
        print(f"{'=' * 60}{Style.RESET_ALL}\n")

    def print_success(self, text: str):
        """Print success message"""
        print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")

    def print_error(self, text: str):
        """Print error message"""
        print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")

    def print_info(self, text: str):
        """Print info message"""
        print(f"{Fore.BLUE}ℹ {text}{Style.RESET_ALL}")

    def export_to_csv(self, data, filename: str):
        """Export DataFrame to CSV"""
        filepath = EXPORTS_DIR / filename
        data.to_csv(filepath, index=False)
        self.print_success(f"Exported to {filepath}")

    def export_to_json(self, data, filename: str):
        """Export data to JSON"""
        filepath = EXPORTS_DIR / filename

        if hasattr(data, 'to_dict'):
            # It's a DataFrame
            json_data = data.to_dict('records')
        else:
            json_data = data

        with open(filepath, 'w') as f:
            json.dump(json_data, f, indent=2, default=str)

        self.print_success(f"Exported to {filepath}")

    def display_table(self, data, headers=None, max_rows=None):
        """Display data as a formatted table"""
        if data.empty:
            self.print_info("No data to display")
            return

        if max_rows:
            data = data.head(max_rows)

        print(tabulate(data, headers='keys' if headers is None else headers,
                      tablefmt='grid', showindex=False, floatfmt='.2f'))

    def show_trending_categories(self, start_month: str, end_month: str,
                                limit: int = 20, export: str = None):
        """Show trending categories"""
        self.print_header(f"Trending Categories: {start_month} to {end_month}")

        trending = self.analyzer.get_trending_categories(start_month, end_month, min_books=1)

        if trending.empty:
            self.print_error("No trending data available for this period")
            return

        # Prepare display data
        display_data = trending.head(limit).copy()
        display_data['trend_score'] = (display_data['trend_score'] * 100).round(2)
        display_data['rank_improvement'] = (display_data['rank_improvement'] * 100).round(2)
        display_data['book_count_growth'] = (display_data['book_count_growth'] * 100).round(2)
        display_data['review_growth'] = (display_data['review_growth'] * 100).round(2)

        # Rename columns for display
        display_data = display_data.rename(columns={
            'category': 'Category',
            'trend_score': 'Trend Score (%)',
            'rank_improvement': 'Rank Improvement (%)',
            'book_count_growth': 'Book Growth (%)',
            'review_growth': 'Review Growth (%)',
            'current_books': '# Books',
            'avg_price': 'Avg Price ($)',
            'avg_rating': 'Avg Rating',
        })

        columns_to_show = [
            'Category', 'Trend Score (%)', 'Rank Improvement (%)',
            '# Books', 'Avg Price ($)', 'Avg Rating'
        ]

        self.display_table(display_data[columns_to_show])

        # Export if requested
        if export:
            if export.lower() == 'csv':
                self.export_to_csv(trending, f'trending_categories_{start_month}_{end_month}.csv')
            elif export.lower() == 'json':
                self.export_to_json(trending, f'trending_categories_{start_month}_{end_month}.json')

    def show_category_details(self, category: str, start_month: str = None,
                             end_month: str = None, export: str = None):
        """Show detailed analysis for a specific category"""
        self.print_header(f"Category Details: {category}")

        timeline = self.analyzer.get_category_timeline(category, start_month, end_month)

        if timeline.empty:
            self.print_error(f"No data available for category '{category}'")
            return

        # Display timeline
        print(f"\n{Fore.YELLOW}Monthly Timeline:{Style.RESET_ALL}")
        display_data = timeline.copy()
        display_data = display_data.rename(columns={
            'month': 'Month',
            'book_count': '# Books',
            'avg_sales_rank': 'Avg Sales Rank',
            'avg_category_rank': 'Avg Category Rank',
            'avg_price': 'Avg Price ($)',
            'total_reviews': 'Total Reviews',
            'avg_rating': 'Avg Rating',
        })

        self.display_table(display_data[[
            'Month', '# Books', 'Avg Category Rank', 'Avg Price ($)',
            'Total Reviews', 'Avg Rating'
        ]])

        # Export if requested
        if export:
            if export.lower() == 'csv':
                self.export_to_csv(timeline, f'category_{category}_{start_month or "all"}.csv')
            elif export.lower() == 'json':
                self.export_to_json(timeline, f'category_{category}_{start_month or "all"}.json')

    def show_top_books(self, category: str, month: str, limit: int = 10,
                      export: str = None):
        """Show top books in a category for a month"""
        self.print_header(f"Top Books: {category} - {month}")

        top_books = self.analyzer.get_top_books_in_category(category, month, limit)

        if top_books.empty:
            self.print_error(f"No books found for {category} in {month}")
            return

        display_data = top_books.copy()
        display_data = display_data.rename(columns={
            'title': 'Title',
            'author': 'Author',
            'category_rank': 'Rank',
            'price': 'Price ($)',
            'review_count': 'Reviews',
            'rating': 'Rating',
        })

        self.display_table(display_data)

        # Export if requested
        if export:
            if export.lower() == 'csv':
                self.export_to_csv(top_books, f'top_books_{category}_{month}.csv')
            elif export.lower() == 'json':
                self.export_to_json(top_books, f'top_books_{category}_{month}.json')

    def show_fastest_growing(self, category: str, start_month: str,
                           end_month: str, limit: int = 10, export: str = None):
        """Show fastest growing books in a category"""
        self.print_header(f"Fastest Growing Books: {category}")

        growing = self.analyzer.get_fastest_growing_books(
            category, start_month, end_month, limit
        )

        if growing.empty:
            self.print_error(f"No growth data found for {category}")
            return

        display_data = growing.copy()
        display_data['rank_improvement'] = (display_data['rank_improvement'] * 100).round(2)
        display_data = display_data.rename(columns={
            'title': 'Title',
            'author': 'Author',
            'rank_improvement': 'Improvement (%)',
            'start_rank': 'Start Rank',
            'end_rank': 'End Rank',
            'review_growth': 'Review Growth',
            'current_price': 'Price ($)',
            'current_rating': 'Rating',
        })

        self.display_table(display_data)

        # Export if requested
        if export:
            if export.lower() == 'csv':
                self.export_to_csv(growing, f'fastest_growing_{category}_{start_month}_{end_month}.csv')
            elif export.lower() == 'json':
                self.export_to_json(growing, f'fastest_growing_{category}_{start_month}_{end_month}.json')

    def list_available_data(self):
        """List available categories and months"""
        self.print_header("Available Data")

        # Get categories
        categories = self.db.get_all_categories()
        print(f"{Fore.YELLOW}Categories:{Style.RESET_ALL}")
        for cat in categories:
            print(f"  • {cat}")

        # Get date range
        months = self.analyzer.get_available_months()
        print(f"\n{Fore.YELLOW}Available Months:{Style.RESET_ALL}")
        for month in months:
            print(f"  • {month}")

        # Get data range
        min_date, max_date = self.db.get_date_range()
        if min_date and max_date:
            print(f"\n{Fore.YELLOW}Data Range:{Style.RESET_ALL}")
            print(f"  From: {min_date}")
            print(f"  To: {max_date}")


@click.group()
def cli():
    """Amazon Book Trends Analyzer - Track trending book niches on Amazon"""
    pass


@cli.command()
@click.option('--months', default=12, help='Number of months of sample data to generate')
def generate_sample_data(months):
    """Generate sample historical data for testing"""
    cli_app = BookTrendsCLI()
    cli_app.print_header("Generating Sample Data")
    cli_app.scraper.generate_sample_historical_data(months)
    cli_app.print_success(f"Generated {months} months of sample data")


@cli.command()
@click.option('--start-month', required=True, help='Start month (YYYY-MM)')
@click.option('--end-month', required=True, help='End month (YYYY-MM)')
@click.option('--limit', default=20, help='Number of categories to show')
@click.option('--export', type=click.Choice(['csv', 'json', 'none']), default='none', help='Export format')
def trending(start_month, end_month, limit, export):
    """Show trending categories for a period"""
    cli_app = BookTrendsCLI()
    export_format = export if export != 'none' else None
    cli_app.show_trending_categories(start_month, end_month, limit, export_format)


@cli.command()
@click.option('--category', required=True, help='Category name')
@click.option('--start-month', help='Start month (YYYY-MM)')
@click.option('--end-month', help='End month (YYYY-MM)')
@click.option('--export', type=click.Choice(['csv', 'json', 'none']), default='none', help='Export format')
def category(category, start_month, end_month, export):
    """Show detailed analysis for a category"""
    cli_app = BookTrendsCLI()
    export_format = export if export != 'none' else None
    cli_app.show_category_details(category, start_month, end_month, export_format)


@cli.command()
@click.option('--category', required=True, help='Category name')
@click.option('--month', required=True, help='Month (YYYY-MM)')
@click.option('--limit', default=10, help='Number of books to show')
@click.option('--export', type=click.Choice(['csv', 'json', 'none']), default='none', help='Export format')
def top_books(category, month, limit, export):
    """Show top books in a category for a month"""
    cli_app = BookTrendsCLI()
    export_format = export if export != 'none' else None
    cli_app.show_top_books(category, month, limit, export_format)


@cli.command()
@click.option('--category', required=True, help='Category name')
@click.option('--start-month', required=True, help='Start month (YYYY-MM)')
@click.option('--end-month', required=True, help='End month (YYYY-MM)')
@click.option('--limit', default=10, help='Number of books to show')
@click.option('--export', type=click.Choice(['csv', 'json', 'none']), default='none', help='Export format')
def growing(category, start_month, end_month, limit, export):
    """Show fastest growing books in a category"""
    cli_app = BookTrendsCLI()
    export_format = export if export != 'none' else None
    cli_app.show_fastest_growing(category, start_month, end_month, limit, export_format)


@cli.command()
def list_data():
    """List available categories and months"""
    cli_app = BookTrendsCLI()
    cli_app.list_available_data()


@cli.command()
@click.option('--categories', help='Comma-separated list of categories to scrape')
@click.option('--pages', default=1, help='Number of pages per category')
def scrape(categories, pages):
    """Scrape Amazon bestseller lists (use responsibly!)"""
    cli_app = BookTrendsCLI()
    cli_app.print_header("Scraping Amazon")

    if categories:
        category_list = [c.strip() for c in categories.split(',')]
    else:
        category_list = AMAZON_CATEGORIES

    cli_app.print_info(f"Scraping {len(category_list)} categories, {pages} pages each")
    cli_app.print_info("⚠️  Please use responsibly and respect Amazon's terms of service")

    results = cli_app.scraper.scrape_all_categories(category_list, pages)
    cli_app.scraper.save_to_database(sum(results.values(), []))

    cli_app.print_success("Scraping complete!")


if __name__ == '__main__':
    cli()
