#!/usr/bin/env python3
"""
Build script for Render deployment
Generates sample data on first deployment
"""
import os
from scraper import AmazonScraper

def main():
    print("🚀 Starting Render build...")

    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('data/exports', exist_ok=True)

    # Check if database already exists
    db_path = 'data/books.db'

    if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
        print("📊 No database found. Generating sample data...")
        scraper = AmazonScraper()
        scraper.generate_sample_historical_data(months=12)
        print("✅ Sample data generated!")
    else:
        print("✅ Database already exists, skipping data generation")

    print("🎉 Build complete!")

if __name__ == '__main__':
    main()
