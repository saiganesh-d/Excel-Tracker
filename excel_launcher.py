"""
Excel Comparison Tool - Launcher for Standalone EXE
This script properly launches the Streamlit app when running as an EXE
"""

import sys
import os
from streamlit.web import cli as stcli

if __name__ == '__main__':
    # Get the directory where the EXE is running
    if getattr(sys, 'frozen', False):
        # Running as compiled EXE
        application_path = sys._MEIPASS
    else:
        # Running as script
        application_path = os.path.dirname(os.path.abspath(__file__))

    # Path to the main Streamlit app
    main_script = os.path.join(application_path, 'main.py')

    # Run Streamlit with the main script
    sys.argv = ["streamlit", "run", main_script, "--server.headless=true"]
    sys.exit(stcli.main())
