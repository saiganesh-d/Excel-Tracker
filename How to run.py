#!/bin/bash
# run.sh - For Mac/Linux

echo "Excel Change Visualizer"
echo "======================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the application
echo ""
echo "Starting Excel Change Visualizer..."
echo "Opening in browser at http://localhost:8501"
echo ""
streamlit run excel_change_visualizer.py

# --- Windows Batch Script (save as run.bat) ---
: '
@echo off
echo Excel Change Visualizer
echo ======================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Run the application
echo.
echo Starting Excel Change Visualizer...
echo Opening in browser at http://localhost:8501
echo.
streamlit run excel_change_visualizer.py
'
