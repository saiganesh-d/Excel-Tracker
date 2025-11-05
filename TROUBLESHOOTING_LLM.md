# Troubleshooting LLM (llama-cpp-python) Issues

## Common Issue: DLL Import Error

If you see an error like:
```
ImportError: DLL load failed while importing llama_cpp
```

This is a common issue with `llama-cpp-python` on Windows. Here are the solutions:

---

## Solution 1: Use Pre-built Wheels (RECOMMENDED for Windows)

### For CPU only (no GPU):
```bash
pip uninstall llama-cpp-python -y
pip install llama-cpp-python --prefer-binary
```

### For CUDA 11.8 (if you have NVIDIA GPU with CUDA 11.8):
```bash
pip uninstall llama-cpp-python -y
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu118
```

### For CUDA 12.1 (if you have NVIDIA GPU with CUDA 12.1):
```bash
pip uninstall llama-cpp-python -y
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
```

---

## Solution 2: Install Visual C++ Redistributables

The DLL error often means missing Visual C++ runtime libraries.

**Download and install:**
- [Microsoft Visual C++ Redistributable (Latest)](https://aka.ms/vs/17/release/vc_redist.x64.exe)

After installing, restart your command prompt and try importing again.

---

## Solution 3: Clean Reinstall

```bash
# Completely remove llama-cpp-python
pip uninstall llama-cpp-python -y
pip cache purge

# Reinstall from scratch
pip install llama-cpp-python --force-reinstall --no-cache-dir
```

---

## Solution 4: Check Dependencies

Make sure you have these installed:

```bash
# Install/update pip and setuptools
python -m pip install --upgrade pip setuptools wheel

# Install dependencies
pip install numpy
```

---

## Solution 5: Use CPU-only Version Explicitly

If you don't need GPU acceleration:

```bash
pip uninstall llama-cpp-python -y

# Install without CUDA support
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

---

## Solution 6: Disable LLM Feature

**The LLM is OPTIONAL!** The system works perfectly without it.

### In the UI:
- Uncheck "🤖 Generate AI explanations" in the sidebar

### In code:
```python
config = ComparisonConfig(
    enable_llm=False  # Disable LLM
)
```

All other features (semantic comparison, requirement analysis, translation) work without LLM!

---

## Test Your Installation

After trying a fix, test with:

```bash
python -c "from llama_cpp import Llama; print('✅ LLM working!')"
```

If you see "✅ LLM working!", the issue is resolved!

---

## Check Your Setup

Run the diagnostic script:

```bash
python fix_llama_cpp.py
```

This will check your system and suggest specific fixes.

---

## GPU Requirements

If you want GPU acceleration:

1. **NVIDIA GPU required** (AMD GPUs not supported by llama-cpp-python)
2. **CUDA Toolkit installed** (11.8 or 12.1)
3. **Matching llama-cpp-python version** installed

### Check CUDA:
```bash
nvidia-smi
```

### Check PyTorch CUDA:
```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
```

---

## Still Not Working?

### Option A: Use the system without LLM
- Set `enable_llm=False` in configuration
- You'll still get:
  - ✅ Semantic comparison (95%+ accuracy)
  - ✅ Requirement analysis
  - ✅ Translation
  - ✅ All core features

### Option B: Use a different LLM provider
- Consider using OpenAI API instead
- Modify `local_llm.py` to use `openai` library
- Trade-off: Not 100% local, requires API key

### Option C: Contact support
- Open an issue on GitHub with:
  - Error message
  - Windows version
  - Python version
  - GPU info (if applicable)

---

## Why This Happens

`llama-cpp-python` is a Python wrapper around C++ code (llama.cpp). On Windows, it needs:
1. Compiled DLL files
2. Visual C++ runtime libraries
3. Proper CUDA libraries (if using GPU)

The pre-built wheels include these dependencies, which is why **Solution 1** usually works best.

---

## Performance Without LLM

**You lose:** AI-generated explanations for changes

**You keep:**
- ✅ Semantic understanding (embeddings)
- ✅ Requirement detection and tracking
- ✅ Translation capabilities
- ✅ 95%+ accuracy comparisons
- ✅ All core functionality

**Recommendation:** Start without LLM, add it later if needed!
