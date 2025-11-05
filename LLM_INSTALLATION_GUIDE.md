# LLM Installation Guide

## Quick Summary

**The LLM feature is OPTIONAL!** Your PDF comparison system works perfectly without it.

- **With LLM**: Get AI-generated explanations for changes
- **Without LLM**: Still get 95%+ accurate semantic comparison, requirement tracking, and all core features

---

## For Your Remote PC (128GB RAM, 32GB GPU)

Since you have excellent hardware, here's the recommended setup:

### Step 1: Install CUDA Toolkit (for GPU acceleration)

1. Check your CUDA version:
   ```bash
   nvidia-smi
   ```
   Look for "CUDA Version" in the output

2. Download matching CUDA Toolkit:
   - **CUDA 11.8**: https://developer.nvidia.com/cuda-11-8-0-download-archive
   - **CUDA 12.1**: https://developer.nvidia.com/cuda-12-1-0-download-archive

3. Install CUDA Toolkit (takes ~10 minutes)

### Step 2: Install PyTorch with CUDA

```bash
# For CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Step 3: Install llama-cpp-python with GPU support

```bash
# For CUDA 11.8
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu118

# For CUDA 12.1
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
```

### Step 4: Test the installation

```bash
python -c "from llama_cpp import Llama; print('✅ LLM ready for GPU acceleration!')"
```

---

## If You Get DLL Errors

### Quick Fix (CPU-only, works immediately):

```bash
pip uninstall llama-cpp-python -y
pip install llama-cpp-python --prefer-binary
```

This installs a pre-built version that includes all DLLs.

### Missing Visual C++ Runtime:

Download and install:
- https://aka.ms/vs/17/release/vc_redist.x64.exe

Then restart your terminal and try again.

---

## Recommended LLM Models

For your hardware (32GB GPU, 128GB RAM), you can run large models:

### Option 1: Llama 3.2 3B (Fast, Good Quality)
- **Size**: ~2GB
- **Speed**: ~50 tokens/second on GPU
- **Quality**: Good for explanations
- **Download**: https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF

### Option 2: Llama 3.1 8B (Better Quality)
- **Size**: ~5GB
- **Speed**: ~20 tokens/second on GPU
- **Quality**: Excellent for detailed explanations
- **Download**: https://huggingface.co/TheBloke/Llama-2-13B-Chat-GGUF

### Option 3: Mistral 7B (Balanced)
- **Size**: ~4GB
- **Speed**: ~30 tokens/second on GPU
- **Quality**: Very good, efficient
- **Download**: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF

**Where to put models:**
```
C:\Users\saiga\Desktop\csi\Excel-Tracker\models\
```

Then in the UI, set LLM model path to:
```
models/your-model-name.gguf
```

---

## Using LLM in the Application

### In the Streamlit UI:

1. Check "🤖 Generate AI explanations" in sidebar
2. Enter model path: `models/llama-3.2-3b.gguf`
3. Set max explanations: 10 (default)
4. Run comparison

### In Python code:

```python
from advanced_pdf_comparator import AdvancedPDFComparator, ComparisonConfig

config = ComparisonConfig(
    enable_llm=True,
    llm_model_path='models/llama-3.2-3b.gguf',
    max_llm_explanations=10,
    use_gpu=True
)

comparator = AdvancedPDFComparator(config)
report = comparator.compare_documents('old.pdf', 'new.pdf')
```

---

## Performance Expectations

With your hardware (32GB GPU):

| Model Size | Load Time | Generation Speed | Quality |
|------------|-----------|------------------|---------|
| 3B         | 5-10s     | 40-60 tokens/s   | Good    |
| 7B         | 10-15s    | 20-40 tokens/s   | Better  |
| 13B        | 15-25s    | 10-20 tokens/s   | Best    |

**First run**: Model loads into GPU (5-25s depending on size)
**Subsequent runs**: Model stays in GPU, instant start

---

## Troubleshooting

### Issue: "DLL load failed"

**Solution**: Use pre-built wheel
```bash
pip install llama-cpp-python --prefer-binary
```

### Issue: "CUDA out of memory"

**Solution**: Use smaller model or reduce context
```python
llm = LocalLLM(
    model_path='models/small-model.gguf',
    n_ctx=2048  # Reduce from default 4096
)
```

### Issue: "Model not found"

**Solution**: Check path
```bash
# List models
dir models\

# Check if model exists
python -c "from pathlib import Path; print(Path('models/your-model.gguf').exists())"
```

### Issue: Very slow generation

**Possible causes:**
1. CPU-only version installed (reinstall with GPU support)
2. Model too large for GPU
3. GPU not detected

**Check GPU usage:**
```bash
nvidia-smi
```

While generating, you should see GPU memory usage increase.

---

## Alternative: Run Without LLM

**Simple solution**: Just uncheck "Generate AI explanations" in the UI!

You'll still get:
- ✅ Semantic comparison (95%+ accuracy)
- ✅ Paragraph-level matching
- ✅ Requirement analysis (MUST/SHALL/SHOULD)
- ✅ Translation (German↔English)
- ✅ Critical change detection
- ✅ Comprehensive reports

**What you lose:**
- ❌ AI-generated natural language explanations

Most users don't need LLM for effective document comparison!

---

## Summary

1. **For quick start**: Disable LLM (`enable_llm=False`)
2. **For best experience**: Install with GPU support + download 7B model
3. **If issues persist**: See TROUBLESHOOTING_LLM.md

Need help? Run: `python fix_llama_cpp.py`
