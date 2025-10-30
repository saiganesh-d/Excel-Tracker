"""
Model Download Script
Downloads all required models for the Document Comparison Suite

Run this once after installing requirements.txt
Models are cached locally and don't need re-downloading
"""

import os
import sys
from pathlib import Path


def download_models():
    """Download all required models"""

    print("="*70)
    print("Document Comparison Suite - Model Download")
    print("="*70)
    print()
    print("This will download ~5GB of models (one-time only)")
    print("Models will be cached in: ./models/")
    print()
    print("Models to download:")
    print("  1. Multilingual Embeddings (~420MB)")
    print("  2. German→English Translation (~300MB)")
    print("  3. English→German Translation (~300MB)")
    print("  4. Optional: Local LLM (~2-4GB)")
    print()

    # Create models directory
    models_dir = Path('./models')
    models_dir.mkdir(exist_ok=True)

    print("="*70)
    print("Step 1/4: Downloading Multilingual Embeddings")
    print("="*70)
    try:
        from sentence_transformers import SentenceTransformer
        print("Loading paraphrase-multilingual-mpnet-base-v2...")
        model = SentenceTransformer(
            'paraphrase-multilingual-mpnet-base-v2',
            cache_folder=str(models_dir)
        )
        print("✓ Multilingual embeddings downloaded successfully!")
        print(f"  Model supports {len(model.tokenizer.vocab)} tokens")
        print()
    except Exception as e:
        print(f"✗ Error downloading multilingual embeddings: {e}")
        print("  Please check your internet connection and try again")
        return False

    print("="*70)
    print("Step 2/4: Downloading German→English Translation")
    print("="*70)
    try:
        from transformers import MarianMTModel, MarianTokenizer
        print("Loading Helsinki-NLP/opus-mt-de-en...")
        model_name = 'Helsinki-NLP/opus-mt-de-en'
        tokenizer = MarianTokenizer.from_pretrained(
            model_name,
            cache_dir=str(models_dir)
        )
        model = MarianMTModel.from_pretrained(
            model_name,
            cache_dir=str(models_dir)
        )
        print("✓ German→English translation model downloaded successfully!")
        print()
    except Exception as e:
        print(f"✗ Error downloading German→English model: {e}")
        print("  Please check your internet connection and try again")
        return False

    print("="*70)
    print("Step 3/4: Downloading English→German Translation")
    print("="*70)
    try:
        from transformers import MarianMTModel, MarianTokenizer
        print("Loading Helsinki-NLP/opus-mt-en-de...")
        model_name = 'Helsinki-NLP/opus-mt-en-de'
        tokenizer = MarianTokenizer.from_pretrained(
            model_name,
            cache_dir=str(models_dir)
        )
        model = MarianMTModel.from_pretrained(
            model_name,
            cache_dir=str(models_dir)
        )
        print("✓ English→German translation model downloaded successfully!")
        print()
    except Exception as e:
        print(f"✗ Error downloading English→German model: {e}")
        print("  Please check your internet connection and try again")
        return False

    print("="*70)
    print("Step 4/4: Optional Local LLM")
    print("="*70)
    print("Local LLM is optional and adds ~2-4GB")
    print("It provides natural language explanations for semantic differences")
    print()
    response = input("Download local LLM? (y/n): ").lower().strip()

    if response == 'y':
        print("\nDownloading Llama-3.2-3B-Instruct...")
        print("This is a large download (~2-4GB), please be patient...")
        try:
            # Note: Actual implementation depends on llama-cpp-python setup
            # For now, we'll skip the actual download
            print("ℹ LLM download not implemented yet in this script")
            print("  You can download it manually later if needed")
            print()
        except Exception as e:
            print(f"✗ Error downloading LLM: {e}")
            print("  Continuing without LLM (can add later)")
            print()
    else:
        print("Skipping LLM download (can add later)")
        print()

    print("="*70)
    print("✅ Model Download Complete!")
    print("="*70)
    print()
    print("Downloaded models:")
    print(f"  Location: {models_dir.absolute()}")
    print(f"  Total size: ~{get_dir_size(models_dir):.1f} MB")
    print()
    print("Next steps:")
    print("  1. Run: python test_installation.py")
    print("  2. Then: streamlit run app.py")
    print()

    return True


def get_dir_size(path):
    """Calculate directory size in MB"""
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    except Exception:
        pass
    return total / (1024 * 1024)  # Convert to MB


def check_dependencies():
    """Check if required packages are installed"""
    print("Checking dependencies...")
    print()

    required_packages = [
        ('torch', 'PyTorch'),
        ('transformers', 'Transformers'),
        ('sentence_transformers', 'Sentence Transformers'),
    ]

    all_installed = True

    for package, name in required_packages:
        try:
            __import__(package)
            print(f"✓ {name} installed")
        except ImportError:
            print(f"✗ {name} NOT installed")
            all_installed = False

    print()

    if not all_installed:
        print("="*70)
        print("Missing dependencies!")
        print("="*70)
        print()
        print("Please install requirements first:")
        print()
        print("  1. Install PyTorch with CUDA:")
        print("     pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
        print()
        print("  2. Install other requirements:")
        print("     pip install -r requirements.txt")
        print()
        return False

    # Check CUDA
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✓ CUDA available: {torch.version.cuda}")
            print(f"✓ GPU: {torch.cuda.get_device_name(0)}")
            print(f"✓ GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        else:
            print("⚠ CUDA not available - will use CPU (slower)")
            print("  Consider installing CUDA toolkit and GPU drivers")
    except Exception as e:
        print(f"⚠ Could not check CUDA: {e}")

    print()
    return True


if __name__ == "__main__":
    print()

    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)

    print("="*70)
    print()

    # Download models
    success = download_models()

    if success:
        print("="*70)
        print("🎉 Setup Complete!")
        print("="*70)
        sys.exit(0)
    else:
        print("="*70)
        print("❌ Setup Failed")
        print("="*70)
        print("Please check errors above and try again")
        sys.exit(1)
