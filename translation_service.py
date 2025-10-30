"""
Local Translation Service

Provides 100% local translation using Opus-MT models.
Includes caching to avoid re-translating the same content.

Supports:
- German <-> English (primary)
- Chinese -> English (future)
- Extensible to other language pairs
"""

import sqlite3
import hashlib
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import warnings

# Suppress transformers warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)


class TranslationCache:
    """SQLite-based cache for translations"""

    def __init__(self, db_path: str = 'translation_cache.db'):
        """
        Initialize translation cache

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self._init_database()

    def _init_database(self):
        """Initialize database and create tables if needed"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS translations (
                text_hash TEXT,
                source_lang TEXT,
                target_lang TEXT,
                source_text TEXT,
                translated_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (text_hash, source_lang, target_lang)
            )
        ''')
        self.conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_hash_lang
            ON translations(text_hash, source_lang, target_lang)
        ''')
        self.conn.commit()

    def _get_text_hash(self, text: str) -> str:
        """
        Get hash of text for caching

        Args:
            text: Text to hash

        Returns:
            SHA256 hash (first 32 chars)
        """
        return hashlib.sha256(text.encode('utf-8')).hexdigest()[:32]

    def get(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """
        Get cached translation if available

        Args:
            text: Source text
            source_lang: Source language code
            target_lang: Target language code

        Returns:
            Translated text if in cache, None otherwise
        """
        if not text or not text.strip():
            return None

        text_hash = self._get_text_hash(text)

        cursor = self.conn.execute(
            'SELECT translated_text FROM translations WHERE text_hash=? AND source_lang=? AND target_lang=?',
            (text_hash, source_lang, target_lang)
        )
        result = cursor.fetchone()

        if result:
            return result[0]
        return None

    def set(self, text: str, source_lang: str, target_lang: str, translation: str):
        """
        Cache a translation

        Args:
            text: Source text
            source_lang: Source language code
            target_lang: Target language code
            translation: Translated text
        """
        if not text or not translation:
            return

        text_hash = self._get_text_hash(text)

        self.conn.execute(
            'INSERT OR REPLACE INTO translations (text_hash, source_lang, target_lang, source_text, translated_text) VALUES (?, ?, ?, ?, ?)',
            (text_hash, source_lang, target_lang, text, translation)
        )
        self.conn.commit()

    def get_statistics(self) -> Dict:
        """
        Get cache statistics

        Returns:
            Dict with cache statistics
        """
        cursor = self.conn.execute('SELECT COUNT(*) FROM translations')
        total_count = cursor.fetchone()[0]

        cursor = self.conn.execute('''
            SELECT source_lang, target_lang, COUNT(*) as count
            FROM translations
            GROUP BY source_lang, target_lang
        ''')
        by_language = cursor.fetchall()

        return {
            'total_translations': total_count,
            'by_language_pair': {
                f"{row[0]}->{row[1]}": row[2]
                for row in by_language
            }
        }

    def clear(self):
        """Clear all cached translations"""
        self.conn.execute('DELETE FROM translations')
        self.conn.commit()

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


class LocalTranslator:
    """
    Local translation service using Opus-MT models
    100% local, no external APIs
    """

    def __init__(self, model_manager=None, cache_enabled: bool = True,
                 cache_db: str = 'translation_cache.db'):
        """
        Initialize local translator

        Args:
            model_manager: ModelManager instance (optional)
            cache_enabled: Whether to use caching
            cache_db: Path to cache database
        """
        self.model_manager = model_manager
        self.cache_enabled = cache_enabled

        # Initialize cache
        if cache_enabled:
            self.cache = TranslationCache(cache_db)
        else:
            self.cache = None

        # Loaded models (lazy loading)
        self._models = {}

        print("Local Translator initialized")
        if cache_enabled:
            stats = self.cache.get_statistics()
            print(f"  Cache: {stats['total_translations']} translations cached")

    def _load_model(self, source_lang: str, target_lang: str) -> Tuple:
        """
        Load translation model for language pair

        Args:
            source_lang: Source language code
            target_lang: Target language code

        Returns:
            Tuple of (model, tokenizer)
        """
        lang_pair = f"{source_lang}-{target_lang}"

        # Check if already loaded
        if lang_pair in self._models:
            return self._models[lang_pair]

        # Use model manager if available
        if self.model_manager:
            model, tokenizer = self.model_manager.get_translator(source_lang, target_lang)
            self._models[lang_pair] = (model, tokenizer)
            return model, tokenizer

        # Otherwise load directly
        print(f"Loading translation model: {source_lang}->{target_lang}...")

        try:
            from transformers import MarianMTModel, MarianTokenizer

            model_mapping = {
                'de-en': 'Helsinki-NLP/opus-mt-de-en',
                'en-de': 'Helsinki-NLP/opus-mt-en-de',
                'zh-en': 'Helsinki-NLP/opus-mt-zh-en',
            }

            model_name = model_mapping.get(lang_pair)
            if not model_name:
                raise ValueError(f"Translation pair {lang_pair} not supported")

            tokenizer = MarianTokenizer.from_pretrained(model_name)
            model = MarianMTModel.from_pretrained(model_name)

            # Move to GPU if available
            try:
                import torch
                if torch.cuda.is_available():
                    model = model.to('cuda')
                    print(f"  [+] Model loaded on GPU")
                else:
                    print(f"  [i] Model loaded on CPU")
            except:
                print(f"  [i] Model loaded on CPU")

            self._models[lang_pair] = (model, tokenizer)
            return model, tokenizer

        except ImportError:
            print("[-] transformers not installed")
            print("  Install with: pip install transformers")
            raise
        except Exception as e:
            print(f"[-] Error loading model: {e}")
            raise

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text from source to target language

        Args:
            text: Text to translate
            source_lang: Source language code (e.g., 'de', 'en')
            target_lang: Target language code

        Returns:
            Translated text
        """
        if not text or not text.strip():
            return ""

        # Check cache first
        if self.cache:
            cached = self.cache.get(text, source_lang, target_lang)
            if cached:
                return cached

        # Load model
        model, tokenizer = self._load_model(source_lang, target_lang)

        # Translate
        try:
            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)

            # Move inputs to same device as model
            if hasattr(model, 'device'):
                inputs = {k: v.to(model.device) for k, v in inputs.items()}

            outputs = model.generate(**inputs, max_length=512)
            translated = tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Cache the result
            if self.cache:
                self.cache.set(text, source_lang, target_lang, translated)

            return translated

        except Exception as e:
            print(f"[-] Translation error: {e}")
            return text  # Return original on error

    def translate_batch(self, texts: List[str], source_lang: str, target_lang: str,
                       batch_size: int = 8) -> List[str]:
        """
        Translate multiple texts efficiently

        Args:
            texts: List of texts to translate
            source_lang: Source language code
            target_lang: Target language code
            batch_size: Number of texts to process at once

        Returns:
            List of translated texts
        """
        if not texts:
            return []

        translated = []

        # Check cache for all texts first
        uncached_indices = []
        uncached_texts = []

        for i, text in enumerate(texts):
            if self.cache:
                cached = self.cache.get(text, source_lang, target_lang)
                if cached:
                    translated.append(cached)
                    continue

            uncached_indices.append(i)
            uncached_texts.append(text)

        # Translate uncached texts
        if uncached_texts:
            model, tokenizer = self._load_model(source_lang, target_lang)

            # Process in batches
            for i in range(0, len(uncached_texts), batch_size):
                batch = uncached_texts[i:i + batch_size]

                try:
                    inputs = tokenizer(batch, return_tensors="pt", padding=True,
                                     truncation=True, max_length=512)

                    # Move to device
                    if hasattr(model, 'device'):
                        inputs = {k: v.to(model.device) for k, v in inputs.items()}

                    outputs = model.generate(**inputs, max_length=512)

                    batch_translated = [
                        tokenizer.decode(output, skip_special_tokens=True)
                        for output in outputs
                    ]

                    # Cache results
                    if self.cache:
                        for orig, trans in zip(batch, batch_translated):
                            self.cache.set(orig, source_lang, target_lang, trans)

                    translated.extend(batch_translated)

                except Exception as e:
                    print(f"[-] Batch translation error: {e}")
                    # Return originals on error
                    translated.extend(batch)

        return translated

    def translate_de_to_en(self, text: str) -> str:
        """
        Translate German to English

        Args:
            text: German text

        Returns:
            English translation
        """
        return self.translate(text, 'de', 'en')

    def translate_en_to_de(self, text: str) -> str:
        """
        Translate English to German

        Args:
            text: English text

        Returns:
            German translation
        """
        return self.translate(text, 'en', 'de')

    def auto_translate(self, text: str, source_lang: str, target_lang: str = 'en') -> str:
        """
        Automatically translate to target language if needed

        Args:
            text: Text to translate
            source_lang: Detected source language
            target_lang: Target language (default: English)

        Returns:
            Translated text (or original if same language)
        """
        if source_lang == target_lang:
            return text

        return self.translate(text, source_lang, target_lang)

    def get_cache_statistics(self) -> Dict:
        """
        Get cache statistics

        Returns:
            Dict with cache statistics
        """
        if self.cache:
            return self.cache.get_statistics()
        return {'cache_enabled': False}

    def clear_cache(self):
        """Clear translation cache"""
        if self.cache:
            self.cache.clear()
            print("[+] Translation cache cleared")


# Example usage and testing
if __name__ == "__main__":
    print("="*70)
    print("Translation Service Testing")
    print("="*70)

    # Initialize translator
    translator = LocalTranslator(cache_enabled=True)

    # Test German to English
    print("\n" + "-"*70)
    print("German -> English Translation:")
    print("-"*70)

    test_de_texts = [
        "Das System muss alle Benutzer authentifizieren.",
        "Die Sicherheitsrichtlinien sind verbindlich.",
        "Alle Änderungen müssen dokumentiert werden.",
    ]

    print("\nNote: This test requires transformers library and Opus-MT models")
    print("Run 'python download_models.py' first to download models\n")

    try:
        for de_text in test_de_texts:
            print(f"DE: {de_text}")
            en_text = translator.translate_de_to_en(de_text)
            print(f"EN: {en_text}")
            print()

        # Test caching
        print("-"*70)
        print("Testing Cache:")
        print("-"*70)

        # Translate again (should use cache)
        cached_text = translator.translate_de_to_en(test_de_texts[0])
        print(f"Cached translation: {cached_text}")

        # Show statistics
        stats = translator.get_cache_statistics()
        print(f"\nCache statistics:")
        print(f"  Total cached: {stats['total_translations']}")
        if 'by_language_pair' in stats:
            for pair, count in stats['by_language_pair'].items():
                print(f"  {pair}: {count}")

    except Exception as e:
        print(f"Error: {e}")
        print("\nTo use translation, ensure:")
        print("1. transformers is installed: pip install transformers")
        print("2. torch is installed: pip install torch")
        print("3. Models are downloaded: python download_models.py")

    print("\n" + "="*70)
    print("[+] Translation service testing complete!")
    print("="*70)
