@echo off
REM Helper script to build EXE when using virtual environment
REM This script automatically activates your venv and builds

echo ========================================
echo Build with Virtual Environment Helper
echo ========================================
echo.

REM Find and activate virtual environment
if exist "venv\Scripts\activate.bat" (
    echo Activating venv...
    call venv\Scripts\activate.bat
    goto :build
)

if exist ".venv\Scripts\activate.bat" (
    echo Activating .venv...
    call .venv\Scripts\activate.bat
    goto :build
)

if exist "env\Scripts\activate.bat" (
    echo Activating env...
    call env\Scripts\activate.bat
    goto :build
)

REM If no venv found, ask user
echo ERROR: No virtual environment found!
echo.
echo Please specify your virtual environment folder name
echo Common names: venv, .venv, env
echo.
set /p VENV_NAME="Enter venv folder name (or press Enter to skip): "

if "%VENV_NAME%"=="" (
    echo Proceeding without activating venv...
    goto :build
)

if exist "%VENV_NAME%\Scripts\activate.bat" (
    echo Activating %VENV_NAME%...
    call %VENV_NAME%\Scripts\activate.bat
    goto :build
) else (
    echo ERROR: Could not find %VENV_NAME%\Scripts\activate.bat
    echo.
    echo Please activate your virtual environment manually and run build_exe.bat
    echo Example: venv\Scripts\activate.bat
    pause
    exit /b 1
)

:build
echo.
echo Virtual environment activated!
echo.
echo Running build script...
echo.

REM Run the actual build script
call build_exe.bat

REM Keep window open
echo.
echo Done!
pause
