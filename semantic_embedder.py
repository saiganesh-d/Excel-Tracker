"""
Semantic Embedder - Generate embeddings from text for semantic comparison

This module provides functionality to convert text into vector embeddings
that can be used for semantic similarity comparison. It uses sentence-transformers
with multilingual support.

Key Features:
- Multilingual embeddings (50+ languages)
- Batch processing for efficiency
- GPU acceleration support
- Caching for repeated texts
- Paragraph-level embedding generation

Author: Advanced PDF Comparison System
Date: 2025-10-30
"""

from typing import List, Dict, Optional, Tuple
import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("[!] numpy not available. Run: pip install numpy")
    np = None

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("[!] sentence-transformers not available. Run: pip install sentence-transformers")
    SentenceTransformer = None

try:
    from model_manager import ModelManager
except ImportError:
    # ModelManager might also have dependency issues
    ModelManager = None


@dataclass
class Embedding:
    """Container for text embedding with metadata"""
    text: str
    vector: any  # np.ndarray when available
    model_name: str
    language: str = 'unknown'
    timestamp: str = None
    text_hash: str = None

    def __post_init__(self):
        """Generate hash and timestamp if not provided"""
        if self.text_hash is None:
            self.text_hash = hashlib.sha256(self.text.encode('utf-8')).hexdigest()[:16]
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """Convert to dictionary (vector as list)"""
        data = asdict(self)
        if NUMPY_AVAILABLE and np is not None:
            data['vector'] = self.vector.tolist() if isinstance(self.vector, np.ndarray) else self.vector
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'Embedding':
        """Create from dictionary"""
        if NUMPY_AVAILABLE and np is not None:
            data['vector'] = np.array(data['vector'])
        return cls(**data)

    def similarity(self, other: 'Embedding') -> float:
        """Compute cosine similarity with another embedding"""
        return cosine_similarity(self.vector, other.vector)


def cosine_similarity(vec1, vec2) -> float:
    """
    Compute cosine similarity between two vectors

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Similarity score between 0 and 1
    """
    if not NUMPY_AVAILABLE or np is None:
        return 0.0

    # Normalize vectors
    vec1_norm = vec1 / (np.linalg.norm(vec1) + 1e-10)
    vec2_norm = vec2 / (np.linalg.norm(vec2) + 1e-10)

    # Compute dot product
    similarity = np.dot(vec1_norm, vec2_norm)

    # Ensure result is between 0 and 1
    return float(max(0.0, min(1.0, (similarity + 1) / 2)))


class EmbeddingCache:
    """
    Cache for text embeddings to avoid recomputation

    Uses in-memory dictionary for fast access. Can be extended
    to use persistent storage (SQLite, Redis, etc.)
    """

    def __init__(self):
        """Initialize empty cache"""
        self._cache: Dict[str, Embedding] = {}
        self._hits = 0
        self._misses = 0

    def get(self, text: str, model_name: str) -> Optional[Embedding]:
        """
        Get cached embedding for text

        Args:
            text: Text to look up
            model_name: Model used for embedding

        Returns:
            Cached embedding or None
        """
        cache_key = self._make_key(text, model_name)

        if cache_key in self._cache:
            self._hits += 1
            return self._cache[cache_key]

        self._misses += 1
        return None

    def set(self, embedding: Embedding, model_name: str):
        """
        Store embedding in cache

        Args:
            embedding: Embedding to cache
            model_name: Model used for embedding
        """
        cache_key = self._make_key(embedding.text, model_name)
        self._cache[cache_key] = embedding

    def _make_key(self, text: str, model_name: str) -> str:
        """Create cache key from text and model"""
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]
        return f"{model_name}:{text_hash}"

    def clear(self):
        """Clear all cached embeddings"""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def get_statistics(self) -> Dict:
        """Get cache statistics"""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0

        return {
            'size': len(self._cache),
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate_percent': round(hit_rate, 2)
        }


class SemanticEmbedder:
    """
    Generate semantic embeddings from text

    This class handles converting text into vector embeddings using
    sentence-transformers. Supports multiple languages, batch processing,
    and GPU acceleration.
    """

    def __init__(
        self,
        model_name: str = 'paraphrase-multilingual-mpnet-base-v2',
        model_manager: Optional[ModelManager] = None,
        cache_enabled: bool = True,
        use_gpu: bool = True
    ):
        """
        Initialize semantic embedder

        Args:
            model_name: Name of sentence-transformers model
            model_manager: Optional ModelManager instance
            cache_enabled: Whether to cache embeddings
            use_gpu: Whether to use GPU if available
        """
        self.model_name = model_name
        if model_manager:
            self.model_manager = model_manager
        elif ModelManager is not None:
            self.model_manager = ModelManager(use_gpu=use_gpu)
        else:
            self.model_manager = None

        self.cache = EmbeddingCache() if cache_enabled else None
        self._model = None

        print(f"[i] SemanticEmbedder initialized")
        print(f"    Model: {model_name}")
        print(f"    Cache: {'Enabled' if cache_enabled else 'Disabled'}")
        if self.model_manager:
            print(f"    GPU: {self.model_manager.gpu_available}")
        else:
            print(f"    GPU: N/A (dependencies not installed)")

    def _load_model(self):
        """Load sentence transformer model (lazy loading)"""
        if self._model is not None:
            return self._model

        if not SENTENCE_TRANSFORMERS_AVAILABLE or SentenceTransformer is None:
            print("[!] sentence-transformers not available")
            return None

        if self.model_manager is None:
            print("[!] ModelManager not available")
            return None

        try:
            print(f"[i] Loading model: {self.model_name}...")
            self._model = self.model_manager.get_embedder(self.model_name)
            print("[+] Model loaded successfully")
            return self._model
        except Exception as e:
            print(f"[-] Error loading model: {e}")
            return None

    def embed(
        self,
        text: str,
        language: str = 'unknown',
        use_cache: bool = True
    ) -> Optional[Embedding]:
        """
        Generate embedding for single text

        Args:
            text: Text to embed
            language: Language of text (for metadata)
            use_cache: Whether to use cached embedding

        Returns:
            Embedding object or None on error
        """
        # Check cache first
        if use_cache and self.cache:
            cached = self.cache.get(text, self.model_name)
            if cached:
                return cached

        # Load model
        model = self._load_model()
        if model is None:
            return None

        try:
            # Generate embedding
            vector = model.encode(text, convert_to_numpy=True, show_progress_bar=False)

            # Create embedding object
            embedding = Embedding(
                text=text,
                vector=vector,
                model_name=self.model_name,
                language=language
            )

            # Cache result
            if self.cache:
                self.cache.set(embedding, self.model_name)

            return embedding

        except Exception as e:
            print(f"[-] Error generating embedding: {e}")
            return None

    def embed_batch(
        self,
        texts: List[str],
        languages: Optional[List[str]] = None,
        batch_size: int = 32,
        show_progress: bool = False
    ) -> List[Optional[Embedding]]:
        """
        Generate embeddings for multiple texts efficiently

        Args:
            texts: List of texts to embed
            languages: Optional list of languages (same length as texts)
            batch_size: Number of texts to process at once
            show_progress: Whether to show progress bar

        Returns:
            List of Embedding objects (None for failures)
        """
        if not texts:
            return []

        # Set default languages
        if languages is None:
            languages = ['unknown'] * len(texts)

        # Check cache first
        embeddings = []
        texts_to_embed = []
        indices_to_embed = []

        for i, (text, lang) in enumerate(zip(texts, languages)):
            if self.cache:
                cached = self.cache.get(text, self.model_name)
                if cached:
                    embeddings.append(cached)
                    continue

            # Need to embed this text
            embeddings.append(None)  # Placeholder
            texts_to_embed.append(text)
            indices_to_embed.append(i)

        # If all cached, return early
        if not texts_to_embed:
            return embeddings

        # Load model
        model = self._load_model()
        if model is None:
            return [None] * len(texts)

        try:
            # Generate embeddings in batches
            print(f"[i] Embedding {len(texts_to_embed)} texts (batch_size={batch_size})...")

            vectors = model.encode(
                texts_to_embed,
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=show_progress
            )

            # Create embedding objects
            for idx, text, vector in zip(indices_to_embed, texts_to_embed, vectors):
                embedding = Embedding(
                    text=text,
                    vector=vector,
                    model_name=self.model_name,
                    language=languages[idx]
                )

                # Cache result
                if self.cache:
                    self.cache.set(embedding, self.model_name)

                # Store in results
                embeddings[idx] = embedding

            print(f"[+] Embedded {len(texts_to_embed)} texts successfully")
            return embeddings

        except Exception as e:
            print(f"[-] Error in batch embedding: {e}")
            return [None] * len(texts)

    def embed_paragraphs(
        self,
        paragraphs: List[str],
        languages: Optional[List[str]] = None,
        batch_size: int = 32
    ) -> List[Optional[Embedding]]:
        """
        Convenience method for embedding paragraphs

        Args:
            paragraphs: List of paragraph texts
            languages: Optional list of languages
            batch_size: Batch size for processing

        Returns:
            List of Embedding objects
        """
        return self.embed_batch(
            texts=paragraphs,
            languages=languages,
            batch_size=batch_size,
            show_progress=True
        )

    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute semantic similarity between two texts

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score between 0 and 1
        """
        emb1 = self.embed(text1)
        emb2 = self.embed(text2)

        if emb1 is None or emb2 is None:
            return 0.0

        return emb1.similarity(emb2)

    def compute_similarity_matrix(
        self,
        texts1: List[str],
        texts2: List[str]
    ):
        """
        Compute similarity matrix between two sets of texts

        Args:
            texts1: First set of texts
            texts2: Second set of texts

        Returns:
            Matrix of shape (len(texts1), len(texts2)) with similarity scores
        """
        # Generate embeddings
        embs1 = self.embed_batch(texts1)
        embs2 = self.embed_batch(texts2)

        # Create similarity matrix
        n1 = len(texts1)
        n2 = len(texts2)

        if NUMPY_AVAILABLE and np is not None:
            matrix = np.zeros((n1, n2))
            for i, emb1 in enumerate(embs1):
                for j, emb2 in enumerate(embs2):
                    if emb1 is not None and emb2 is not None:
                        matrix[i, j] = emb1.similarity(emb2)
        else:
            # Use list of lists if numpy not available
            matrix = [[0.0] * n2 for _ in range(n1)]
            for i, emb1 in enumerate(embs1):
                for j, emb2 in enumerate(embs2):
                    if emb1 is not None and emb2 is not None:
                        matrix[i][j] = emb1.similarity(emb2)

        return matrix

    def get_cache_statistics(self) -> Dict:
        """Get cache statistics"""
        if self.cache:
            return self.cache.get_statistics()
        return {'cache': 'disabled'}

    def clear_cache(self):
        """Clear embedding cache"""
        if self.cache:
            self.cache.clear()
            print("[+] Cache cleared")


def main():
    """Example usage and testing"""
    print("=" * 60)
    print("SEMANTIC EMBEDDER TEST")
    print("=" * 60)

    # Initialize embedder
    embedder = SemanticEmbedder(cache_enabled=True)

    # Test single embedding
    print("\n[TEST 1] Single text embedding")
    text = "This is a test sentence for semantic embedding."
    embedding = embedder.embed(text, language='en')

    if embedding:
        print(f"[+] Text: {text}")
        print(f"[+] Vector shape: {embedding.vector.shape}")
        print(f"[+] Vector norm: {np.linalg.norm(embedding.vector):.4f}")
    else:
        print("[-] Embedding failed (models not installed)")

    # Test similarity
    print("\n[TEST 2] Semantic similarity")
    text1 = "The quick brown fox jumps over the lazy dog."
    text2 = "A fast brown fox leaps over a sleepy dog."
    text3 = "Python is a programming language."

    sim12 = embedder.compute_similarity(text1, text2)
    sim13 = embedder.compute_similarity(text1, text3)

    print(f"[+] Text 1: {text1}")
    print(f"[+] Text 2: {text2}")
    print(f"[+] Similarity 1-2: {sim12:.4f} (similar)")
    print(f"[+] Text 3: {text3}")
    print(f"[+] Similarity 1-3: {sim13:.4f} (different)")

    # Test batch embedding
    print("\n[TEST 3] Batch embedding")
    texts = [
        "Machine learning is a subset of artificial intelligence.",
        "AI helps computers learn from data.",
        "The weather is nice today.",
        "I like to read books on weekends."
    ]

    embeddings = embedder.embed_batch(texts)
    successful = sum(1 for e in embeddings if e is not None)
    print(f"[+] Embedded {successful}/{len(texts)} texts")

    # Test cache
    print("\n[TEST 4] Cache performance")
    stats = embedder.get_cache_statistics()
    print(f"[+] Cache statistics: {stats}")

    # Re-embed same text (should use cache)
    embedder.embed(text1)
    embedder.embed(text2)

    stats = embedder.get_cache_statistics()
    print(f"[+] After re-embedding: {stats}")

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
