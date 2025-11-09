#!/usr/bin/env python3
"""
Terminal-based dashboard viewer for Amazon Book Trends Analyzer
Use this when web access is restricted
"""
import webbrowser
import os
from analyzer import TrendAnalyzer
from database import BookDatabase
from tabulate import tabulate
from colorama import init, Fore, Style

init(autoreset=True)

def print_header(text):
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{'=' * 70}")
    print(f"{text.center(70)}")
    print(f"{'=' * 70}{Style.RESET_ALL}\n")

def main():
    analyzer = TrendAnalyzer()
    db = BookDatabase()

    # Get stats
    print_header("📊 AMAZON BOOK TRENDS DASHBOARD")

    categories = db.get_all_categories()
    min_date, max_date = db.get_date_range()
    months = analyzer.get_available_months()
    monthly_data = db.get_monthly_snapshots()
    total_books = int(monthly_data['book_count'].sum()) if not monthly_data.empty else 0

    stats = [
        ["📂 Categories Tracked", len(categories)],
        ["📖 Books Analyzed", total_books],
        ["📅 Months of Data", len(months)],
        ["📆 Date Range", f"{min_date} to {max_date}"],
    ]

    print(tabulate(stats, tablefmt="grid"))

    # Show trending
    if len(months) >= 2:
        start_month = months[-1]
        end_month = months[0]

        print_header(f"📈 TRENDING CATEGORIES ({start_month} to {end_month})")

        trending = analyzer.get_trending_categories(start_month, end_month, min_books=1)

        if not trending.empty:
            display_data = trending.head(10).copy()
            display_data['trend_score'] = (display_data['trend_score'] * 100).round(2)
            display_data['rank_improvement'] = (display_data['rank_improvement'] * 100).round(2)

            table_data = []
            for idx, row in display_data.iterrows():
                trend_indicator = "📈" if row['trend_score'] > 5 else "→"
                table_data.append([
                    f"{trend_indicator} {row['category'].replace('-', ' ').title()}",
                    f"{row['trend_score']:.1f}%",
                    f"{row['rank_improvement']:.1f}%",
                    int(row['current_books']),
                    f"${row['avg_price']:.2f}",
                    f"⭐ {row['avg_rating']:.1f}",
                ])

            headers = ["Category", "Trend Score", "Rank Δ", "Books", "Avg Price", "Rating"]
            print(tabulate(table_data, headers=headers, tablefmt="grid"))

    # Show categories
    print_header("📂 AVAILABLE CATEGORIES")
    print("Click on category names to view details:\n")

    for i, cat in enumerate(categories, 1):
        print(f"  {i}. {Fore.BLUE}{cat.replace('-', ' ').title()}{Style.RESET_ALL}")

    print(f"\n{Fore.GREEN}✓ Web interface running at: http://localhost:5000{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}  (If you have web access, open this URL in your browser){Style.RESET_ALL}\n")

    # Try to open browser
    choice = input("Would you like to try opening in browser? (y/n): ").lower()
    if choice == 'y':
        try:
            webbrowser.open('http://localhost:5000')
            print(f"\n{Fore.GREEN}✓ Browser opened!{Style.RESET_ALL}")
        except:
            print(f"\n{Fore.RED}✗ Could not open browser automatically{Style.RESET_ALL}")
            print(f"  Please manually open: http://localhost:5000")

if __name__ == '__main__':
    main()
