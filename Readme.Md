# Excel Change Visualizer 📊

A powerful tool to visualize and track changes between Excel files. Perfect for tracking client modifications to templates across multiple iterations.

## Features ✨

- **Multi-Sheet Support**: Compare entire workbooks with multiple sheets
- **Visual Change Tracking**: Color-coded visualization of additions, modifications, and deletions
- **Smart Grouping**: Changes organized by sheet and row for easy review
- **Multiple Export Options**:
  - Highlighted Excel file with all changes marked
  - JSON report for programmatic processing
  - HTML report for sharing with stakeholders
- **User-Friendly Interface**: Clean web UI built with Streamlit
- **Detailed Summary**: Quick overview of total changes across all sheets

## Installation 🚀

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Quick Setup

1. **Clone or download the files**:
   - `excel_change_visualizer.py` (main application)
   - `requirements.txt` (dependencies)
   - `run.sh` (for Mac/Linux) or `run.bat` (for Windows)

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   
   **Windows:**
   ```cmd
   run.bat
   ```
   
   **Mac/Linux:**
   ```bash
   chmod +x run.sh
   ./run.sh
   ```
   
   **Or directly with Python:**
   ```bash
   streamlit run excel_change_visualizer.py
   ```

4. **Access the application**:
   - The app will automatically open in your browser
   - If not, navigate to: `http://localhost:8501`

## Usage Guide 📖

### Step 1: Upload Files
1. Click on the sidebar (left side of the screen)
2. Upload your **Original Template** (the file you sent to the client)
3. Upload the **Modified Version** (the file returned by the client)

### Step 2: Compare Files
- Click the **"🔍 Compare Files"** button
- The tool will analyze all sheets and identify changes

### Step 3: Review Changes
- **Summary Dashboard**: See total changes at a glance
- **Sheet Tabs**: Navigate between modified sheets
- **Change Details**: View specific cells that were:
  - ✅ Added (Green)
  - 📝 Modified (Yellow)  
  - ❌ Removed (Red)

### Step 4: Export Results
Choose from three export options:

1. **📊 Diff Excel**: 
   - Creates a new Excel file with all changes highlighted
   - Includes comments showing original values
   - Adds a summary sheet with statistics

2. **📄 JSON Report**:
   - Machine-readable format
   - Perfect for integration with other tools
   - Contains all change details and metadata

3. **🌐 HTML Report**:
   - Shareable web-based report
   - Can be opened in any browser
   - Includes all changes with color coding

## Understanding the Output 🎨

### Color Coding
- **Green Background**: New content added by client
- **Yellow Background**: Existing content modified
- **Red Background**: Content removed by client

### Change Notation
- **Cell References**: Shows exact location (e.g., A1, B5)
- **Old Values**: Shown with strikethrough
- **New Values**: Shown in bold

### Summary Metrics
- **Total Changes**: Sum of all modifications
- **Cells Added/Removed/Modified**: Breakdown by change type
- **Sheets Modified**: List of sheets with changes

## Advanced Features 🔧

### Handling Large Files
- The tool efficiently processes large Excel files
- Progress indicators show processing status
- Memory-optimized for files with thousands of cells

### Multiple Iterations
- Save comparison reports for each iteration
- Track changes over time
- Build a history of modifications

### Comments and Formulas
- Detects changes in cell values
- Preserves formatting in diff Excel
- Adds helpful comments explaining changes

## Troubleshooting 🔨

### Common Issues

**Issue: "ModuleNotFoundError"**
- Solution: Install missing dependencies with `pip install -r requirements.txt`

**Issue: Excel file not loading**
- Ensure file is not open in Excel
- Check file format is .xlsx or .xls
- Verify file is not corrupted

**Issue: Browser doesn't open automatically**
- Manually navigate to http://localhost:8501
- Check if port 8501 is blocked by firewall

**Issue: Memory error with large files**
- Close other applications
- Process sheets individually if needed
- Consider breaking large files into smaller chunks

## Tips for Best Results 💡

1. **Consistent Templates**: Use the same structure across iterations
2. **Clear Naming**: Use descriptive sheet names
3. **Regular Comparisons**: Compare after each client iteration
4. **Archive Reports**: Save comparison reports for documentation
5. **Review Summary First**: Start with the overview before diving into details

## Technical Details 🛠️

### Technologies Used
- **Python**: Core programming language
- **Streamlit**: Web UI framework
- **openpyxl**: Excel file processing
- **pandas**: Data manipulation
- **numpy**: Numerical operations

### File Structure
```
excel-change-visualizer/
├── excel_change_visualizer.py  # Main application
├── requirements.txt            # Python dependencies
├── run.sh                     # Mac/Linux launcher
├── run.bat                    # Windows launcher
└── README.md                  # This file
```

## Support 📧

For issues or questions:
1. Check the troubleshooting section above
2. Ensure all dependencies are correctly installed
3. Verify Excel files are in supported formats (.xlsx, .xls)

## Future Enhancements 🚀

Potential improvements for future versions:
- Support for Google Sheets
- Real-time collaboration features
- Change history timeline
- Automated email notifications
- Custom change detection rules
- Integration with version control systems

---

**Note**: This tool is designed to save hours of manual comparison work. It's particularly useful for:
- Contract negotiations
- Budget revisions
- Data collection forms
- Collaborative spreadsheet work
- Template standardization

Happy tracking! 🎉
