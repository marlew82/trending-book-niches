@echo off
REM Amazon Book Trends Analyzer - Setup Script for Windows

echo ============================================================
echo   Amazon Book Trends Analyzer - Setup
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo √ Python found
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

if errorlevel 1 (
    echo X Failed to create virtual environment
    pause
    exit /b 1
)

echo √ Virtual environment created
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo X Failed to install dependencies
    pause
    exit /b 1
)

echo √ Dependencies installed
echo.

REM Create necessary directories
echo Creating data directories...
if not exist data mkdir data
if not exist data\exports mkdir data\exports

echo √ Directories created
echo.

REM Generate sample data
echo Generating 12 months of sample data...
python main.py generate-sample-data --months 12

if errorlevel 1 (
    echo X Failed to generate sample data
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   √ Setup Complete!
echo ============================================================
echo.
echo To get started:
echo.
echo   1. Activate the virtual environment:
echo      venv\Scripts\activate.bat
echo.
echo   2. View available data:
echo      python main.py list-data
echo.
echo   3. Analyze trending categories:
echo      python main.py trending --start-month 2024-01 --end-month 2024-12
echo.
echo   4. Run example scripts:
echo      python examples.py
echo.
echo   5. View all commands:
echo      python main.py --help
echo.
echo Happy analyzing! 📚📊
echo.
pause
