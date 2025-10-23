@echo off
REM Build script for creating Windows executable
REM This creates a standalone EXE that users can run without Python

echo ========================================
echo Document Comparison Suite - EXE Builder
echo ========================================
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
