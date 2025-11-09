"""
Configuration settings for Amazon Book Trends Analyzer
"""
import os
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
DB_PATH = DATA_DIR / 'books.db'
EXPORTS_DIR = DATA_DIR / 'exports'

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
EXPORTS_DIR.mkdir(exist_ok=True)

# Scraping configuration
SCRAPING_CONFIG = {
    'delay_min': 2,  # Minimum delay between requests (seconds)
    'delay_max': 5,  # Maximum delay between requests (seconds)
    'timeout': 30,   # Request timeout (seconds)
    'max_retries': 3,  # Maximum number of retries per request
    'use_proxies': False,  # Enable proxy rotation
}

# Amazon categories to track
AMAZON_CATEGORIES = [
    'mystery-thriller-suspense',
    'science-fiction-fantasy',
    'romance',
    'literature-fiction',
    'business-money',
    'self-help',
    'cookbooks-food-wine',
    'biographies-memoirs',
    'history',
    'health-fitness-dieting',
    'religion-spirituality',
    'parenting-relationships',
    'crafts-hobbies-home',
    'teen-young-adult',
    'children-books',
]

# Amazon bestseller URLs
AMAZON_BASE_URL = 'https://www.amazon.com'
BESTSELLER_URL_TEMPLATE = f'{AMAZON_BASE_URL}/Best-Sellers-Books/zgbs/books'

# User agent rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
]

# Analysis configuration
ANALYSIS_CONFIG = {
    'min_reviews_threshold': 10,  # Minimum reviews to be considered in trending analysis
    'growth_threshold': 0.15,  # 15% growth to be considered trending
    'top_n_niches': 20,  # Number of top niches to show by default
}

# Data collection schedule
COLLECTION_CONFIG = {
    'months_to_track': 12,  # Number of months of historical data
    'books_per_category': 100,  # Number of books to collect per category
}
