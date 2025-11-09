#!/bin/bash

# Amazon Book Trends Analyzer - Setup Script
# This script sets up the project and generates sample data

echo "============================================================"
echo "  Amazon Book Trends Analyzer - Setup"
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python found: $(python3 --version)"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi

echo "✓ Virtual environment created"
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed"
echo ""

# Create necessary directories
echo "📁 Creating data directories..."
mkdir -p data
mkdir -p data/exports

echo "✓ Directories created"
echo ""

# Generate sample data
echo "🔄 Generating 12 months of sample data..."
python main.py generate-sample-data --months 12

if [ $? -ne 0 ]; then
    echo "❌ Failed to generate sample data"
    exit 1
fi

echo ""
echo "============================================================"
echo "  ✅ Setup Complete!"
echo "============================================================"
echo ""
echo "To get started:"
echo ""
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. View available data:"
echo "     python main.py list-data"
echo ""
echo "  3. Analyze trending categories:"
echo "     python main.py trending --start-month 2024-01 --end-month 2024-12"
echo ""
echo "  4. Run example scripts:"
echo "     python examples.py"
echo ""
echo "  5. View all commands:"
echo "     python main.py --help"
echo ""
echo "Happy analyzing! 📚📊"
echo ""
