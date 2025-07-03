@echo off
echo Setting up BLE Beacon API development environment...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Copy environment file
if not exist .env (
    echo Creating .env file...
    copy .env.example .env
    echo Please edit .env file with your database configuration
)

echo.
echo Setup complete!
echo To activate the virtual environment, run: venv\Scripts\activate
echo To start the development server, run: python run_dev.py
echo.
echo Don't forget to:
echo 1. Set up PostgreSQL database
echo 2. Update .env file with your database URL
echo 3. Run database migrations: alembic upgrade head
