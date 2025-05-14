@echo off
echo ===================================================
echo      FLASK APPLICATION TESTING SCRIPT
echo ===================================================
echo.

cd /d "%~dp0"

echo Setting up Python environment...
call python -c "import sys; print(f'Python version: {sys.version}')" || goto :error

echo.
echo Step 1: Checking Flask application imports...
call python -c "import flask; print(f'Flask version: {flask.__version__}')" || goto :error
call python -c "import selenium; print(f'Selenium version: {selenium.__version__}')" || goto :error

echo.
echo Step 2: Checking database access...
call python -c "from app import create_app, db; app = create_app('testing'); ctx = app.app_context(); ctx.push(); from app.models import User; print(f'Database URI: {db.engine.url}'); print('Database access successful'); ctx.pop()" || goto :error

echo.
echo Step 3: Running basic unit tests...
call python -m unittest test/basic_env_test.py || goto :error

echo.
echo Step 4: Testing Flask forms...
call python -m unittest discover -s test -p "test_forms.py" || goto :error

echo.
echo All tests completed successfully!
echo.
echo ===================================================
pause
exit /b 0

:error
echo.
echo ERROR: Test failed with error code %errorlevel%
echo.
echo ===================================================
pause
exit /b %errorlevel%
