"""
ML Model Manager

Manages lifecycle of all ML models:
- Sentence transformers (embeddings)
- Translation models (Opus-MT)
- Optional LLM (Llama)

Handles loading, caching, GPU detection, and resource management.
"""

import os
from pathlib import Path
from typing import Optional, Dict
import warnings

# Suppress some model loading warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)


class ModelManager:
    """Centralized management of all ML models"""

    def __init__(self, models_dir: str = './models', use_gpu: bool = True):
        """
        Initialize model manager

        Args:
            models_dir: Directory to cache models
            use_gpu: Whether to use GPU if available
        """
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        self.use_gpu = use_gpu

        # Model instances (lazy loaded)
        self._embedder = None
        self._de_en_translator = None
        self._en_de_translator = None
        self._llm = None

        # GPU availability
        self.gpu_available = False
        self.gpu_name = None
        self.gpu_memory_gb = 0

        # Check GPU
        self._check_gpu()

    def _check_gpu(self):
        """Check if GPU is available and get info"""
        try:
            import torch
            self.gpu_available = torch.cuda.is_available()

            if self.gpu_available:
                self.gpu_name = torch.cuda.get_device_name(0)
                self.gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                print(f"[+] GPU available: {self.gpu_name} ({self.gpu_memory_gb:.1f} GB)")
            else:
                print("[i] GPU not available, using CPU")
                print("  Performance will be 5-6x slower")
                print("  Consider installing CUDA toolkit and GPU drivers")

        except Exception as e:
            print(f"[!] Could not check GPU: {e}")
            self.gpu_available = False

    def get_embedder(self, model_name: str = 'paraphrase-multilingual-mpnet-base-v2'):
        """
        Get or load sentence transformer for embeddings

        Args:
            model_name: Name of sentence-transformers model

        Returns:
            SentenceTransformer model
        """
        if self._embedder is not None:
            return self._embedder

        print(f"Loading embeddings model: {model_name}...")

        try:
            from sentence_transformers import SentenceTransformer
            import torch

            # Load model
            self._embedder = SentenceTransformer(
                model_name,
                cache_folder=str(self.models_dir)
            )

            # Move to GPU if available and requested
            if self.use_gpu and self.gpu_available:
                self._embedder = self._embedder.to('cuda')
                print(f"  [+] Model loaded on GPU")
            else:
                print(f"  [+] Model loaded on CPU")

            return self._embedder

        except ImportError:
            print("[-] sentence-transformers not installed")
            print("  Install with: pip install sentence-transformers")
            raise
        except Exception as e:
            print(f"[-] Error loading embeddings model: {e}")
            raise

    def get_translator(self, source_lang: str, target_lang: str):
        """
        Get or load translation model

        Args:
            source_lang: Source language code ('de', 'en', etc.)
            target_lang: Target language code

        Returns:
            Tuple of (model, tokenizer)
        """
        # Determine which translator to use
        lang_pair = f"{source_lang}-{target_lang}"

        # Check if already loaded
        if lang_pair == 'de-en' and self._de_en_translator is not None:
            return self._de_en_translator
        elif lang_pair == 'en-de' and self._en_de_translator is not None:
            return self._en_de_translator

        print(f"Loading translation model: {source_lang}→{target_lang}...")

        try:
            from transformers import MarianMTModel, MarianTokenizer
            import torch

            # Determine model name
            model_mapping = {
                'de-en': 'Helsinki-NLP/opus-mt-de-en',
                'en-de': 'Helsinki-NLP/opus-mt-en-de',
                'zh-en': 'Helsinki-NLP/opus-mt-zh-en',
                'en-zh': 'Helsinki-NLP/opus-mt-en-zh',
            }

            model_name = model_mapping.get(lang_pair)
            if not model_name:
                raise ValueError(f"Translation pair {lang_pair} not supported")

            # Load tokenizer and model
            tokenizer = MarianTokenizer.from_pretrained(
                model_name,
                cache_dir=str(self.models_dir)
            )

            model = MarianMTModel.from_pretrained(
                model_name,
                cache_dir=str(self.models_dir)
            )

            # Move to GPU if available
            if self.use_gpu and self.gpu_available:
                model = model.to('cuda')
                print(f"  [+] Translation model loaded on GPU")
            else:
                print(f"  [+] Translation model loaded on CPU")

            # Cache the translator
            translator = (model, tokenizer)
            if lang_pair == 'de-en':
                self._de_en_translator = translator
            elif lang_pair == 'en-de':
                self._en_de_translator = translator

            return translator

        except ImportError:
            print("[-] transformers not installed")
            print("  Install with: pip install transformers")
            raise
        except Exception as e:
            print(f"[-] Error loading translation model: {e}")
            raise

    def get_llm(self, model_name: str = 'llama-3.2-3b-instruct'):
        """
        Get or load local LLM for explanations

        Args:
            model_name: Name of LLM model

        Returns:
            LLM model instance (implementation depends on llama-cpp-python)
        """
        if self._llm is not None:
            return self._llm

        print(f"Loading LLM: {model_name}...")
        print("  Note: LLM loading not fully implemented yet")
        print("  This is optional and can be added later")

        # TODO: Implement LLM loading with llama-cpp-python
        # For now, return None (LLM is optional)
        return None

    def check_models_downloaded(self) -> Dict[str, bool]:
        """
        Check which models are already downloaded

        Returns:
            Dict mapping model types to download status
        """
        status = {}

        # Check embeddings model
        embeddings_path = self.models_dir / 'sentence-transformers' / 'paraphrase-multilingual-mpnet-base-v2'
        status['embeddings'] = embeddings_path.exists()

        # Check translation models
        de_en_path = self.models_dir / 'models--Helsinki-NLP--opus-mt-de-en'
        status['translation_de_en'] = de_en_path.exists()

        en_de_path = self.models_dir / 'models--Helsinki-NLP--opus-mt-en-de'
        status['translation_en_de'] = en_de_path.exists()

        # Check LLM (optional)
        llm_path = self.models_dir / 'llama-3.2-3b'
        status['llm'] = llm_path.exists()

        return status

    def get_model_info(self) -> Dict:
        """
        Get information about models and system

        Returns:
            Dict with model and system information
        """
        models_status = self.check_models_downloaded()

        info = {
            'gpu_available': self.gpu_available,
            'gpu_name': self.gpu_name,
            'gpu_memory_gb': self.gpu_memory_gb,
            'using_gpu': self.use_gpu and self.gpu_available,
            'models_dir': str(self.models_dir.absolute()),
            'models_downloaded': models_status,
            'embedder_loaded': self._embedder is not None,
            'translator_de_en_loaded': self._de_en_translator is not None,
            'translator_en_de_loaded': self._en_de_translator is not None,
            'llm_loaded': self._llm is not None,
        }

        return info

    def unload_all_models(self):
        """
        Unload all models to free memory

        Useful for resource cleanup or switching configurations
        """
        print("Unloading all models...")

        self._embedder = None
        self._de_en_translator = None
        self._en_de_translator = None
        self._llm = None

        # Force garbage collection
        import gc
        gc.collect()

        # Clear CUDA cache if using GPU
        if self.gpu_available:
            try:
                import torch
                torch.cuda.empty_cache()
                print("  [+] GPU cache cleared")
            except:
                pass

        print("  [+] All models unloaded")

    def estimate_memory_usage(self) -> Dict[str, float]:
        """
        Estimate memory usage of each model (in GB)

        Returns:
            Dict mapping model types to estimated memory in GB
        """
        estimates = {
            'embeddings': 0.42,  # ~420 MB
            'translation_de_en': 0.30,  # ~300 MB
            'translation_en_de': 0.30,  # ~300 MB
            'llm': 2.5,  # ~2.5 GB for 3B parameter model
        }

        # Total if all loaded
        total = sum(estimates.values())

        estimates['total_all_models'] = total

        # Typical usage (embeddings + one translation pair)
        typical = estimates['embeddings'] + estimates['translation_de_en']
        estimates['typical_usage'] = typical

        return estimates


# Example usage and testing
if __name__ == "__main__":
    print("="*70)
    print("Model Manager Testing")
    print("="*70)

    # Initialize manager
    manager = ModelManager(models_dir='./models')

    # Get system info
    print("\n" + "-"*70)
    print("System Information:")
    print("-"*70)
    info = manager.get_model_info()
    print(f"GPU Available: {info['gpu_available']}")
    if info['gpu_available']:
        print(f"GPU Name: {info['gpu_name']}")
        print(f"GPU Memory: {info['gpu_memory_gb']:.1f} GB")
    print(f"Using GPU: {info['using_gpu']}")
    print(f"Models Directory: {info['models_dir']}")

    # Check downloaded models
    print("\n" + "-"*70)
    print("Models Downloaded:")
    print("-"*70)
    for model_type, downloaded in info['models_downloaded'].items():
        status = "[+]" if downloaded else "[-]"
        print(f"{status} {model_type}")

    # Memory estimates
    print("\n" + "-"*70)
    print("Memory Usage Estimates:")
    print("-"*70)
    memory = manager.estimate_memory_usage()
    for model_type, size_gb in memory.items():
        print(f"{model_type}: {size_gb:.2f} GB")

    # Test loading models (only if they're downloaded)
    if info['models_downloaded']['embeddings']:
        print("\n" + "-"*70)
        print("Testing Model Loading:")
        print("-"*70)

        try:
            embedder = manager.get_embedder()
            print("[+] Embeddings model loaded successfully")

            # Test encoding
            test_text = "This is a test sentence."
            embedding = embedder.encode(test_text)
            print(f"  Test encoding shape: {embedding.shape}")

        except Exception as e:
            print(f"[-] Error loading embeddings: {e}")

    else:
        print("\n" + "-"*70)
        print("Models not downloaded yet")
        print("-"*70)
        print("Run: python download_models.py")

    print("\n" + "="*70)
    print("[+] Model manager testing complete!")
    print("="*70)
