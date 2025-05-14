# Enhanced Flask Application Testing PowerShell Script
Write-Host "=================================================================" -ForegroundColor Blue
Write-Host "        FLASK APPLICATION TESTING SCRIPT" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Blue
Write-Host ""

# Get current directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Check environment
Write-Host "Checking environment..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
    
    # Check required packages
    python -c "import flask; import selenium; print('Required packages found')"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Required packages found" -ForegroundColor Green
    } else {
        Write-Host "Required packages missing! Run: pip install -r requirements.txt" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Python not found! Please make sure Python is installed and in your PATH" -ForegroundColor Red
    exit 1
}

# Display menu
Write-Host ""
Write-Host "Available test options:" -ForegroundColor Yellow
Write-Host "1. Run basic environment check" -ForegroundColor Cyan
Write-Host "2. Run basic Selenium test (includes Flask server)" -ForegroundColor Cyan
Write-Host "3. Run all unit tests" -ForegroundColor Cyan
Write-Host "4. Run Selenium tests with pytest" -ForegroundColor Cyan
Write-Host "5. Run comprehensive Selenium test suite" -ForegroundColor Cyan
Write-Host ""

$choice = Read-Host "Enter your choice (1-5)"

$flaskProcess = $null

try {
    switch ($choice) {
        "1" {
            Write-Host "Running basic environment check..." -ForegroundColor Yellow
            python test\basic_env_test.py
        }
        "2" {
            Write-Host "Running basic Selenium test..." -ForegroundColor Yellow
            python test\basic_selenium.py
        }
        "3" {
            Write-Host "Running all unit tests..." -ForegroundColor Yellow
            python -m pytest test\test_forms.py test\test_models.py -v
        }
        "4" {
            Write-Host "Running Selenium tests with pytest..." -ForegroundColor Yellow
            Write-Host "Starting Flask server first..." -ForegroundColor Yellow
            $flaskProcess = Start-Process -FilePath "python" -ArgumentList "run_for_testing.py" -PassThru -WindowStyle Normal
            Write-Host "Flask server starting... please wait" -ForegroundColor Yellow
            Start-Sleep -Seconds 5
            
            python -m pytest test\test_selenium_simple.py -v
        }
        "5" {
            Write-Host "Running comprehensive Selenium test suite..." -ForegroundColor Yellow
            python test\comprehensive_test.py
        }
        default {
            Write-Host "Invalid choice!" -ForegroundColor Red
        }
    }
}
finally {
    # Clean up: Stop Flask server if we started it
    if ($null -ne $flaskProcess) {
        Write-Host ""
        Write-Host "Stopping Flask server..." -ForegroundColor Yellow
        Stop-Process -Id $flaskProcess.Id -Force -ErrorAction SilentlyContinue
    }
}

Write-Host ""
Write-Host "Tests completed!" -ForegroundColor Green
Read-Host "Press Enter to exit"
