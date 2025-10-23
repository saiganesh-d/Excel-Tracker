@echo off
REM Quick test script for the built executable

echo ========================================
echo Testing Built Executable
echo ========================================
echo.

REM Check if build exists
if not exist "dist\DocumentComparison\DocumentComparison.exe" (
    echo ERROR: Executable not found!
    echo.
    echo Please run build_exe.bat first.
    echo.
    pause
    exit /b 1
)

echo Found: dist\DocumentComparison\DocumentComparison.exe
echo.

REM Check file size
for %%I in ("dist\DocumentComparison\DocumentComparison.exe") do set size=%%~zI
echo File size: %size% bytes
echo.

REM Count files in _internal folder
if exist "dist\DocumentComparison\_internal\" (
    dir /b /s "dist\DocumentComparison\_internal\" | find /c /v "" > temp_count.txt
    set /p file_count=<temp_count.txt
    del temp_count.txt
    echo Support files: %file_count% files in _internal folder
) else (
    echo WARNING: _internal folder not found!
)
echo.

echo ========================================
echo Starting executable for testing...
echo ========================================
echo.
echo The application will start in a moment.
echo Check that:
echo   1. Console window opens (you'll see it)
echo   2. Browser opens automatically
echo   3. Application loads without errors
echo   4. You can upload and compare files
echo.
echo Press Ctrl+C in the console window to stop.
echo.
pause

REM Run the executable
cd dist\DocumentComparison
DocumentComparison.exe

echo.
echo ========================================
echo Test complete
echo ========================================
pause
