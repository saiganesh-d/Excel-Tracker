"""
Language Detection for Multilingual Document Comparison

Detects language of paragraphs/documents to enable proper translation
and semantic comparison.

Supports: German (de), English (en), Chinese (zh), and 50+ more languages
"""

from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class LanguageResult:
    """Result of language detection"""
    language: str  # ISO 639-1 code (e.g., 'en', 'de', 'zh')
    confidence: float  # 0.0 to 1.0
    language_name: str  # Human-readable name


class LanguageDetector:
    """Detect language of text using langdetect library"""

    # Supported languages for our application
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'de': 'German',
        'zh-cn': 'Chinese (Simplified)',
        'zh-tw': 'Chinese (Traditional)',
        'fr': 'French',
        'es': 'Spanish',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'ja': 'Japanese',
        'ko': 'Korean',
    }

    # Primary languages for this project
    PRIMARY_LANGUAGES = ['en', 'de', 'zh-cn']

    def __init__(self):
        """Initialize language detector"""
        try:
            import langdetect
            from langdetect import detect, detect_langs, DetectorFactory
            # Set seed for consistent results
            DetectorFactory.seed = 0
            self.langdetect = langdetect
            self.detect = detect
            self.detect_langs = detect_langs
            self.available = True
        except ImportError:
            print("Warning: langdetect not installed. Language detection disabled.")
            print("Install with: pip install langdetect")
            self.available = False

    def detect_language(self, text: str) -> LanguageResult:
        """
        Detect language of a single text

        Args:
            text: Text to analyze

        Returns:
            LanguageResult with detected language and confidence
        """
        if not self.available:
            # Fallback to English if langdetect not available
            return LanguageResult(
                language='en',
                confidence=0.5,
                language_name='English (default)'
            )

        if not text or len(text.strip()) < 3:
            # Too short to reliably detect
            return LanguageResult(
                language='en',
                confidence=0.0,
                language_name='Unknown (text too short)'
            )

        try:
            # Get language with confidence scores
            langs = self.detect_langs(text)

            if not langs:
                # Default to English
                return LanguageResult(
                    language='en',
                    confidence=0.0,
                    language_name='English (default)'
                )

            # Get most likely language
            top_lang = langs[0]
            lang_code = top_lang.lang
            confidence = top_lang.prob

            # Normalize Chinese variants
            if lang_code == 'zh-cn' or lang_code == 'zh-tw':
                lang_code = 'zh-cn'  # Treat both as Chinese for our purposes

            # Get human-readable name
            lang_name = self.SUPPORTED_LANGUAGES.get(
                lang_code,
                f"{lang_code.upper()} (detected)"
            )

            return LanguageResult(
                language=lang_code,
                confidence=confidence,
                language_name=lang_name
            )

        except Exception as e:
            print(f"Language detection error: {e}")
            # Default to English on error
            return LanguageResult(
                language='en',
                confidence=0.0,
                language_name='English (error fallback)'
            )

    def detect_document_language(self, paragraphs: List[str],
                                 sample_size: int = 5) -> LanguageResult:
        """
        Detect primary language of a document

        Samples first few paragraphs for efficiency

        Args:
            paragraphs: List of paragraph texts
            sample_size: Number of paragraphs to sample

        Returns:
            LanguageResult for document's primary language
        """
        if not paragraphs:
            return LanguageResult(
                language='en',
                confidence=0.0,
                language_name='English (no content)'
            )

        # Sample paragraphs (first few usually representative)
        sample_paras = paragraphs[:min(sample_size, len(paragraphs))]

        # Combine sampled paragraphs
        sample_text = ' '.join(sample_paras)

        # Detect language
        result = self.detect_language(sample_text)

        return result

    def detect_per_paragraph(self, paragraphs: List[str]) -> List[Dict]:
        """
        Detect language for each paragraph individually

        Useful for mixed-language documents

        Args:
            paragraphs: List of paragraph texts

        Returns:
            List of dicts with 'text', 'language', 'confidence'
        """
        results = []

        for para in paragraphs:
            lang_result = self.detect_language(para)

            results.append({
                'text': para,
                'language': lang_result.language,
                'confidence': lang_result.confidence,
                'language_name': lang_result.language_name
            })

        return results

    def is_supported(self, language_code: str) -> bool:
        """
        Check if a language is supported by our translation system

        Args:
            language_code: ISO 639-1 language code

        Returns:
            True if language is supported
        """
        return language_code in self.SUPPORTED_LANGUAGES

    def is_primary_language(self, language_code: str) -> bool:
        """
        Check if language is one of our primary supported languages
        (English, German, Chinese)

        Args:
            language_code: ISO 639-1 language code

        Returns:
            True if primary language
        """
        return language_code in self.PRIMARY_LANGUAGES

    def get_language_statistics(self, paragraphs: List[str]) -> Dict:
        """
        Get statistics about languages in a document

        Args:
            paragraphs: List of paragraph texts

        Returns:
            Dict with language distribution and statistics
        """
        if not paragraphs:
            return {
                'primary_language': 'en',
                'language_counts': {},
                'is_multilingual': False,
                'total_paragraphs': 0
            }

        # Detect language for each paragraph
        para_results = self.detect_per_paragraph(paragraphs)

        # Count languages
        language_counts = {}
        for result in para_results:
            lang = result['language']
            language_counts[lang] = language_counts.get(lang, 0) + 1

        # Determine primary language (most common)
        primary_lang = max(language_counts.items(), key=lambda x: x[1])[0]

        # Check if multilingual (more than one language with >10% presence)
        total_paras = len(paragraphs)
        significant_langs = [
            lang for lang, count in language_counts.items()
            if count / total_paras > 0.1
        ]
        is_multilingual = len(significant_langs) > 1

        return {
            'primary_language': primary_lang,
            'primary_language_name': self.SUPPORTED_LANGUAGES.get(
                primary_lang,
                f"{primary_lang.upper()}"
            ),
            'language_counts': language_counts,
            'language_percentages': {
                lang: (count / total_paras * 100)
                for lang, count in language_counts.items()
            },
            'is_multilingual': is_multilingual,
            'total_paragraphs': total_paras,
            'languages_present': len(language_counts)
        }

    def needs_translation(self, source_lang: str,
                         target_lang: str = 'en') -> bool:
        """
        Check if translation is needed

        Args:
            source_lang: Source language code
            target_lang: Target language code (default: English)

        Returns:
            True if translation needed
        """
        # Normalize
        source_lang = source_lang.lower()
        target_lang = target_lang.lower()

        # Same language, no translation needed
        if source_lang == target_lang:
            return False

        # Chinese variants both go to Chinese
        if source_lang in ['zh-cn', 'zh-tw'] and target_lang in ['zh-cn', 'zh-tw']:
            return False

        return True


# Example usage and testing
if __name__ == "__main__":
    detector = LanguageDetector()

    print("="*70)
    print("Language Detection Testing")
    print("="*70)

    if not detector.available:
        print("\n[!] langdetect not available")
        print("Install with: pip install langdetect")
        print("\nContinuing with default (English) mode...")

    # Test samples
    test_samples = [
        ("This is a test document in English.", "English"),
        ("Dies ist ein Testdokument auf Deutsch.", "German"),
        ("Das System muss alle Benutzer authentifizieren.", "German"),
        ("The system must authenticate all users.", "English"),
        ("这是一个中文测试文档。", "Chinese"),
    ]

    print("\n" + "-"*70)
    print("Single Text Detection:")
    print("-"*70)

    for text, expected in test_samples:
        result = detector.detect_language(text)
        print(f"\nText: {text[:50]}...")
        print(f"  Detected: {result.language_name}")
        print(f"  Code: {result.language}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Expected: {expected}")

    # Test document detection
    print("\n" + "-"*70)
    print("Document Language Detection:")
    print("-"*70)

    doc_paragraphs = [
        "The system must authenticate all users before granting access.",
        "Multi-factor authentication is required for privileged accounts.",
        "All security events shall be logged and monitored.",
        "Encryption must be applied to sensitive data at rest and in transit."
    ]

    doc_result = detector.detect_document_language(doc_paragraphs)
    print(f"\nDocument language: {doc_result.language_name}")
    print(f"Confidence: {doc_result.confidence:.2f}")

    # Test statistics
    print("\n" + "-"*70)
    print("Language Statistics:")
    print("-"*70)

    stats = detector.get_language_statistics(doc_paragraphs)
    print(f"\nPrimary language: {stats['primary_language_name']}")
    print(f"Total paragraphs: {stats['total_paragraphs']}")
    print(f"Languages present: {stats['languages_present']}")
    print(f"Multilingual: {stats['is_multilingual']}")

    # Test translation need
    print("\n" + "-"*70)
    print("Translation Requirement:")
    print("-"*70)

    test_pairs = [
        ('en', 'en'),
        ('de', 'en'),
        ('en', 'de'),
        ('zh-cn', 'en'),
    ]

    for source, target in test_pairs:
        needs = detector.needs_translation(source, target)
        print(f"{source} → {target}: {'Translation needed' if needs else 'No translation needed'}")

    print("\n" + "="*70)
    print("[+] Language detection testing complete!")
    print("="*70)
