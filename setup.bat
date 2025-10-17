@echo off
echo ========================================
echo Cost Calculation System - Setup Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo ✓ Python is installed
echo.

REM Check if PostgreSQL is running (basic check)
echo Checking PostgreSQL connection...
python -c "import psycopg2; psycopg2.connect('postgresql://postgres:123456789@localhost/cost_calculation_db')" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Cannot connect to PostgreSQL database
    echo Please ensure:
    echo 1. PostgreSQL is installed and running
    echo 2. Database 'cost_calculation_db' exists
    echo 3. User 'postgres' with password '123456789' exists
    echo.
    echo You can create the database with:
    echo createdb cost_calculation_db
    echo.
    pause
)

echo ✓ PostgreSQL connection successful
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv .venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo ✓ Virtual environment created
echo.

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing Python packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)

echo ✓ All packages installed successfully
echo.

REM Initialize database
echo Initializing database...
python init_db.py
if errorlevel 1 (
    echo ERROR: Failed to initialize database
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo To start the application:
echo 1. Activate virtual environment: .venv\Scripts\activate.bat
echo 2. Run application: python app.py
echo 3. Open browser: http://localhost:5000
echo.
echo Login credentials:
echo Username: admin
echo Password: admin123
echo.
echo Press any key to exit...
pause >nul
