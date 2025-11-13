@echo off
REM Build script for Excel Comparison EXE
REM This creates a standalone executable

echo ========================================
echo Excel Comparison EXE Builder
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo [1/6] Creating virtual environment...
    python -m venv venv
    echo Done!
    echo.
) else (
    echo [1/6] Virtual environment exists
    echo.
)

REM Activate virtual environment
echo [2/6] Activating virtual environment...
call venv\Scripts\activate.bat
echo Done!
echo.

REM Install minimal dependencies
echo [3/6] Installing Excel-only dependencies...
echo This will take 2-3 minutes...
pip install --upgrade pip
pip install -r requirements_excel_only.txt
pip install pyinstaller
echo Done!
echo.

REM Clean previous builds
echo [4/6] Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "ExcelCompare.exe" del ExcelCompare.exe
echo Done!
echo.

REM Build EXE
echo [5/6] Building EXE with PyInstaller...
echo This will take 5-10 minutes...
pyinstaller --clean --noconfirm excel_compare.spec
echo Done!
echo.

REM Move EXE to root
echo [6/6] Finalizing...
if exist "dist\ExcelCompare.exe" (
    move dist\ExcelCompare.exe ExcelCompare.exe
    echo.
    echo ========================================
    echo SUCCESS! EXE created successfully!
    echo ========================================
    echo.
    echo File: ExcelCompare.exe
    echo Size:
    dir ExcelCompare.exe | findstr ExcelCompare
    echo.
    echo You can now send ExcelCompare.exe to anyone!
    echo They can run it without Python installed.
    echo.
) else (
    echo.
    echo ========================================
    echo ERROR: EXE creation failed!
    echo ========================================
    echo.
    echo Check the output above for errors.
    echo Common issues:
    echo - Missing dependencies
    echo - Antivirus blocking PyInstaller
    echo - Insufficient disk space
    echo.
)

echo Press any key to exit...
pause >nul
