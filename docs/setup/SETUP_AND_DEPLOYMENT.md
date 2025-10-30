# Setup and Deployment Guide

## 🎯 Purpose

This guide explains how to set up the Document Comparison Suite from scratch on a new server. Follow these steps after cloning the repository.

---

## 📋 Prerequisites

### Hardware Requirements (Your Server):
- ✅ CPU: Multi-core processor
- ✅ RAM: 128GB (excellent!)
- ✅ GPU: 32GB dedicated graphics (excellent!)
- ✅ Storage: 1TB available (excellent!)
- ✅ OS: Windows Server or Windows 10/11

### Software Requirements:
- Python 3.10 or 3.11 (NOT 3.12, compatibility issues with some libraries)
- Git (for cloning repository)
- CUDA Toolkit 11.8+ (for GPU acceleration)
- Internet connection (for initial model download only)

---

## 🚀 Step-by-Step Setup

### Step 1: Install Python

**Download Python 3.11**:
```
https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
```

**Installation Options**:
- ✅ Check "Add Python to PATH"
- ✅ Install for all users
- ✅ Customize: Install pip, tcl/tk, documentation

**Verify Installation**:
```bash
python --version
# Should show: Python 3.11.x

pip --version
# Should show: pip 24.x.x
```

---

### Step 2: Install CUDA Toolkit (for GPU)

**Download CUDA 12.1**:
```
https://developer.nvidia.com/cuda-12-1-0-download-archive
```

**Select**:
- OS: Windows
- Architecture: x86_64
- Version: Your Windows version
- Installer: exe (network)

**Verify Installation**:
```bash
nvcc --version
# Should show CUDA version

nvidia-smi
# Should show your GPU (32GB VRAM)
```

---

### Step 3: Clone Repository

```bash
# Navigate to desired location
cd C:\

# Clone repository
git clone https://github.com/saiganesh-d/Excel-Tracker.git

# Navigate to project
cd Excel-Tracker
```

---

### Step 4: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# You should see (venv) in your prompt
```

---

### Step 5: Install Dependencies

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install PyTorch with CUDA support (IMPORTANT!)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Verify CUDA is available
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"
# Should show: CUDA available: True

# Install all other requirements
pip install -r requirements.txt

# This will install:
# - streamlit (web framework)
# - sentence-transformers (embeddings)
# - transformers (translation)
# - pdfplumber (PDF extraction)
# - langdetect (language detection)
# - scikit-learn (similarity calculations)
# - llama-cpp-python (optional local LLM)
# - and more...
```

**Expected Duration**: 10-15 minutes (depending on internet speed)

---

### Step 6: Download Models

**Run the model download script**:
```bash
python download_models.py
```

This will download:
1. **Multilingual Embeddings** (420MB)
   - Model: paraphrase-multilingual-mpnet-base-v2
   - Purpose: Semantic understanding (50+ languages)

2. **German→English Translation** (300MB)
   - Model: Helsinki-NLP/opus-mt-de-en
   - Purpose: Translate German documents

3. **English→German Translation** (300MB)
   - Model: Helsinki-NLP/opus-mt-en-de
   - Purpose: Translate to German if needed

4. **Optional: Local LLM** (2-4GB)
   - Model: Llama-3.2-3B-Instruct
   - Purpose: Explain semantic differences

**Total Download**: ~5GB
**Duration**: 15-30 minutes (depending on internet speed)

**Models will be cached in**:
```
Excel-Tracker/models/
```

**You only need to download once!** After this, no internet is needed.

---

### Step 7: Test Installation

```bash
# Test core components
python test_installation.py
```

**Expected Output**:
```
Testing Document Comparison Suite Installation
==============================================

1. Testing Python packages...
   ✓ streamlit 1.28.0+
   ✓ torch 2.0.0+ (CUDA available)
   ✓ sentence-transformers 2.2.0+
   ✓ transformers 4.30.0+
   ✓ pdfplumber 0.10.0+
   ✓ langdetect 1.0.9+
   ✓ scikit-learn 1.3.0+

2. Testing GPU...
   ✓ CUDA available: True
   ✓ GPU: NVIDIA RTX [Your GPU Model]
   ✓ GPU Memory: 32GB

3. Testing models...
   ✓ Multilingual embeddings loaded
   ✓ Translation models loaded
   ✓ All models ready!

==============================================
✅ Installation successful! Ready to run.
```

---

### Step 8: Run the Application

```bash
# Make sure virtual environment is activated
venv\Scripts\activate

# Run Streamlit app
streamlit run app.py
```

**Expected Output**:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

**Browser will open automatically showing the application!**

---

## 🌐 Network Access (Allow Other Users)

### Option 1: Local Network Access

**Find your server IP**:
```bash
ipconfig
# Look for IPv4 Address (e.g., 192.168.1.100)
```

**Users access via**:
```
http://192.168.1.100:8501
```

### Option 2: External Access (with Firewall)

**Open Windows Firewall**:
```bash
# Run as Administrator
netsh advfirewall firewall add rule name="Streamlit" dir=in action=allow protocol=TCP localport=8501
```

**Configure Router Port Forwarding** (if needed):
- External Port: 8501
- Internal IP: Your server IP
- Internal Port: 8501

### Option 3: HTTPS (Secure - Recommended)

**Use Streamlit with SSL**:
```bash
streamlit run app.py --server.port 8501 --server.sslCertFile cert.pem --server.sslKeyFile key.pem
```

---

## 🔄 Starting Application Automatically

### Create Startup Script

**File: `start_app.bat`**
```batch
@echo off
cd C:\Excel-Tracker
call venv\Scripts\activate
streamlit run app.py --server.headless true
```

**Run on Windows Startup**:
1. Press `Win + R`
2. Type `shell:startup`
3. Create shortcut to `start_app.bat`

**Or use Windows Task Scheduler** (better for servers):
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: At startup
4. Action: Start program
5. Program: `C:\Excel-Tracker\start_app.bat`

---

## 🛠️ Maintenance

### Update Application

```bash
# Navigate to project
cd C:\Excel-Tracker

# Pull latest changes
git pull

# Activate virtual environment
venv\Scripts\activate

# Update dependencies (if changed)
pip install -r requirements.txt --upgrade

# Restart application
# (Stop current instance with Ctrl+C, then)
streamlit run app.py
```

### Clear Cache

```bash
# Clear Streamlit cache
streamlit cache clear

# Clear translation cache
del translation_cache.db

# Models are safe in models/ folder
```

### Check Logs

Streamlit logs are shown in the command prompt where you ran `streamlit run app.py`.

To save logs to file:
```bash
streamlit run app.py > logs.txt 2>&1
```

---

## 🐛 Troubleshooting

### Issue 1: CUDA Not Available

**Problem**: `torch.cuda.is_available()` returns False

**Solutions**:
1. Install CUDA Toolkit
2. Install GPU drivers from NVIDIA
3. Reinstall PyTorch with CUDA:
   ```bash
   pip uninstall torch torchvision torchaudio
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

### Issue 2: Models Not Found

**Problem**: Error loading models

**Solutions**:
1. Run download script again:
   ```bash
   python download_models.py
   ```
2. Check `models/` folder exists
3. Check internet connection

### Issue 3: Out of Memory

**Problem**: GPU out of memory error

**Solutions**:
1. Reduce batch size (already optimized in code)
2. Process documents in chunks
3. With 32GB GPU, this should NOT happen - check if other apps using GPU

### Issue 4: Slow Performance

**Problem**: Processing takes too long

**Check**:
1. Is GPU being used?
   ```python
   python -c "import torch; print(torch.cuda.is_available())"
   ```
2. Are models loaded?
3. Check GPU utilization: `nvidia-smi`

**With your hardware (32GB GPU), should be very fast (~30 seconds per 100 pages)**

### Issue 5: Port Already in Use

**Problem**: Port 8501 already in use

**Solutions**:
1. Stop other Streamlit instances
2. Or use different port:
   ```bash
   streamlit run app.py --server.port 8502
   ```

### Issue 6: Translation Errors

**Problem**: Translation fails or shows errors

**Solutions**:
1. Check models downloaded:
   ```bash
   ls models/
   ```
2. Re-download translation models:
   ```bash
   python download_models.py --translation-only
   ```

---

## 📊 Performance Tuning

### GPU Settings

**Set default GPU** (if multiple GPUs):
```python
# In app.py or comparator files
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'  # Use first GPU
```

### Batch Size

**Adjust in semantic_embedder.py**:
```python
embeddings = self.model.encode(
    paragraphs,
    batch_size=64,  # Increase for better GPU utilization
    show_progress_bar=True
)
```

**With 32GB GPU, you can use large batch sizes (128-256)**

### Translation Caching

Translation cache is automatic via SQLite database.

**Check cache size**:
```bash
# In Excel-Tracker folder
dir translation_cache.db
```

**Clear cache if too large**:
```bash
del translation_cache.db
# Will be recreated automatically
```

---

## 🔐 Security (Optional)

Since you mentioned no authentication needed, security is minimal. But if you change your mind:

### Add Password Protection

Install:
```bash
pip install streamlit-authenticator
```

Update `app.py`:
```python
import streamlit_authenticator as stauth

# Simple authentication
names = ['Admin', 'User1']
usernames = ['admin', 'user1']
passwords = ['admin123', 'user123']  # Use hashed passwords in production!

authenticator = stauth.Authenticate(
    names, usernames, passwords,
    'app_name', 'auth_key', cookie_expiry_days=30
)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    authenticator.logout('Logout', 'main')
    # Your app code here
elif authentication_status == False:
    st.error('Username/password is incorrect')
```

---

## 📁 File Structure After Setup

```
Excel-Tracker/
├── venv/                           # Virtual environment
├── models/                         # Downloaded models (~5GB)
│   ├── paraphrase-multilingual-mpnet-base-v2/
│   ├── opus-mt-de-en/
│   ├── opus-mt-en-de/
│   └── llama-3.2-3b/ (optional)
├── translation_cache.db            # Translation cache (created automatically)
├── app.py                          # Main application
├── main.py                         # Excel comparison (existing)
├── pdf_compare_optimized.py        # PDF extraction (existing)
├── pdf_compare_ui_optimized.py     # PDF UI (existing)
├── smart_diff.py                   # Smart diff (existing)
├── paragraph_extractor.py          # NEW - Paragraph extraction
├── language_detector.py            # NEW - Language detection
├── translation_service.py          # NEW - Local translation
├── semantic_embedder.py            # NEW - Embeddings
├── semantic_comparator.py          # NEW - Semantic comparison
├── requirement_analyzer.py         # NEW - Requirement analysis
├── advanced_pdf_comparator.py      # NEW - Main engine
├── pdf_compare_ui_advanced.py      # NEW - Advanced UI
├── model_manager.py                # NEW - Model management
├── download_models.py              # NEW - Model download script
├── test_installation.py            # Installation test
├── requirements.txt                # Dependencies
├── start_app.bat                   # Startup script
└── SETUP_AND_DEPLOYMENT.md         # This file
```

---

## ⚡ Quick Start Commands

**First Time Setup**:
```bash
git clone https://github.com/saiganesh-d/Excel-Tracker.git
cd Excel-Tracker
python -m venv venv
venv\Scripts\activate
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
python download_models.py
python test_installation.py
streamlit run app.py
```

**Daily Use**:
```bash
cd Excel-Tracker
venv\Scripts\activate
streamlit run app.py
```

**Update Application**:
```bash
cd Excel-Tracker
git pull
venv\Scripts\activate
pip install -r requirements.txt --upgrade
streamlit run app.py
```

---

## 🎯 Expected Performance (Your Hardware)

With 128GB RAM and 32GB GPU:

| Task | Expected Time | Notes |
|------|---------------|-------|
| Extract 100-page PDF | 10 seconds | CPU-bound (pdfplumber) |
| Detect language | <1 second | Very fast |
| Translate 100 paragraphs (German→English) | 10-15 seconds | GPU-accelerated |
| Generate embeddings (100 paragraphs) | 2-3 seconds | GPU-accelerated |
| Compare & match paragraphs | <1 second | CPU (fast with 128GB RAM) |
| Requirement analysis | <1 second | Rule-based |
| **Total for typical document** | **30-40 seconds** | End-to-end |

**Large document (500 pages)**:
- Extraction: 30-40 seconds
- Processing: 60-90 seconds
- **Total: ~2 minutes**

**Your hardware is excellent and will process documents very fast!**

---

## 📞 Support

If you encounter issues:

1. **Check test_installation.py output**
2. **Check this troubleshooting section**
3. **Check application logs**
4. **Verify all models downloaded**: `ls models/`
5. **Verify GPU working**: `nvidia-smi`

---

## ✅ Post-Setup Checklist

After setup, verify:

- [ ] Python 3.11 installed
- [ ] CUDA Toolkit installed
- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] All dependencies installed
- [ ] PyTorch recognizes GPU
- [ ] All models downloaded (~5GB in models/)
- [ ] test_installation.py passes
- [ ] Application starts without errors
- [ ] Browser opens with interface
- [ ] Can upload and process documents
- [ ] Results display correctly

---

## 🎉 You're Ready!

After completing this guide:
- ✅ Application is fully set up
- ✅ All models are downloaded
- ✅ GPU acceleration is working
- ✅ Users can access via browser
- ✅ No internet needed for operation

**Start the application**:
```bash
streamlit run app.py
```

**Access at**: http://localhost:8501

**Share with users**: http://YOUR_SERVER_IP:8501

---

*Last Updated: 2025-10-30*
