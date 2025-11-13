# Excel Comparison EXE - Build Guide

## Quick Start (Easiest Method)

Just double-click: **`build_excel_exe.bat`**

That's it! The script will:
1. Create a virtual environment
2. Install only Excel dependencies (~50MB)
3. Build the EXE with PyInstaller
4. Create `ExcelCompare.exe` (ready to share!)

**Time**: 5-10 minutes
**Final Size**: ~80-120MB (much smaller than with PDF libraries!)

---

## What You Get

**ExcelCompare.exe**
- Standalone executable
- No Python required to run
- No dependencies required
- Works on any Windows PC
- Can be shared with anyone!

---

## Manual Build (If Script Fails)

```bash
# 1. Create clean virtual environment
python -m venv venv_excel
venv_excel\Scripts\activate

# 2. Install minimal dependencies
pip install -r requirements_excel_only.txt
pip install pyinstaller

# 3. Build EXE
pyinstaller --clean --noconfirm excel_compare.spec

# 4. Find your EXE
# Location: dist\ExcelCompare.exe
```

---

## Troubleshooting

### Issue 1: "PyInstaller not found"

**Solution:**
```bash
pip install pyinstaller
```

### Issue 2: "ModuleNotFoundError" when running EXE

**Solution:** Add missing module to `excel_compare.spec` hiddenimports:
```python
hiddenimports=[
    'streamlit',
    'your_missing_module_here',
    ...
]
```

Then rebuild:
```bash
pyinstaller --clean excel_compare.spec
```

### Issue 3: Antivirus blocks PyInstaller

**Solution:**
1. Temporarily disable antivirus
2. Add exception for PyInstaller
3. Or use `--noupx` flag in spec file

### Issue 4: EXE is too large (>200MB)

**Reasons:**
- Including unnecessary dependencies
- Not excluding PDF/ML libraries

**Solution:** Check `excel_compare.spec` excludes section. Should exclude:
- torch, transformers, scipy
- pdfplumber, pypdf2
- All PDF comparison modules

### Issue 5: EXE crashes immediately

**Solution:**
1. Run from command line to see errors:
   ```bash
   ExcelCompare.exe
   ```

2. Check for missing DLLs:
   - Install Visual C++ Redistributable
   - https://aka.ms/vs/17/release/vc_redist.x64.exe

3. Rebuild with console mode:
   ```python
   # In excel_compare.spec
   console=True  # Shows debug output
   ```

---

## Size Comparison

| Build Type | Size | Dependencies |
|------------|------|--------------|
| **Excel Only** | ~80-120MB | Minimal |
| Full App (with PDF) | ~2-5GB | All ML libraries |

By excluding PDF comparison, we save 95% of space!

---

## What's Excluded

The EXE **only includes Excel comparison**, excluding:

❌ PDF comparison features
❌ Machine learning libraries
❌ Translation service
❌ Semantic embedder
❌ LLM integration

✅ Excel file upload
✅ Cell-by-cell comparison
✅ VS Code-style diff view
✅ Export to Excel/JSON/Text
✅ All Excel-specific features

---

## Distribution

### Method 1: Send EXE directly
- Email/USB/Cloud storage
- Recipient just double-clicks to run
- No installation needed!

### Method 2: Create installer (optional)
Use Inno Setup or NSIS to create a proper installer:
- Professional appearance
- Desktop shortcut
- Start menu entry
- Uninstaller

---

## Advanced: Reduce Size Further

### Option 1: Use UPX compression
Already enabled in spec file (`upx=True`)

### Option 2: One-folder mode
Change in spec file:
```python
exe = EXE(
    ...
    # Instead of one-file, use one-folder (smaller)
)

# Then use:
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='ExcelCompare'
)
```

This creates a folder with smaller EXE + DLLs (~60MB total)

### Option 3: Exclude more Streamlit files
If some Streamlit features aren't used, exclude them in spec.

---

## Testing Your EXE

1. **Test on build machine:**
   ```bash
   ExcelCompare.exe
   ```
   Should open browser with Excel comparison UI

2. **Test on clean VM:**
   - Windows 10/11 without Python
   - Copy only ExcelCompare.exe
   - Double-click to run
   - Should work without any installation!

3. **Test with actual Excel files:**
   - Upload two Excel files
   - Run comparison
   - Export results

---

## Common Errors & Fixes

### Error: "Failed to execute script"
**Fix:** Missing runtime dependencies. Install:
```bash
# Visual C++ Redistributable
# Download from Microsoft
```

### Error: "Streamlit command not found"
**Fix:** Check spec file includes Streamlit correctly:
```python
datas=[
    ('venv/Lib/site-packages/streamlit/static', 'streamlit/static'),
]
```

### Error: Import errors for pandas/openpyxl
**Fix:** Add to hiddenimports in spec file

### Browser doesn't open
**Fix:** EXE runs but browser doesn't auto-open.
Manually go to: http://localhost:8501

---

## Performance

| Operation | Time |
|-----------|------|
| EXE startup | 5-10 seconds |
| Load Excel file | 1-2 seconds |
| Compare files | 2-5 seconds |
| Export results | 1-2 seconds |

First run is slower (Streamlit initialization)

---

## Security Note

Some antivirus software flags PyInstaller EXEs as suspicious (false positive).

**To fix:**
1. Code-sign your EXE (costs money)
2. Report false positive to antivirus vendor
3. Tell users to add exception

---

## Next Steps

After successful build:

1. ✅ Test EXE on your machine
2. ✅ Test on another PC without Python
3. ✅ Document usage for recipients
4. ✅ Distribute!

---

## Need Help?

Run diagnostic:
```bash
python -c "import streamlit; import pandas; import openpyxl; print('All dependencies OK!')"
```

Check PyInstaller version:
```bash
pyinstaller --version
```

Should be 5.0 or higher.

---

## Success Checklist

- [ ] `build_excel_exe.bat` runs without errors
- [ ] `ExcelCompare.exe` created in root folder
- [ ] EXE size is reasonable (80-150MB)
- [ ] EXE runs and opens browser
- [ ] Can upload Excel files
- [ ] Comparison works correctly
- [ ] Export functionality works
- [ ] Tested on clean Windows PC

If all checked, you're ready to distribute! 🎉
