# Quick Start Guide

Get started with Amazon Book Trends Analyzer in 5 minutes!

## Option 1: Automated Setup (Recommended)

### Linux/Mac

```bash
cd trending-book-niches
chmod +x setup.sh
./setup.sh
```

### Windows

```cmd
cd trending-book-niches
setup.bat
```

The setup script will:
- Create a virtual environment
- Install all dependencies
- Generate 12 months of sample data
- Verify the installation

## Option 2: Manual Setup

### Step 1: Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Generate Sample Data

```bash
python main.py generate-sample-data --months 12
```

### Step 3: Verify Installation

```bash
python main.py list-data
```

## Your First Analysis

### 1. View Trending Categories

```bash
python main.py trending --start-month 2024-01 --end-month 2024-12
```

### 2. Analyze a Specific Category

```bash
python main.py category --category romance
```

### 3. See Top Books

```bash
python main.py top-books --category self-help --month 2024-12
```

### 4. Find Fastest Growing Books

```bash
python main.py growing --category romance --start-month 2024-01 --end-month 2024-12
```

### 5. Export Results

```bash
python main.py trending --start-month 2024-01 --end-month 2024-12 --export csv
```

## Run Examples

```bash
python examples.py
```

## Common Commands

| Task | Command |
|------|---------|
| List available data | `python main.py list-data` |
| View trending niches | `python main.py trending --start-month YYYY-MM --end-month YYYY-MM` |
| Analyze category | `python main.py category --category CATEGORY_NAME` |
| Top books | `python main.py top-books --category CATEGORY --month YYYY-MM` |
| Growing books | `python main.py growing --category CATEGORY --start-month YYYY-MM --end-month YYYY-MM` |
| Export to CSV | Add `--export csv` to any command |
| Export to JSON | Add `--export json` to any command |

## Available Categories

- mystery-thriller-suspense
- science-fiction-fantasy
- romance
- self-help
- business-money

## Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Explore [examples.py](examples.py) for Python usage examples
3. Customize [config.py](config.py) for your needs
4. Try live scraping (use responsibly!): `python main.py scrape --help`

## Getting Help

```bash
# General help
python main.py --help

# Command-specific help
python main.py trending --help
python main.py category --help
python main.py top-books --help
```

## Troubleshooting

**No data available?**
```bash
python main.py generate-sample-data --months 12
```

**Import errors?**
```bash
pip install -r requirements.txt
```

**Need to reset?**
```bash
rm -rf data/books.db
python main.py generate-sample-data --months 12
```

---

Happy analyzing! 📚📊
