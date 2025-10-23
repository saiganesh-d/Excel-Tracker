"""
Launcher script for creating standalone executable
This is the entry point for PyInstaller
"""

import sys
import os
from pathlib import Path

# Add the script directory to Python path
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    application_path = sys._MEIPASS
else:
    # Running as script
    application_path = os.path.dirname(os.path.abspath(__file__))

# Add to path
sys.path.insert(0, application_path)

def main():
    """Main entry point for the application"""
    # Import streamlit CLI
    from streamlit.web import cli as stcli

    # Get the path to app.py
    app_path = os.path.join(application_path, "app.py")

    # Set up arguments for Streamlit
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--server.headless=true",
        "--server.port=8501",
        "--browser.gatherUsageStats=false",
        "--global.developmentMode=false"
    ]

    # Run Streamlit
    sys.exit(stcli.main())

if __name__ == "__main__":
    main()
