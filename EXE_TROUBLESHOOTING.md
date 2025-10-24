# EXE Build and Runtime Troubleshooting Guide

## Problem: EXE Opens Command Prompt and Closes Immediately

This is the most common issue when running PyInstaller executables.

---

## Quick Fix Steps

### Step 1: Use Debug Mode to See Errors

Run the debug launcher to see what error is happening:

```bash
run_debug.bat
```

This will:
- Launch the EXE
- Keep the command prompt open
- Show any error messages
- Wait for you to press a key before closing

### Step 2: Common Causes and Solutions

#### Cause 1: Missing Application Files in Build

**Symptom**: Error like "ModuleNotFoundError: No module named 'pdf_compare_optimized'"

**Solution**: The spec file was missing new Python files. This has been FIXED.

**Updated Files**:
- ✅ `pdf_compare_optimized.py` - Added to spec
- ✅ `pdf_compare_ui_optimized.py` - Added to spec
- ✅ `smart_diff.py` - Added to spec

**Action**: Rebuild the EXE with the updated spec file:
```bash
build_with_venv.bat
```

#### Cause 2: Missing Streamlit Dependencies

**Symptom**: Error like "No module named 'streamlit.runtime'"

**Solution**: Ensure all dependencies are installed before building

**Action**:
```bash
# Activate venv
venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt

# Rebuild
build_with_venv.bat
```

#### Cause 3: Port Already in Use

**Symptom**: Error like "Address already in use" or "Port 8501 is in use"

**Solution**: Another Streamlit instance is running

**Action**:
1. Close any running Streamlit applications
2. Open Task Manager (Ctrl+Shift+Esc)
3. End any "python.exe" or "streamlit.exe" processes
4. Try running the EXE again

#### Cause 4: Antivirus Blocking

**Symptom**: EXE disappears or gets quarantined

**Solution**: PyInstaller executables are sometimes flagged as suspicious

**Action**:
1. Check your antivirus quarantine
2. Add exception for `dist\DocumentComparison\DocumentComparison.exe`
3. Windows Defender: Settings → Virus & threat protection → Exclusions
4. Rebuild if needed

#### Cause 5: Missing Runtime Files

**Symptom**: Error about missing DLL files or Visual C++ runtime

**Solution**: Install Visual C++ Redistributable

**Action**:
1. Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Install the redistributable
3. Restart computer
4. Try running EXE again

---

## Rebuild with Fixed Spec File

The spec file has been updated to include all new files. Follow these steps:

### Step 1: Clean Previous Build

```bash
# Remove old build artifacts
rmdir /s /q build
rmdir /s /q dist
```

### Step 2: Activate Virtual Environment

```bash
# If you have venv:
venv\Scripts\activate

# Or .venv:
.venv\Scripts\activate

# Or env:
env\Scripts\activate
```

### Step 3: Verify Dependencies

```bash
# Check all required packages
python -c "import streamlit; import pdfplumber; import openpyxl; print('All dependencies OK')"
```

Expected output: `All dependencies OK`

If you get an error, install dependencies:
```bash
pip install -r requirements.txt
```

### Step 4: Rebuild EXE

```bash
build_with_venv.bat
```

This will:
1. Clean old build
2. Run PyInstaller with updated spec
3. Create new EXE with all files included

### Step 5: Test the EXE

```bash
run_debug.bat
```

You should see:
```
========================================
Document Comparison Tool - DEBUG MODE
========================================

Current directory: C:\...\dist\DocumentComparison

Contents:
DocumentComparison.exe
[... other files ...]

========================================
Starting application...
========================================

  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

Browser should open automatically showing the application.

---

## Detailed Error Messages and Solutions

### Error: "Failed to execute script launcher"

**Cause**: launcher.py can't find or import app.py

**Check**:
1. Verify `launcher.py` exists in the project root
2. Verify `app.py` is listed in the spec file (line 30)
3. Rebuild with updated spec

**Debug**:
```bash
# Check if launcher.py exists
dir launcher.py

# Read launcher.py content
type launcher.py
```

### Error: "ModuleNotFoundError: No module named 'pdf_compare_optimized'"

**Cause**: New Python files not included in spec file

**Solution**: ✅ FIXED in updated spec file

**Verify Fix**:
```bash
# Check spec file includes new modules
findstr /i "optimized" document_comparison.spec
findstr /i "smart_diff" document_comparison.spec
```

Should show:
```
('pdf_compare_optimized.py', '.'),
('pdf_compare_ui_optimized.py', '.'),
('smart_diff.py', '.'),
```

### Error: "AttributeError: module 'streamlit' has no attribute 'web'"

**Cause**: Streamlit version mismatch or incomplete installation

**Solution**:
```bash
# Uninstall and reinstall streamlit
pip uninstall streamlit
pip install streamlit>=1.28.0

# Rebuild
build_with_venv.bat
```

### Error: "RuntimeError: This app has encountered an error"

**Cause**: Generic Streamlit error, need to see full traceback

**Solution**: Use debug mode
```bash
run_debug.bat
```

Look for the full error traceback and address the specific issue.

### Error: "FileNotFoundError: [Errno 2] No such file or directory"

**Cause**: Application trying to access a file with wrong path

**Check**:
- Are all .py files in the spec file?
- Are paths in code using relative paths?

**Common Issues**:
```python
# BAD - absolute path
with open('C:\\Users\\saiga\\...\\file.py')

# GOOD - relative path
with open('app.py')
```

---

## Verification Checklist

Before building, ensure:

- [ ] Virtual environment activated
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] All Python files exist:
  - [ ] app.py
  - [ ] main.py
  - [ ] launcher.py
  - [ ] pdf_compare.py
  - [ ] pdf_compare_ui.py
  - [ ] pdf_compare_optimized.py
  - [ ] pdf_compare_ui_optimized.py
  - [ ] smart_diff.py
- [ ] Spec file updated (document_comparison.spec)
- [ ] Previous build cleaned (no old dist/build folders)

After building, verify:

- [ ] dist\DocumentComparison folder exists
- [ ] DocumentComparison.exe exists in that folder
- [ ] Size is reasonable (>50MB, usually 200-300MB)
- [ ] run_debug.bat shows no errors
- [ ] Application opens in browser
- [ ] All 3 tools visible (Excel, PDF, PDF Fast)

---

## Manual Debug Commands

If run_debug.bat doesn't help, try these:

### Check EXE Dependencies

```bash
# Navigate to dist folder
cd dist\DocumentComparison

# List all files
dir

# Check if Python files are bundled
dir *.py

# Run with Python error output
DocumentComparison.exe 2> error.log
type error.log
```

### Check Streamlit Installation in EXE

```bash
cd dist\DocumentComparison

# The EXE should have streamlit bundled
# Check if _internal folder exists
dir _internal
```

### Run Directly with Python (Not EXE)

To verify the application code works:

```bash
# In main project folder (not dist)
python launcher.py
```

If this works but EXE doesn't, it's a PyInstaller packaging issue.

---

## Rebuild from Scratch

If all else fails, completely rebuild:

```bash
# 1. Clean everything
rmdir /s /q build
rmdir /s /q dist
del /f /q *.spec

# 2. Activate venv
venv\Scripts\activate

# 3. Reinstall all dependencies
pip uninstall -y streamlit pdfplumber openpyxl pandas pyinstaller
pip install -r requirements.txt

# 4. Verify installation
python test_installation.py

# 5. Build with fresh spec
pyinstaller document_comparison.spec --clean --noconfirm

# 6. Test
run_debug.bat
```

---

## What the Updated Spec File Includes

The `document_comparison.spec` file now includes:

```python
# Add application files
datas += [
    ('app.py', '.'),
    ('main.py', '.'),
    ('pdf_compare.py', '.'),
    ('pdf_compare_ui.py', '.'),
    ('pdf_compare_optimized.py', '.'),      # ← ADDED
    ('pdf_compare_ui_optimized.py', '.'),   # ← ADDED
    ('smart_diff.py', '.'),                 # ← ADDED
]
```

These are the files that were missing in the previous build, causing the immediate crash.

---

## Expected Build Output

When building successfully, you should see:

```
========================================
Document Comparison Suite - EXE Builder
========================================

Python found:
Python 3.x.x

Step 1: Cleaning previous builds...
    Done.

Step 2: Building executable with PyInstaller...
    This may take 5-10 minutes...

[... PyInstaller output ...]

INFO: Building EXE from EXE-00.toc completed successfully.
INFO: Building COLLECT COLLECT-00.toc completed successfully.

========================================
BUILD SUCCESSFUL!
========================================

Your executable is ready at:
    dist\DocumentComparison\DocumentComparison.exe

The complete folder to distribute:
    dist\DocumentComparison\
```

---

## Expected Runtime Behavior

When running the EXE successfully:

```
run_debug.bat

========================================
Document Comparison Tool - DEBUG MODE
========================================

Current directory: C:\Users\saiga\Desktop\csi\Excel-Tracker\dist\DocumentComparison

========================================
Starting application...
========================================

  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501

[Browser opens automatically]
[Application shows 3 options:]
1. Excel Comparison
2. PDF Comparison
3. PDF Comparison (Fast & Optimized)
```

---

## Testing the Fixed Build

### Test 1: Basic Launch

```bash
run_debug.bat
```

**Expected**:
- Command prompt stays open
- Shows "You can now view your Streamlit app"
- Browser opens with application

**If Fails**: Read error message in command prompt

### Test 2: Application Functionality

Once browser opens:

1. Click "PDF Comparison (Fast & Optimized)"
2. Upload two test PDFs
3. Click "Extract Structure"

**Expected**: No errors, structure extracts successfully

**If Fails**: Check console output in command prompt

### Test 3: Standalone Test

Copy the entire `dist\DocumentComparison` folder to a different location (like Desktop).

Run `DocumentComparison.exe` from there.

**Expected**: Works independently, no errors

**If Fails**: Missing dependencies or files

---

## Common Build Warnings (Safe to Ignore)

These warnings are normal and won't prevent the EXE from working:

```
WARNING: lib not found: ...
WARNING: Cannot find imports for ...
WARNING: Hidden import ... not found
```

As long as you see "BUILD SUCCESSFUL!" at the end, these are okay.

---

## Getting More Help

### Collect Debug Information

If you still have issues, collect this information:

```bash
# 1. Python version
python --version

# 2. Package versions
pip list | findstr "streamlit pdfplumber pyinstaller"

# 3. Error from debug run
run_debug.bat > debug_output.txt 2>&1

# 4. Build output
build_with_venv.bat > build_output.txt 2>&1

# 5. File listing
dir dist\DocumentComparison > files.txt
```

### Check Build Logs

After building, check:
- `build\DocumentComparison\warn-DocumentComparison.txt` - Build warnings
- `build\DocumentComparison\xref-DocumentComparison.html` - Cross-references

---

## Summary

**Root Cause**: Spec file was missing new Python files (pdf_compare_optimized.py, pdf_compare_ui_optimized.py, smart_diff.py)

**Fix Applied**: Updated document_comparison.spec to include all files

**Next Steps**:
1. Run `build_with_venv.bat` to rebuild with updated spec
2. Run `run_debug.bat` to test and see any errors
3. Application should work correctly now

**If Still Having Issues**:
1. Use `run_debug.bat` to see actual error message
2. Check this troubleshooting guide for that specific error
3. Verify all files exist and venv is activated

---

**The spec file fix should resolve your issue!** Rebuild and test with the debug script.
