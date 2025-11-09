"""
Database module for storing and retrieving book data
"""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import pandas as pd
from config import DB_PATH


class BookDatabase:
    """Manages the SQLite database for book data"""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.conn = None
        self.initialize_database()

    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def initialize_database(self):
        """Create database tables if they don't exist"""
        conn = self.connect()
        cursor = conn.cursor()

        # Books table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asin TEXT NOT NULL,
                title TEXT NOT NULL,
                author TEXT,
                category TEXT NOT NULL,
                subcategory TEXT,
                publication_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(asin, category)
            )
        """)

        # Book snapshots table (for tracking changes over time)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS book_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                snapshot_date DATE NOT NULL,
                sales_rank INTEGER,
                category_rank INTEGER,
                price REAL,
                review_count INTEGER,
                rating REAL,
                FOREIGN KEY (book_id) REFERENCES books(id),
                UNIQUE(book_id, snapshot_date)
            )
        """)

        # Categories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                parent_category TEXT,
                description TEXT
            )
        """)

        # Create indexes for better query performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_books_category
            ON books(category)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_snapshots_date
            ON book_snapshots(snapshot_date)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_snapshots_book_date
            ON book_snapshots(book_id, snapshot_date)
        """)

        conn.commit()
        self.close()

    def insert_book(self, asin: str, title: str, author: str, category: str,
                    subcategory: Optional[str] = None, publication_date: Optional[str] = None) -> int:
        """Insert a new book or return existing book ID"""
        conn = self.connect()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO books (asin, title, author, category, subcategory, publication_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (asin, title, author, category, subcategory, publication_date))
            book_id = cursor.lastrowid
            conn.commit()
        except sqlite3.IntegrityError:
            # Book already exists, get its ID
            cursor.execute("""
                SELECT id FROM books
                WHERE asin = ? AND category = ?
            """, (asin, category))
            book_id = cursor.fetchone()[0]

        self.close()
        return book_id

    def insert_snapshot(self, book_id: int, snapshot_date: str, sales_rank: Optional[int] = None,
                       category_rank: Optional[int] = None, price: Optional[float] = None,
                       review_count: Optional[int] = None, rating: Optional[float] = None):
        """Insert a snapshot of book metrics"""
        conn = self.connect()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO book_snapshots
                (book_id, snapshot_date, sales_rank, category_rank, price, review_count, rating)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (book_id, snapshot_date, sales_rank, category_rank, price, review_count, rating))
            conn.commit()
        except sqlite3.IntegrityError:
            # Update existing snapshot
            cursor.execute("""
                UPDATE book_snapshots
                SET sales_rank = ?, category_rank = ?, price = ?, review_count = ?, rating = ?
                WHERE book_id = ? AND snapshot_date = ?
            """, (sales_rank, category_rank, price, review_count, rating, book_id, snapshot_date))
            conn.commit()

        self.close()

    def get_books_by_category(self, category: str, start_date: Optional[str] = None,
                             end_date: Optional[str] = None) -> pd.DataFrame:
        """Get all books in a category with their snapshots"""
        conn = self.connect()

        query = """
            SELECT
                b.asin,
                b.title,
                b.author,
                b.category,
                b.subcategory,
                b.publication_date,
                bs.snapshot_date,
                bs.sales_rank,
                bs.category_rank,
                bs.price,
                bs.review_count,
                bs.rating
            FROM books b
            LEFT JOIN book_snapshots bs ON b.id = bs.book_id
            WHERE b.category = ?
        """

        params = [category]

        if start_date:
            query += " AND bs.snapshot_date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND bs.snapshot_date <= ?"
            params.append(end_date)

        query += " ORDER BY bs.snapshot_date DESC, bs.category_rank ASC"

        df = pd.read_sql_query(query, conn, params=params)
        self.close()
        return df

    def get_all_categories(self) -> List[str]:
        """Get list of all categories in database"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT DISTINCT category FROM books ORDER BY category")
        categories = [row[0] for row in cursor.fetchall()]

        self.close()
        return categories

    def get_date_range(self) -> Tuple[Optional[str], Optional[str]]:
        """Get the min and max snapshot dates in the database"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT MIN(snapshot_date), MAX(snapshot_date)
            FROM book_snapshots
        """)
        result = cursor.fetchone()

        self.close()
        return result if result else (None, None)

    def get_category_stats(self, category: str, month: str) -> Dict:
        """Get statistics for a category in a specific month"""
        conn = self.connect()

        query = """
            SELECT
                COUNT(DISTINCT b.id) as book_count,
                AVG(bs.sales_rank) as avg_sales_rank,
                AVG(bs.price) as avg_price,
                AVG(bs.review_count) as avg_reviews,
                AVG(bs.rating) as avg_rating
            FROM books b
            JOIN book_snapshots bs ON b.id = bs.book_id
            WHERE b.category = ?
            AND strftime('%Y-%m', bs.snapshot_date) = ?
        """

        df = pd.read_sql_query(query, conn, params=[category, month])
        self.close()

        return df.to_dict('records')[0] if not df.empty else {}

    def get_monthly_snapshots(self, start_date: Optional[str] = None,
                             end_date: Optional[str] = None) -> pd.DataFrame:
        """Get all snapshots grouped by month"""
        conn = self.connect()

        query = """
            SELECT
                b.category,
                b.subcategory,
                strftime('%Y-%m', bs.snapshot_date) as month,
                COUNT(DISTINCT b.id) as book_count,
                AVG(bs.sales_rank) as avg_sales_rank,
                AVG(bs.category_rank) as avg_category_rank,
                AVG(bs.price) as avg_price,
                SUM(bs.review_count) as total_reviews,
                AVG(bs.rating) as avg_rating
            FROM books b
            JOIN book_snapshots bs ON b.id = bs.book_id
            WHERE 1=1
        """

        params = []

        if start_date:
            query += " AND bs.snapshot_date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND bs.snapshot_date <= ?"
            params.append(end_date)

        query += " GROUP BY b.category, b.subcategory, month ORDER BY month DESC"

        df = pd.read_sql_query(query, conn, params=params)
        self.close()
        return df

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
