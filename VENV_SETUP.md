# 🐍 Virtual Environment Setup Guide

## Overview

This guide helps you work with the Document Comparison Suite when using Python virtual environments instead of global Python installation.

---

## Quick Answer: How to Build EXE with Virtual Environment

### Option 1: Use the Helper Script (Easiest)

```bash
# Just run this - it auto-detects your venv!
build_with_venv.bat
```

### Option 2: Activate Manually

```bash
# 1. Activate your virtual environment
venv\Scripts\activate.bat        # or .venv\Scripts\activate.bat or env\Scripts\activate.bat

# 2. Build the executable
build_exe.bat
```

---

## Detailed Setup

### Step 1: Create Virtual Environment (If You Don't Have One)

```bash
# Navigate to project folder
cd "c:\Users\saiga\Desktop\csi\Excel-Tracker"

# Create virtual environment (choose one name)
python -m venv venv          # Most common
# OR
python -m venv .venv         # Hidden folder
# OR
python -m venv env           # Alternative name
```

**Result:** A folder named `venv` (or `.venv` or `env`) is created with its own Python installation.

---

### Step 2: Activate Virtual Environment

**Windows Command Prompt:**
```bash
venv\Scripts\activate.bat
```

**Windows PowerShell:**
```powershell
venv\Scripts\Activate.ps1
```

**Git Bash:**
```bash
source venv/Scripts/activate
```

**You'll know it's activated when you see:**
```
(venv) C:\Users\saiga\Desktop\csi\Excel-Tracker>
```

---

### Step 3: Install Dependencies

```bash
# Make sure venv is activated first!
pip install -r requirements.txt
```

---

### Step 4: Build the Executable

**Method 1: Auto-activate and build**
```bash
build_with_venv.bat
```

**Method 2: Manual activation**
```bash
# Activate first
venv\Scripts\activate.bat

# Then build
build_exe.bat
```

---

## Understanding Your Setup

### What is a Virtual Environment?

A virtual environment is an **isolated Python installation** for your project. It has its own:
- ✅ Python interpreter
- ✅ pip package manager
- ✅ Installed packages (separate from system)

### Why Use Virtual Environment?

**Advantages:**
- ✅ **Isolation** - Project dependencies don't conflict with system
- ✅ **Reproducibility** - Same environment across machines
- ✅ **No admin rights needed** - Install packages without elevation
- ✅ **Clean** - Delete folder to remove everything

**Your situation:**
- ✅ You don't have global Python installed
- ✅ All work happens in virtual environment
- ✅ This is actually **best practice**!

---

## Common Scenarios

### Scenario 1: I Have a Virtual Environment Named "venv"

```bash
# Activate
venv\Scripts\activate.bat

# Verify
python --version
pip list

# Build
build_exe.bat
```

### Scenario 2: I Have a Virtual Environment Named ".venv"

```bash
# Activate
.venv\Scripts\activate.bat

# Build
build_exe.bat
```

### Scenario 3: I Don't Know Where My Virtual Environment Is

```bash
# Use the helper script - it will find it!
build_with_venv.bat
```

### Scenario 4: I Want to Build from Scratch

```bash
# 1. Create fresh virtual environment
python -m venv venv

# 2. Activate it
venv\Scripts\activate.bat

# 3. Install dependencies
pip install -r requirements.txt

# 4. Test application
streamlit run app.py

# 5. Build executable
build_exe.bat
```

---

## Checking Your Setup

### How to Check if Virtual Environment is Active

```bash
# Check for (venv) prefix in prompt
(venv) C:\Users\saiga\Desktop\csi\Excel-Tracker>

# OR check Python location
where python
# Should show: C:\Users\saiga\Desktop\csi\Excel-Tracker\venv\Scripts\python.exe
```

### How to Check Installed Packages

```bash
# Make sure venv is activated
pip list

# Should see:
# streamlit
# pandas
# openpyxl
# pdfplumber
# pyinstaller
# etc.
```

### How to Verify Everything Works

```bash
# Test installation
python test_installation.py

# Should show all green checkmarks ✓
```

---

## Troubleshooting

### ❌ Error: "Python is not recognized"

**Problem:** Virtual environment not activated

**Solution:**
```bash
# Activate venv first
venv\Scripts\activate.bat

# Then retry
build_exe.bat
```

### ❌ Error: "PyInstaller not found"

**Problem:** PyInstaller not installed in this virtual environment

**Solution:**
```bash
# Make sure venv is activated
venv\Scripts\activate.bat

# Install PyInstaller
pip install pyinstaller>=6.0.0

# Retry build
build_exe.bat
```

### ❌ Error: "Cannot find venv\Scripts\activate.bat"

**Problem:** Virtual environment doesn't exist or has different name

**Solution:**
```bash
# List folders to find venv
dir

# Look for: venv, .venv, env folders

# If found, activate correct one:
YOUR_VENV_NAME\Scripts\activate.bat

# If not found, create new one:
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

### ❌ Build works but EXE is huge (>1 GB)

**Problem:** Virtual environment includes unnecessary packages

**Solution:**
```bash
# Create fresh minimal venv
python -m venv venv_build
venv_build\Scripts\activate.bat

# Install only required packages
pip install -r requirements.txt

# Build from clean environment
build_exe.bat
```

### ❌ PowerShell: "Running scripts is disabled"

**Problem:** PowerShell execution policy

**Solution 1 - Use Command Prompt instead:**
```bash
venv\Scripts\activate.bat
```

**Solution 2 - Change PowerShell policy:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\Activate.ps1
```

---

## Best Practices

### ✅ DO

- **Always activate venv before working**
  ```bash
  venv\Scripts\activate.bat
  ```

- **Keep requirements.txt updated**
  ```bash
  pip freeze > requirements.txt
  ```

- **Use one venv per project**
  - Don't share venvs between projects

- **Test in venv before building**
  ```bash
  streamlit run app.py
  ```

- **Add venv to .gitignore**
  - Venv folders shouldn't be committed

### ❌ DON'T

- **Don't commit venv folder to git**
  - It's huge and machine-specific

- **Don't mix global and venv packages**
  - Always activate venv first

- **Don't delete venv while activated**
  - Deactivate first with `deactivate`

---

## Quick Commands Reference

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows Command Prompt)
venv\Scripts\activate.bat

# Activate (PowerShell)
venv\Scripts\Activate.ps1

# Activate (Git Bash)
source venv/Scripts/activate

# Deactivate (any shell)
deactivate

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py

# Build executable
build_exe.bat

# OR use helper
build_with_venv.bat
```

---

## Your Workflow

Based on your setup (virtual environment only, no global Python):

### Daily Development

```bash
# 1. Open terminal in project folder
cd "c:\Users\saiga\Desktop\csi\Excel-Tracker"

# 2. Activate virtual environment
venv\Scripts\activate.bat

# 3. Run application
streamlit run app.py

# 4. When done, deactivate
deactivate
```

### Building Executable for Distribution

```bash
# Option A: Use helper (easiest)
build_with_venv.bat

# Option B: Manual
venv\Scripts\activate.bat
build_exe.bat
```

### Installing New Packages

```bash
# 1. Activate venv
venv\Scripts\activate.bat

# 2. Install package
pip install package_name

# 3. Update requirements
pip freeze > requirements.txt

# 4. Commit requirements.txt to git
git add requirements.txt
git commit -m "Add package_name dependency"
```

---

## Virtual Environment Folder Structure

```
Excel-Tracker/
├── venv/                          ← Your virtual environment
│   ├── Scripts/
│   │   ├── activate.bat          ← Activation script
│   │   ├── python.exe            ← Python interpreter
│   │   ├── pip.exe               ← Package manager
│   │   └── streamlit.exe         ← Installed tools
│   ├── Lib/
│   │   └── site-packages/        ← Installed packages
│   └── ...
├── app.py                         ← Your application
├── main.py
├── pdf_compare.py
├── requirements.txt               ← Dependencies list
└── build_exe.bat                  ← Build script
```

**Important:** The `venv` folder is usually 200-500 MB. Don't commit it to git!

---

## FAQ

### Q: Can I use a different venv name?

**A:** Yes! The scripts check for common names:
- `venv`
- `.venv`
- `env`

Or use `build_with_venv.bat` and enter your custom name.

### Q: Do I need to activate venv every time?

**A:** Yes, every time you open a new terminal. But it's just one command:
```bash
venv\Scripts\activate.bat
```

### Q: Will the EXE work on machines without Python?

**A:** Yes! The EXE bundles everything. Users don't need Python or virtual environments.

### Q: Can I delete the venv and recreate it?

**A:** Yes!
```bash
# Delete
rmdir /s /q venv

# Recreate
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

### Q: How do I know which Python my venv uses?

**A:**
```bash
# Activate venv
venv\Scripts\activate.bat

# Check version
python --version

# Check location
where python
```

### Q: Can I have multiple virtual environments?

**A:** Yes! For example:
- `venv` - Main development
- `venv_test` - Testing
- `venv_build` - Clean environment for building

Just activate the one you need.

---

## Next Steps

1. ✅ **Verify your venv is working:**
   ```bash
   venv\Scripts\activate.bat
   python test_installation.py
   ```

2. ✅ **Test the application:**
   ```bash
   streamlit run app.py
   ```

3. ✅ **Build the executable:**
   ```bash
   build_with_venv.bat
   ```

4. ✅ **Test the EXE:**
   ```bash
   test_build.bat
   ```

---

## Summary

**For your setup (venv only):**

✅ Use `build_with_venv.bat` - easiest method
✅ OR activate venv first, then run `build_exe.bat`
✅ Everything works the same, just activate first
✅ The EXE will still work on machines without Python

**You're all set!** Your virtual environment setup is actually ideal for development. 🎉
