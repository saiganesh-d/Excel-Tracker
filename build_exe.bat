@echo off
REM Build script for creating Windows executable
REM This creates a standalone EXE that users can run without Python
REM Works with both global Python and virtual environments

echo ========================================
echo Document Comparison Suite - EXE Builder
echo ========================================
echo.

REM Check if we're in a virtual environment
if defined VIRTUAL_ENV (
    echo Using virtual environment: %VIRTUAL_ENV%
    echo.
) else (
    echo WARNING: Not in a virtual environment
    echo Looking for venv in common locations...
    echo.

    REM Check for common venv locations
    if exist "venv\Scripts\activate.bat" (
        echo Found venv folder. Activating...
        call venv\Scripts\activate.bat
    ) else if exist ".venv\Scripts\activate.bat" (
        echo Found .venv folder. Activating...
        call .venv\Scripts\activate.bat
    ) else if exist "env\Scripts\activate.bat" (
        echo Found env folder. Activating...
        call env\Scripts\activate.bat
    ) else (
        echo No virtual environment found.
        echo Using system Python (if available)
        echo.
    )
)

REM Verify Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo.
    echo Please either:
    echo 1. Activate your virtual environment first, then run this script
    echo 2. Install Python globally
    echo.
    echo Example: venv\Scripts\activate.bat
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller>=6.0.0
    if errorlevel 1 (
        echo Failed to install PyInstaller
        pause
        exit /b 1
    )
)

echo Step 1: Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo    Done.
echo.

echo Step 2: Building executable with PyInstaller...
echo    This may take 5-10 minutes...
echo.
pyinstaller document_comparison.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo ========================================
    echo BUILD FAILED
    echo ========================================
    echo Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo BUILD SUCCESSFUL!
echo ========================================
echo.
echo Your executable is ready at:
echo    dist\DocumentComparison\DocumentComparison.exe
echo.
echo The complete folder to distribute:
echo    dist\DocumentComparison\
echo.
echo Next steps:
echo 1. Test the executable by running it
echo 2. Zip the entire 'DocumentComparison' folder
echo 3. Share the zip file with users
echo.
echo Users should:
echo 1. Extract the zip file
echo 2. Double-click DocumentComparison.exe
echo 3. Browser will open automatically
echo.
pause
