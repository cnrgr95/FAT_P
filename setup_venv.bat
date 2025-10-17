@echo off
echo Creating virtual environment for Cost Calculation System...
echo.

REM Create virtual environment
python -m venv .venv

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install requirements
pip install -r requirements.txt

echo.
echo Virtual environment created successfully!
echo.
echo To activate the virtual environment, run:
echo .venv\Scripts\activate.bat
echo.
echo To run the application, use:
echo python app.py
echo.
pause
