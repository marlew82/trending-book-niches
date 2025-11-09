"""
Example usage scripts for Amazon Book Trends Analyzer
"""
from analyzer import TrendAnalyzer
from scraper import AmazonScraper
from database import BookDatabase
import pandas as pd


def example_1_basic_trending_analysis():
    """Example 1: Basic trending analysis"""
    print("=" * 60)
    print("Example 1: Basic Trending Analysis")
    print("=" * 60)

    analyzer = TrendAnalyzer()

    # Get available months
    months = analyzer.get_available_months()
    if len(months) < 2:
        print("Not enough data. Generate sample data first:")
        print("python main.py generate-sample-data --months 12")
        return

    start_month = months[-1]  # Oldest month
    end_month = months[0]     # Newest month

    print(f"\nAnalyzing trends from {start_month} to {end_month}\n")

    # Get trending categories
    trending = analyzer.get_trending_categories(start_month, end_month)

    if not trending.empty:
        print("\nTop 10 Trending Categories:")
        print("-" * 60)
        for idx, row in trending.head(10).iterrows():
            print(f"{idx + 1}. {row['category']}")
            print(f"   Trend Score: {row['trend_score']:.2%}")
            print(f"   Books: {row['current_books']}")
            print(f"   Avg Price: ${row['avg_price']:.2f}")
            print()


def example_2_category_deep_dive():
    """Example 2: Deep dive into a specific category"""
    print("\n" + "=" * 60)
    print("Example 2: Category Deep Dive")
    print("=" * 60)

    analyzer = TrendAnalyzer()
    category = 'romance'

    # Get category timeline
    timeline = analyzer.get_category_timeline(category)

    if not timeline.empty:
        print(f"\n{category.upper()} Category Timeline:")
        print("-" * 60)

        for idx, row in timeline.iterrows():
            print(f"\nMonth: {row['month']}")
            print(f"  Books: {row['book_count']}")
            print(f"  Avg Rank: {row['avg_category_rank']:.1f}")
            print(f"  Avg Price: ${row['avg_price']:.2f}")
            print(f"  Total Reviews: {row['total_reviews']:,}")


def example_3_top_performers():
    """Example 3: Find top performing books"""
    print("\n" + "=" * 60)
    print("Example 3: Top Performing Books")
    print("=" * 60)

    analyzer = TrendAnalyzer()
    months = analyzer.get_available_months()

    if not months:
        print("No data available")
        return

    latest_month = months[0]
    category = 'self-help'

    print(f"\nTop 5 Books in {category.upper()} for {latest_month}:")
    print("-" * 60)

    top_books = analyzer.get_top_books_in_category(category, latest_month, limit=5)

    if not top_books.empty:
        for idx, book in top_books.iterrows():
            print(f"\n{idx + 1}. {book['title']}")
            print(f"   Author: {book['author']}")
            print(f"   Rank: #{book['category_rank']:.0f}")
            print(f"   Price: ${book['price']:.2f}")
            print(f"   Rating: {book['rating']:.1f} ({book['review_count']:,} reviews)")


def example_4_fastest_growing():
    """Example 4: Identify fastest growing books"""
    print("\n" + "=" * 60)
    print("Example 4: Fastest Growing Books")
    print("=" * 60)

    analyzer = TrendAnalyzer()
    months = analyzer.get_available_months()

    if len(months) < 2:
        print("Not enough data")
        return

    start_month = months[-1]
    end_month = months[0]
    category = 'science-fiction-fantasy'

    print(f"\nFastest Growing Books in {category.upper()}")
    print(f"Period: {start_month} to {end_month}")
    print("-" * 60)

    growing = analyzer.get_fastest_growing_books(category, start_month, end_month, limit=5)

    if not growing.empty:
        for idx, book in growing.iterrows():
            print(f"\n{idx + 1}. {book['title']}")
            print(f"   Author: {book['author']}")
            print(f"   Rank Improvement: {book['rank_improvement']:.1%}")
            print(f"   Start Rank: #{book['start_rank']}")
            print(f"   End Rank: #{book['end_rank']}")
            print(f"   Review Growth: +{book['review_growth']:,}")


def example_5_custom_analysis():
    """Example 5: Custom analysis with pandas"""
    print("\n" + "=" * 60)
    print("Example 5: Custom Analysis")
    print("=" * 60)

    analyzer = TrendAnalyzer()
    months = analyzer.get_available_months()

    if len(months) < 3:
        print("Not enough data")
        return

    # Get last 3 months
    recent_months = months[:3]

    print(f"\nComparing Categories Across Last 3 Months:")
    print(f"Months: {', '.join(recent_months)}")
    print("-" * 60)

    # Collect data for multiple categories
    categories_to_compare = ['romance', 'self-help', 'mystery-thriller-suspense']

    comparison = []

    for category in categories_to_compare:
        timeline = analyzer.get_category_timeline(
            category,
            start_month=recent_months[-1],
            end_month=recent_months[0]
        )

        if not timeline.empty:
            avg_books = timeline['book_count'].mean()
            avg_rank = timeline['avg_category_rank'].mean()
            avg_price = timeline['avg_price'].mean()

            comparison.append({
                'Category': category,
                'Avg Books': f"{avg_books:.0f}",
                'Avg Rank': f"{avg_rank:.1f}",
                'Avg Price': f"${avg_price:.2f}",
            })

    # Display comparison
    if comparison:
        df = pd.DataFrame(comparison)
        print(f"\n{df.to_string(index=False)}")


def example_6_export_data():
    """Example 6: Export data for external analysis"""
    print("\n" + "=" * 60)
    print("Example 6: Export Data")
    print("=" * 60)

    analyzer = TrendAnalyzer()
    months = analyzer.get_available_months()

    if len(months) < 2:
        print("Not enough data")
        return

    start_month = months[-1]
    end_month = months[0]

    # Get trending data
    trending = analyzer.get_trending_categories(start_month, end_month)

    if not trending.empty:
        # Export to CSV
        csv_file = 'data/exports/example_trending_export.csv'
        trending.to_csv(csv_file, index=False)
        print(f"\n✓ Exported trending data to {csv_file}")

        # Export to JSON
        json_file = 'data/exports/example_trending_export.json'
        trending.to_json(json_file, orient='records', indent=2)
        print(f"✓ Exported trending data to {json_file}")

        print(f"\nExported {len(trending)} categories")


def example_7_database_queries():
    """Example 7: Direct database queries"""
    print("\n" + "=" * 60)
    print("Example 7: Direct Database Queries")
    print("=" * 60)

    db = BookDatabase()

    # Get all categories
    categories = db.get_all_categories()
    print(f"\nTotal Categories: {len(categories)}")

    # Get date range
    min_date, max_date = db.get_date_range()
    print(f"Date Range: {min_date} to {max_date}")

    # Get specific category data
    if categories:
        category = categories[0]
        df = db.get_books_by_category(category)
        print(f"\nBooks in '{category}': {len(df['asin'].unique())}")
        print(f"Total snapshots: {len(df)}")


def run_all_examples():
    """Run all examples"""
    print("\n" + "=" * 70)
    print(" Amazon Book Trends Analyzer - Example Scripts ".center(70, "="))
    print("=" * 70)

    try:
        example_1_basic_trending_analysis()
        example_2_category_deep_dive()
        example_3_top_performers()
        example_4_fastest_growing()
        example_5_custom_analysis()
        example_6_export_data()
        example_7_database_queries()

        print("\n" + "=" * 70)
        print(" All Examples Completed! ".center(70, "="))
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("\nMake sure you have generated sample data first:")
        print("python main.py generate-sample-data --months 12")


if __name__ == '__main__':
    run_all_examples()
