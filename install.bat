@echo off
REM Installation script for Bitcoin Trading Framework (Windows)

echo ======================================================
echo Installing Bitcoin Trading Framework Dependencies
echo ======================================================
echo.

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not installed. Please install Python and pip first.
    exit /b 1
)

echo Installing required packages...
pip install -r requirements.txt

echo.
echo ======================================================
echo Installation Complete!
echo ======================================================
echo.
echo To verify the installation, run:
echo   set PYTHONPATH=.
echo   python examples\backtest_sma_example.py
echo.
echo For more information, see:
echo   - README.md for detailed documentation
echo   - QUICKSTART.md for a 5-minute tutorial
echo.
pause
