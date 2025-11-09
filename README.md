# Amazon Book Trends Analyzer

A comprehensive Python tool for analyzing trending book niches on Amazon with month-by-month filtering, data collection, trend analysis, and interactive reporting. **Now includes a beautiful web interface!**

## ✨ Features

- **🌐 Modern Web Interface**: Beautiful, responsive web application with interactive charts
- **📊 Data Collection**: Automated scraping of Amazon bestseller lists with responsible anti-scraping measures
- **💾 Data Storage**: Efficient SQLite database with optimized queries
- **📈 Trend Analysis**: Calculate growth rates, rank improvements, and trending niches
- **🔍 Month-by-Month Filtering**: Analyze trends across any time period
- **📋 Multiple Export Formats**: Export reports as CSV or JSON
- **🎨 Dual Interface**: Both web UI and CLI available
- **📚 Historical Data**: Track up to 12 months of historical data
- **📊 Interactive Charts**: Powered by Plotly for beautiful visualizations

## 🚀 Quick Start (Web Interface)

The easiest way to use this tool is through the web interface:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate sample data
python3 main.py generate-sample-data --months 12

# 3. Run the web application
python3 app.py
```

Then open your browser to **http://localhost:5000** and explore the beautiful interface!

## Project Structure

```
trending-book-niches/
├── app.py              # Flask web application
├── config.py           # Configuration settings
├── database.py         # Database operations (SQLite)
├── scraper.py          # Amazon web scraper
├── analyzer.py         # Trend analysis engine
├── cli.py              # Command-line interface
├── main.py             # CLI entry point
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
│   ├── base.html       # Base template
│   ├── index.html      # Dashboard
│   ├── trending.html   # Trending categories
│   ├── category.html   # Category details
│   ├── books.html      # Top books
│   └── about.html      # About page
├── static/             # Static assets
│   ├── css/style.css   # Custom CSS
│   └── js/main.js      # JavaScript
├── data/               # Data directory
│   ├── books.db        # SQLite database
│   └── exports/        # Exported reports
└── README.md           # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone or download this repository**

```bash
cd trending-book-niches
```

2. **Create a virtual environment (recommended)**

```bash
# On Linux/Mac
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Verify installation**

```bash
python main.py --help
```

## Quick Start

### 1. Generate Sample Data

To get started quickly with sample data for testing:

```bash
python main.py generate-sample-data --months 12
```

This generates 12 months of realistic sample book data across multiple categories.

### 2. View Available Data

Check what categories and months are available:

```bash
python main.py list-data
```

### 3. Analyze Trending Categories

View trending categories between two months:

```bash
python main.py trending --start-month 2024-01 --end-month 2024-12
```

## 🌐 Web Interface Guide

### Starting the Web Application

```bash
python3 app.py
```

The web server will start at **http://localhost:5000**

### Web Interface Features

#### 📊 **Dashboard** (/)
- Overview statistics (categories, books, months tracked)
- Quick trending chart
- Category browser
- Quick actions (generate sample data, view trending, etc.)

#### 📈 **Trending Categories** (/trending)
- Interactive filters for date ranges
- Top trending categories with composite scores
- Detailed metrics table (rank improvement, book growth, review growth)
- Export to CSV/JSON
- Interactive bar charts

#### 📂 **Category Details** (/category/<category-name>)
- Performance timeline chart
- Monthly metrics table
- Top performing books in selected month
- Fastest growing books in the category

#### 📖 **Top Books** (/books)
- Filter by category and month
- Detailed book rankings
- Sales rank, reviews, ratings, and prices
- Category browser

#### ℹ️ **About** (/about)
- Methodology explanation
- Trend score formula
- Technology stack
- Getting started guide

### API Endpoints

The web application also provides RESTful API endpoints:

- `GET /api/stats` - Overall statistics
- `GET /api/trending?start_month=YYYY-MM&end_month=YYYY-MM` - Trending categories
- `GET /api/category/<category>/timeline` - Category timeline
- `GET /api/category/<category>/books?month=YYYY-MM` - Top books
- `GET /api/category/<category>/growing` - Fastest growing books
- `GET /api/chart/trending` - Trending chart data (Plotly JSON)
- `GET /api/chart/category/<category>/timeline` - Category timeline chart
- `GET /api/export/trending?format=csv|json` - Export trending data

### Example API Usage

```bash
# Get overall stats
curl http://localhost:5000/api/stats

# Get trending categories
curl "http://localhost:5000/api/trending?start_month=2024-01&end_month=2024-12"

# Get top books in romance category
curl "http://localhost:5000/api/category/romance/books?month=2024-12&limit=10"

# Export trending data as CSV
curl "http://localhost:5000/api/export/trending?start_month=2024-01&end_month=2024-12&format=csv" -o trending.csv
```

## 💻 CLI Usage Guide

### Commands Overview

| Command | Description |
|---------|-------------|
| `generate-sample-data` | Generate sample historical data |
| `trending` | Show trending categories for a period |
| `category` | Show detailed analysis for a category |
| `top-books` | Show top books in a category for a month |
| `growing` | Show fastest growing books |
| `list-data` | List available categories and months |
| `scrape` | Scrape Amazon bestseller lists (use responsibly!) |

### Detailed Command Examples

#### 1. Generate Sample Data

Generate historical data for testing:

```bash
# Generate 12 months of sample data
python main.py generate-sample-data --months 12

# Generate 6 months of sample data
python main.py generate-sample-data --months 6
```

#### 2. View Trending Categories

Analyze which categories are trending:

```bash
# Show top 20 trending categories from Jan to Dec 2024
python main.py trending --start-month 2024-01 --end-month 2024-12 --limit 20

# Export results to CSV
python main.py trending --start-month 2024-01 --end-month 2024-12 --export csv

# Export results to JSON
python main.py trending --start-month 2024-01 --end-month 2024-12 --export json
```

**Output includes:**
- Trend score (composite metric)
- Rank improvement percentage
- Book count growth
- Average price and rating

#### 3. Analyze a Specific Category

Get detailed timeline for a category:

```bash
# View all data for romance category
python main.py category --category romance

# View specific time period
python main.py category --category self-help --start-month 2024-06 --end-month 2024-12

# Export to CSV
python main.py category --category romance --export csv
```

**Output includes:**
- Monthly book counts
- Average sales and category ranks
- Price trends
- Review counts and ratings

#### 4. View Top Books in a Category

See the best-performing books:

```bash
# Top 10 books in romance for December 2024
python main.py top-books --category romance --month 2024-12 --limit 10

# Top 20 books with export
python main.py top-books --category self-help --month 2024-11 --limit 20 --export csv
```

#### 5. Find Fastest Growing Books

Identify books with biggest rank improvements:

```bash
# Fastest growing books in a category
python main.py growing --category romance --start-month 2024-01 --end-month 2024-12

# Limit to top 5 and export
python main.py growing --category self-help --start-month 2024-06 --end-month 2024-12 --limit 5 --export json
```

#### 6. List Available Data

See what's in your database:

```bash
python main.py list-data
```

#### 7. Scrape Live Amazon Data

**⚠️ Use Responsibly! Please respect Amazon's Terms of Service**

```bash
# Scrape specific categories
python main.py scrape --categories "romance,self-help,mystery-thriller-suspense" --pages 1

# Scrape all configured categories
python main.py scrape --pages 2
```

## Configuration

Edit `config.py` to customize:

### Scraping Settings

```python
SCRAPING_CONFIG = {
    'delay_min': 2,      # Minimum delay between requests (seconds)
    'delay_max': 5,      # Maximum delay between requests (seconds)
    'timeout': 30,       # Request timeout (seconds)
    'max_retries': 3,    # Maximum number of retries per request
}
```

### Categories to Track

```python
AMAZON_CATEGORIES = [
    'mystery-thriller-suspense',
    'science-fiction-fantasy',
    'romance',
    'self-help',
    # Add more categories...
]
```

### Analysis Parameters

```python
ANALYSIS_CONFIG = {
    'min_reviews_threshold': 10,   # Minimum reviews for analysis
    'growth_threshold': 0.15,       # 15% growth threshold
    'top_n_niches': 20,            # Default number of top niches
}
```

## Data Analysis Methodology

### Trend Score Calculation

The trend score is a composite metric calculated as:

```
Trend Score = (Rank Improvement × 0.4) + (Book Count Growth × 0.3) + (Review Growth × 0.3)
```

Where:
- **Rank Improvement**: Percentage improvement in average category rank (lower rank is better)
- **Book Count Growth**: Percentage increase in number of books in category
- **Review Growth**: Percentage increase in total reviews

### Metrics Explained

- **Sales Rank (BSR)**: Amazon Best Sellers Rank - lower is better
- **Category Rank**: Rank within specific category - lower is better
- **Review Count**: Total number of customer reviews
- **Rating**: Average customer rating (1-5 stars)
- **Rank Improvement**: Positive percentage means rank improved (got lower)

## Export Formats

### CSV Export

Exports to `data/exports/` directory with columns ready for Excel or data analysis tools.

```bash
python main.py trending --start-month 2024-01 --end-month 2024-12 --export csv
```

### JSON Export

Exports to `data/exports/` directory in structured JSON format for API integration or further processing.

```bash
python main.py trending --start-month 2024-01 --end-month 2024-12 --export json
```

## Database Schema

The tool uses SQLite with three main tables:

### Books Table
- `id`: Primary key
- `asin`: Amazon Standard Identification Number
- `title`: Book title
- `author`: Author name
- `category`: Main category
- `subcategory`: Subcategory (optional)
- `publication_date`: Publication date

### Book Snapshots Table
- `id`: Primary key
- `book_id`: Foreign key to books
- `snapshot_date`: Date of snapshot
- `sales_rank`: Overall Amazon sales rank
- `category_rank`: Rank within category
- `price`: Book price
- `review_count`: Number of reviews
- `rating`: Average rating

### Categories Table
- `id`: Primary key
- `name`: Category name
- `parent_category`: Parent category
- `description`: Category description

## Responsible Web Scraping

This tool implements several anti-scraping best practices:

1. **Random Delays**: 2-5 second delays between requests
2. **User Agent Rotation**: Rotates between multiple user agents
3. **Retry Logic**: Exponential backoff on failures
4. **Rate Limiting**: Respects server responses
5. **Proxy Support**: Optional proxy rotation (configure in `config.py`)

**Important Notes:**
- Amazon's Terms of Service may prohibit automated scraping
- Use the sample data generation feature for testing
- Consider using Amazon's Product Advertising API for production use
- Implement delays and be respectful of server resources

## Troubleshooting

### Issue: "No data available"

**Solution**: Generate sample data first:
```bash
python main.py generate-sample-data --months 12
```

### Issue: "ImportError: No module named..."

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Issue: Database locked error

**Solution**: Close other connections to the database or restart the application

### Issue: Scraping returns no results

**Solutions:**
- Amazon may have changed their HTML structure
- You may be rate-limited (wait and try again)
- Check your internet connection
- Use sample data generation instead

## Advanced Usage

### Using as a Python Library

```python
from analyzer import TrendAnalyzer
from database import BookDatabase

# Initialize analyzer
analyzer = TrendAnalyzer()

# Get trending categories
trending = analyzer.get_trending_categories('2024-01', '2024-12')
print(trending)

# Get category timeline
timeline = analyzer.get_category_timeline('romance', '2024-01', '2024-12')
print(timeline)

# Get top books
top_books = analyzer.get_top_books_in_category('romance', '2024-12', limit=10)
print(top_books)
```

### Custom Analysis Scripts

Create custom analysis scripts in the project directory:

```python
# my_analysis.py
from analyzer import TrendAnalyzer
import matplotlib.pyplot as plt

analyzer = TrendAnalyzer()
timeline = analyzer.get_category_timeline('romance')

# Create visualization
plt.plot(timeline['month'], timeline['book_count'])
plt.xlabel('Month')
plt.ylabel('Number of Books')
plt.title('Romance Category Growth')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('romance_growth.png')
```

## Scheduling Data Collection

### Using Cron (Linux/Mac)

Add to crontab to scrape daily:

```bash
# Edit crontab
crontab -e

# Add line to scrape daily at 2 AM
0 2 * * * cd /path/to/trending-book-niches && /path/to/venv/bin/python main.py scrape --pages 1
```

### Using Task Scheduler (Windows)

1. Open Task Scheduler
2. Create new task
3. Set trigger (e.g., daily at 2 AM)
4. Set action: `python C:\path\to\main.py scrape --pages 1`

## API Integration Options

For production use, consider these alternatives to scraping:

1. **Amazon Product Advertising API**: Official API with usage limits
2. **Rainforest API**: Third-party Amazon data API
3. **ScraperAPI**: Proxy service for web scraping
4. **ParseHub**: Visual web scraping tool

## Performance Optimization

### Database Indexing

The database automatically creates indexes on:
- `books.category`
- `book_snapshots.snapshot_date`
- `book_snapshots.book_id, snapshot_date`

### Query Optimization

For large datasets:
```python
# Use date ranges to limit data
analyzer.get_trending_categories('2024-11', '2024-12')

# Limit result sets
analyzer.get_top_books_in_category('romance', '2024-12', limit=10)
```

## Contributing

Contributions are welcome! Areas for improvement:

- Additional data sources
- More analysis metrics
- Visualization dashboard
- API endpoints
- Category auto-detection
- Machine learning predictions

## License

This tool is for educational purposes. Please respect Amazon's Terms of Service and use responsibly.

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review the example commands
3. Inspect the code comments
4. Test with sample data first

## Changelog

### Version 1.0.0
- Initial release
- Amazon scraper with anti-scraping measures
- SQLite database with optimized schema
- Trend analysis engine
- CLI interface with export capabilities
- Sample data generation
- Comprehensive documentation

## Credits

Built with:
- Python 3.8+
- BeautifulSoup4 for HTML parsing
- Pandas for data analysis
- Click for CLI interface
- Colorama for colored output
- SQLite for data storage

---

**Happy analyzing! 📚📊**
