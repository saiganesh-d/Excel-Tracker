@echo off
REM Debug launcher - keeps window open to see errors

echo ========================================
echo Document Comparison Tool - DEBUG MODE
echo ========================================
echo.

REM Check if dist folder exists
if not exist "dist\DocumentComparison" (
    echo ERROR: dist\DocumentComparison folder not found!
    echo Please run build_with_venv.bat first to create the EXE.
    echo.
    pause
    exit /b 1
)

REM Navigate to dist folder
cd dist\DocumentComparison

echo Current directory: %CD%
echo.
echo Contents:
dir /b
echo.
echo ========================================
echo Starting application...
echo ========================================
echo.

REM Run the EXE and keep window open
DocumentComparison.exe

echo.
echo ========================================
echo Application closed
echo ========================================
echo.
echo If you saw an error above, please note it down.
echo.

pause
