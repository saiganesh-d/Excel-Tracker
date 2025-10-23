================================================================================
                     DOCUMENT COMPARISON SUITE v1.0
================================================================================

WHAT IS THIS?
-------------
Professional tool for comparing Excel spreadsheets and PDF documents.
Perfect for tracking supplier modifications to templates and requirements.


SYSTEM REQUIREMENTS
-------------------
- Windows 10 or later
- 2 GB RAM minimum
- 500 MB free disk space
- Modern web browser (Chrome, Firefox, Edge)


HOW TO RUN
----------
1. Extract the zip file to a location on your computer
   Example: C:\Tools\DocumentComparison

2. Open the extracted folder

3. Double-click "DocumentComparison.exe"

4. Wait 10-20 seconds for the application to start

5. Your web browser will open automatically to http://localhost:8501

6. Choose your comparison tool:
   - Excel Diff Visualizer (for spreadsheets)
   - PDF Structure Comparison (for documents)


FIRST TIME USE
--------------
- Windows may show a "SmartScreen" warning
- Click "More info" → "Run anyway"
- This is normal for applications without code signing certificates


USING EXCEL COMPARISON
----------------------
1. Select "Excel Diff Visualizer"
2. Upload your original template (.xlsx)
3. Upload the modified version (.xlsx)
4. Click "Compare Files"
5. Review changes with synchronized scrolling
6. Export results if needed


USING PDF COMPARISON
--------------------
1. Select "PDF Structure Comparison"
2. Upload original document (.pdf)
3. Upload modified version (.pdf)
4. Add critical keywords (one per line):
   - security
   - mandatory
   - compliance
   - shall
   - must
5. Click "Compare Documents"
6. Review flagged critical changes first
7. Export report for your team


IMPORTANT NOTES
---------------
- Keep the entire folder together (don't move just the .exe file)
- First startup is slower (10-20 seconds) - this is normal
- The console window shows application status - don't close it
- If browser doesn't open, manually go to: http://localhost:8501
- All processing is done locally - no data sent to cloud


TROUBLESHOOTING
---------------

Problem: "Windows Defender blocked this app"
Solution: Click "More info" → "Run anyway"

Problem: "Application won't start"
Solution:
- Right-click DocumentComparison.exe → "Run as administrator"
- Check antivirus isn't blocking it
- Verify entire folder was extracted (not just the .exe)

Problem: "Browser doesn't open"
Solution:
- Wait 30 seconds
- Manually open browser to: http://localhost:8501
- Check console window for errors

Problem: "Port already in use"
Solution:
- Another instance is running
- Close other instances or restart computer

Problem: "Application is very slow"
Solution:
- Close other applications to free memory
- First launch is always slower
- Processing large files takes time (normal)


FEATURES
--------
Excel Comparison:
✓ Cell-by-cell change tracking
✓ Synchronized horizontal & vertical scrolling
✓ Formula modification detection
✓ Visual highlighting of changes
✓ Export to Excel, Text, or JSON

PDF Comparison:
✓ Intelligent section matching
✓ Handles reordering and removal
✓ Critical keyword highlighting
✓ Multiple view modes
✓ Export to Excel, Text, or JSON


KEYBOARD SHORTCUTS
------------------
Ctrl + R  : Refresh page
Ctrl + K  : Clear cache and rerun
Ctrl + C  : Close application (in console window)


FILE SIZE LIMITS
----------------
Excel: Recommended <10 MB (larger files work but slower)
PDF: Recommended <50 MB (larger files work but slower)


GETTING HELP
------------
For issues or questions:
- Check this guide first
- Review console window for error messages
- Contact your IT support or system administrator


PRIVACY & SECURITY
------------------
✓ All processing done locally on your computer
✓ No data sent to internet or cloud
✓ Files processed in memory only
✓ No files stored by application
✓ Safe for confidential documents


VERSION INFORMATION
-------------------
Version: 1.0
Release Date: 2024
Platform: Windows 10/11 64-bit

Technology:
- Built with Python and Streamlit
- PDF parsing with pdfplumber
- Excel handling with openpyxl


LICENSE
-------
Internal use only - not for redistribution


SUPPORT
-------
For technical support, please contact:
[Your IT Department]
Email: [Your Email]
Phone: [Your Phone]


TIPS FOR BEST RESULTS
----------------------
1. Use standardized templates with clear headings
2. Define critical keywords for your document type
3. Review critical changes first (marked with 🔴)
4. Export reports for team collaboration
5. Keep application updated to latest version


WHAT'S INCLUDED
---------------
✓ Excel spreadsheet comparison
✓ PDF document structure comparison
✓ Multiple view modes
✓ Export capabilities
✓ User-friendly interface
✓ No Python installation required


LIMITATIONS
-----------
- Requires Windows operating system
- PDF must be text-based (not scanned images)
- Processing time increases with file size
- One comparison at a time per instance


UPDATES
-------
Check with your administrator for newer versions.
Recommended to use latest version for best results.


================================================================================
                          Thank you for using our tool!
================================================================================

For the latest information and support, contact your IT department.
