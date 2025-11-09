"""
Data analysis module for calculating book niche trends
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from collections import defaultdict

from database import BookDatabase
from config import ANALYSIS_CONFIG


class TrendAnalyzer:
    """
    Analyzes book data to identify trending niches and categories

    Features:
    - Month-over-month growth analysis
    - Sales rank improvement tracking
    - New release detection
    - Category performance metrics
    """

    def __init__(self):
        self.db = BookDatabase()
        self.config = ANALYSIS_CONFIG

    def calculate_growth_rate(self, old_value: float, new_value: float) -> float:
        """
        Calculate percentage growth rate

        Note: For sales rank, lower is better, so we invert the calculation

        Args:
            old_value: Previous period value
            new_value: Current period value

        Returns:
            Growth rate as a decimal (e.g., 0.15 for 15% growth)
        """
        if old_value == 0 or pd.isna(old_value):
            return 0.0

        # For sales rank, improvement means lower number
        # So we invert: if rank goes from 100 to 50, that's 50% improvement
        growth = (old_value - new_value) / old_value
        return growth

    def get_trending_categories(self, start_month: str, end_month: str,
                               min_books: int = 5) -> pd.DataFrame:
        """
        Identify trending categories based on various metrics

        Args:
            start_month: Start month in YYYY-MM format
            end_month: End month in YYYY-MM format
            min_books: Minimum number of books to consider category

        Returns:
            DataFrame with trending categories and their metrics
        """
        # Get monthly snapshots for the period
        start_date = f"{start_month}-01"
        end_date = f"{end_month}-28"

        monthly_data = self.db.get_monthly_snapshots(start_date, end_date)

        if monthly_data.empty:
            return pd.DataFrame()

        # Calculate metrics for each category
        category_trends = []

        for category in monthly_data['category'].unique():
            cat_data = monthly_data[monthly_data['category'] == category].copy()

            if len(cat_data) < 2:
                continue

            # Sort by month
            cat_data = cat_data.sort_values('month')

            # Get first and last month data
            first_month = cat_data.iloc[0]
            last_month = cat_data.iloc[-1]

            # Skip if not enough books
            if first_month['book_count'] < min_books:
                continue

            # Calculate various growth metrics
            rank_improvement = self.calculate_growth_rate(
                first_month['avg_category_rank'],
                last_month['avg_category_rank']
            )

            book_count_growth = self.calculate_growth_rate(
                first_month['book_count'],
                last_month['book_count']
            ) * -1  # More books is good, so invert

            review_growth = self.calculate_growth_rate(
                first_month['total_reviews'],
                last_month['total_reviews']
            ) * -1  # More reviews is good

            # Calculate composite trend score
            # Weights: rank improvement (40%), book growth (30%), review growth (30%)
            trend_score = (
                rank_improvement * 0.4 +
                book_count_growth * 0.3 +
                review_growth * 0.3
            )

            category_trends.append({
                'category': category,
                'trend_score': trend_score,
                'rank_improvement': rank_improvement,
                'book_count_growth': book_count_growth,
                'review_growth': review_growth,
                'current_books': int(last_month['book_count']),
                'avg_price': last_month['avg_price'],
                'avg_rating': last_month['avg_rating'],
                'total_reviews': int(last_month['total_reviews']),
                'avg_rank': last_month['avg_category_rank'],
            })

        # Create DataFrame and sort by trend score
        df = pd.DataFrame(category_trends)

        if not df.empty:
            df = df.sort_values('trend_score', ascending=False)

        return df

    def get_category_timeline(self, category: str, start_month: str = None,
                             end_month: str = None) -> pd.DataFrame:
        """
        Get monthly timeline data for a specific category

        Args:
            category: Category name
            start_month: Start month in YYYY-MM format
            end_month: End month in YYYY-MM format

        Returns:
            DataFrame with monthly metrics
        """
        start_date = f"{start_month}-01" if start_month else None
        end_date = f"{end_month}-28" if end_month else None

        monthly_data = self.db.get_monthly_snapshots(start_date, end_date)

        if monthly_data.empty:
            return pd.DataFrame()

        cat_data = monthly_data[monthly_data['category'] == category].copy()
        cat_data = cat_data.sort_values('month')

        return cat_data

    def get_top_books_in_category(self, category: str, month: str,
                                  limit: int = 10) -> pd.DataFrame:
        """
        Get top performing books in a category for a specific month

        Args:
            category: Category name
            month: Month in YYYY-MM format
            limit: Number of books to return

        Returns:
            DataFrame with top books
        """
        start_date = f"{month}-01"
        end_date = f"{month}-28"

        books_df = self.db.get_books_by_category(category, start_date, end_date)

        if books_df.empty:
            return pd.DataFrame()

        # Filter by month and sort by category rank
        books_df['month'] = pd.to_datetime(books_df['snapshot_date']).dt.strftime('%Y-%m')
        books_df = books_df[books_df['month'] == month]

        # Get the best rank for each book in the month
        top_books = books_df.sort_values('category_rank').drop_duplicates('asin').head(limit)

        return top_books[['title', 'author', 'category_rank', 'sales_rank',
                         'price', 'review_count', 'rating']]

    def get_fastest_growing_books(self, category: str, start_month: str,
                                 end_month: str, limit: int = 10) -> pd.DataFrame:
        """
        Find books with the biggest rank improvements

        Args:
            category: Category name
            start_month: Start month in YYYY-MM format
            end_month: End month in YYYY-MM format
            limit: Number of books to return

        Returns:
            DataFrame with fastest growing books
        """
        start_date = f"{start_month}-01"
        end_date = f"{end_month}-28"

        books_df = self.db.get_books_by_category(category, start_date, end_date)

        if books_df.empty:
            return pd.DataFrame()

        # Calculate rank changes for each book
        books_df['snapshot_date'] = pd.to_datetime(books_df['snapshot_date'])
        books_df = books_df.sort_values(['asin', 'snapshot_date'])

        growth_data = []

        for asin in books_df['asin'].unique():
            book_data = books_df[books_df['asin'] == asin].copy()

            if len(book_data) < 2:
                continue

            first_snapshot = book_data.iloc[0]
            last_snapshot = book_data.iloc[-1]

            if pd.isna(first_snapshot['category_rank']) or pd.isna(last_snapshot['category_rank']):
                continue

            rank_improvement = self.calculate_growth_rate(
                first_snapshot['category_rank'],
                last_snapshot['category_rank']
            )

            review_growth = last_snapshot['review_count'] - first_snapshot['review_count']

            growth_data.append({
                'title': last_snapshot['title'],
                'author': last_snapshot['author'],
                'rank_improvement': rank_improvement,
                'start_rank': int(first_snapshot['category_rank']),
                'end_rank': int(last_snapshot['category_rank']),
                'review_growth': int(review_growth) if not pd.isna(review_growth) else 0,
                'current_price': last_snapshot['price'],
                'current_rating': last_snapshot['rating'],
            })

        df = pd.DataFrame(growth_data)

        if not df.empty:
            df = df.sort_values('rank_improvement', ascending=False).head(limit)

        return df

    def get_new_releases(self, category: str, month: str) -> pd.DataFrame:
        """
        Find books that first appeared in a specific month

        Args:
            category: Category name
            month: Month in YYYY-MM format

        Returns:
            DataFrame with new releases
        """
        start_date = f"{month}-01"
        end_date = f"{month}-28"

        books_df = self.db.get_books_by_category(category)

        if books_df.empty:
            return pd.DataFrame()

        # Find books where first snapshot is in the target month
        books_df['snapshot_date'] = pd.to_datetime(books_df['snapshot_date'])
        books_df['month'] = books_df['snapshot_date'].dt.strftime('%Y-%m')

        new_releases = []

        for asin in books_df['asin'].unique():
            book_data = books_df[books_df['asin'] == asin].copy()
            first_appearance = book_data.sort_values('snapshot_date').iloc[0]

            if first_appearance['month'] == month:
                new_releases.append({
                    'title': first_appearance['title'],
                    'author': first_appearance['author'],
                    'first_rank': first_appearance['category_rank'],
                    'price': first_appearance['price'],
                    'rating': first_appearance['rating'],
                })

        return pd.DataFrame(new_releases)

    def generate_trend_report(self, start_month: str, end_month: str,
                            top_n: int = None) -> Dict:
        """
        Generate a comprehensive trend report

        Args:
            start_month: Start month in YYYY-MM format
            end_month: End month in YYYY-MM format
            top_n: Number of top categories to include

        Returns:
            Dictionary containing trend analysis
        """
        if top_n is None:
            top_n = self.config['top_n_niches']

        trending_categories = self.get_trending_categories(start_month, end_month)

        report = {
            'period': {
                'start': start_month,
                'end': end_month,
            },
            'trending_categories': trending_categories.head(top_n).to_dict('records'),
            'categories_analyzed': len(trending_categories),
            'generated_at': datetime.now().isoformat(),
        }

        return report

    def get_monthly_comparison(self, category: str, months: List[str]) -> pd.DataFrame:
        """
        Compare metrics across multiple months for a category

        Args:
            category: Category name
            months: List of months in YYYY-MM format

        Returns:
            DataFrame with month-by-month comparison
        """
        comparison_data = []

        for month in months:
            stats = self.db.get_category_stats(category, month)

            if stats and stats.get('book_count', 0) > 0:
                comparison_data.append({
                    'month': month,
                    **stats
                })

        return pd.DataFrame(comparison_data)

    def get_available_months(self) -> List[str]:
        """
        Get list of months with available data

        Returns:
            List of month strings in YYYY-MM format
        """
        monthly_data = self.db.get_monthly_snapshots()

        if monthly_data.empty:
            return []

        months = sorted(monthly_data['month'].unique(), reverse=True)
        return months


def main():
    """Example usage of the analyzer"""
    analyzer = TrendAnalyzer()

    # Get available months
    months = analyzer.get_available_months()
    print(f"Available months: {months}")

    if len(months) >= 2:
        # Analyze trends between first and last month
        start_month = months[-1]
        end_month = months[0]

        print(f"\nTrending categories from {start_month} to {end_month}:")
        trending = analyzer.get_trending_categories(start_month, end_month)
        print(trending.head(10))


if __name__ == '__main__':
    main()
