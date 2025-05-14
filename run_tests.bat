@echo off
echo ===================================================
echo      FLASK APPLICATION TESTING SCRIPT
echo ===================================================
echo.

cd /d "%~dp0"

echo Setting up environment...
echo Checking Python...
python --version || echo Python not found! Please make sure Python is installed and in your PATH && pause && exit /b 1

echo.
echo Checking for required packages...
python -c "import flask; import selenium; print('Required packages found')" || echo Required packages missing! Run: pip install -r requirements.txt && pause && exit /b 1

echo.
echo Available test options:
echo 1. Run basic environment check
echo 2. Run basic Selenium test (includes Flask server)
echo 3. Run all unit tests
echo 4. Run Selenium tests with pytest
echo 5. Run comprehensive Selenium test suite
echo.

set /p choice="Enter your choice (1-5): "

echo.
if "%choice%"=="1" (
    echo Running basic environment check...
    python test\basic_env_test.py
) else if "%choice%"=="2" (
    echo Running basic Selenium test...
    python test\basic_selenium.py
) else if "%choice%"=="3" (
    echo Running all unit tests...
    python -m pytest test\test_forms.py test\test_models.py -v
) else if "%choice%"=="4" (
    echo Running Selenium tests with pytest...
    echo Note: Make sure Flask is running in another terminal with: python run_for_testing.py
    timeout /t 5
    python -m pytest test\test_selenium_simple.py -v
) else if "%choice%"=="5" (
    echo Running comprehensive Selenium test suite...
    python test\comprehensive_test.py
) else (
    echo Invalid choice!
)

echo.
echo Tests completed!
pause
