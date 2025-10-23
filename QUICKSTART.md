# 🚀 Quick Start Guide - Document Comparison Suite

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Install Dependencies

Open a terminal/command prompt in the project directory and run:

```bash
pip install -r requirements.txt
```

This will install:
- `streamlit` - Web interface framework
- `pandas` - Data manipulation
- `openpyxl` - Excel file handling
- `numpy` - Numerical operations
- `pdfplumber` - PDF text extraction

### Step 2: Verify Installation

Check that Streamlit is installed correctly:

```bash
streamlit --version
```

You should see output like: `Streamlit, version 1.28.0`

## Running the Application

### Option 1: Unified Tool Suite (Recommended)

Run the unified application with both Excel and PDF comparison:

```bash
streamlit run app.py
```

This opens a browser window where you can choose:
- 📊 Excel Diff Visualizer
- 📄 PDF Structure Comparison

### Option 2: Excel Comparison Only

Run just the Excel comparison tool:

```bash
streamlit run main.py
```

### Option 3: PDF Comparison Only

Run just the PDF comparison tool:

```bash
streamlit run pdf_compare_ui.py
```

## First Time Usage

### Excel Comparison

1. **Launch the tool**: `streamlit run app.py`
2. **Select "Excel Diff Visualizer"**
3. **Upload files**:
   - Click "Upload Original Template" (your baseline Excel file)
   - Click "Upload Modified Version" (supplier's modified file)
4. **Click "Compare Files"**
5. **Review results**: See synchronized side-by-side comparison
6. **Export**: Download reports in your preferred format

### PDF Comparison

1. **Launch the tool**: `streamlit run app.py`
2. **Select "PDF Structure Comparison"**
3. **Upload documents**:
   - Upload "Original Template" (your baseline PDF)
   - Upload "Supplier Modified Version" (modified PDF)
4. **Configure settings**:
   - Choose view mode (start with "Structured Overview")
   - Add critical keywords (one per line)
5. **Click "Compare Documents"**
6. **Review results**: Analyze changes by section
7. **Export**: Download change reports

## Example Workflow for Analysts

### Scenario: Supplier Modified Requirement Document

```
Day 1 - Send to Supplier:
✓ Send requirement_template_v1.0.pdf to supplier

Day 7 - Receive from Supplier:
✓ Receive supplier_requirements_modified.pdf

Day 7 - Analysis (5 minutes):
1. Launch: streamlit run app.py
2. Select: PDF Structure Comparison
3. Upload both PDFs
4. Add keywords: security, mandatory, compliance, shall
5. Click Compare
6. Review 🔴 critical changes first
7. Check removed sections
8. Export Excel summary for team review

Day 8 - Follow-up:
✓ Share Excel summary with stakeholders
✓ Request clarification on critical changes
✓ Archive comparison report for audit trail
```

## Common Use Cases

### 1. Quick Template Check (Excel)

**Time: 2 minutes**

```bash
streamlit run main.py
```
- Upload template_original.xlsx
- Upload template_from_supplier.xlsx
- Click Compare
- Scan yellow highlights for changes
- Export if needed

### 2. Requirement Document Review (PDF)

**Time: 5 minutes**

```bash
streamlit run app.py
```
- Select PDF tool
- Upload both PDFs
- Add critical keywords
- Compare
- Review critical changes
- Export for team

### 3. Monthly Template Audit (Excel)

**Time: 10 minutes**

- Compare current month vs previous month
- Check for unauthorized changes
- Export JSON for record keeping
- Archive comparison reports

## File Structure

```
Excel-Tracker/
├── app.py                    # Unified application launcher
├── main.py                   # Excel comparison tool
├── pdf_compare.py            # PDF comparison engine
├── pdf_compare_ui.py         # PDF comparison UI
├── requirements.txt          # Python dependencies
├── README_PDF_COMPARE.md     # Detailed PDF tool documentation
└── QUICKSTART.md            # This file
```

## Keyboard Shortcuts

When the Streamlit app is running:

- `Ctrl + R` / `Cmd + R` - Refresh the page
- `Ctrl + K` / `Cmd + K` - Clear cache and rerun
- `Ctrl + Click` on file links - Open in new tab

## Tips for Faster Analysis

### Excel Comparison

1. **Use "Summary Only" view first** - Get quick overview
2. **Filter empty changes** - Uncheck "Show [empty] → value changes" if not needed
3. **Export Excel with highlights** - Easier to share with non-technical team
4. **Use horizontal scroll** - Both panels scroll together

### PDF Comparison

1. **Start with Summary Dashboard** - See statistics first
2. **Check critical changes** - Look for 🔴 flags
3. **Review removed sections** - Ensure nothing important was deleted
4. **Use "Change List Only"** - For quick scanning
5. **Export text report** - Easy to email

## Troubleshooting

### Issue: "Address already in use"

**Solution**: Another Streamlit app is running.

```bash
# Run on different port
streamlit run app.py --server.port 8502
```

### Issue: "ModuleNotFoundError"

**Solution**: Dependencies not installed.

```bash
pip install -r requirements.txt
```

### Issue: PDF not parsing correctly

**Possible causes**:
- PDF is image-based (use OCR first)
- Headings not clearly formatted
- Try uploading a different PDF to test

### Issue: Excel comparison very slow

**Solution**:
- Large files take longer
- Close other applications
- Use "Summary Only" view first

### Issue: Browser doesn't open automatically

**Solution**: Manually open browser to:
```
http://localhost:8501
```

## Performance Notes

### Excel Comparison
- **Small files (<1MB)**: Instant
- **Medium files (1-5MB)**: 2-5 seconds
- **Large files (>5MB)**: 10-30 seconds

### PDF Comparison
- **Small docs (<50 pages)**: 5-10 seconds
- **Medium docs (50-200 pages)**: 10-30 seconds
- **Large docs (>200 pages)**: 30-60 seconds

## Advanced Configuration

### Change Default Port

Edit `.streamlit/config.toml` (create if doesn't exist):

```toml
[server]
port = 8502
headless = false
```

### Increase Upload Limit

For very large files, edit `.streamlit/config.toml`:

```toml
[server]
maxUploadSize = 500
```

### Dark Mode

Streamlit auto-detects system theme. To force dark mode:

```toml
[theme]
base = "dark"
```

## Getting Help

### Check Logs

Streamlit shows errors in the terminal. Look for:
- Red error messages
- Traceback information
- Warning messages

### Debug Mode

Run with verbose output:

```bash
streamlit run app.py --logger.level debug
```

### Clear Cache

If results seem stale:
- Click hamburger menu (☰) in top right
- Select "Clear cache"
- Click "Rerun"

## Next Steps

1. ✅ Install dependencies
2. ✅ Run the application
3. ✅ Try sample comparison
4. 📖 Read full documentation in README_PDF_COMPARE.md
5. 🎯 Use with real documents
6. 📊 Share with team

## Support

For issues or questions:
1. Check this guide first
2. Review README_PDF_COMPARE.md for detailed docs
3. Check error messages in terminal
4. Test with sample files

## Updates

To update dependencies:

```bash
pip install --upgrade -r requirements.txt
```

To check for Streamlit updates:

```bash
pip show streamlit
pip install --upgrade streamlit
```

---

**You're ready to go! 🚀**

Run `streamlit run app.py` and start comparing documents!
