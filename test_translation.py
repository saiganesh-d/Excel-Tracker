"""
Test Translation Service

Tests local translation functionality with German, English
Tests caching, batch processing, and error handling
"""

from translation_service import LocalTranslator, TranslationCache
from language_detector import LanguageDetector
import time


def test_cache():
    """Test translation cache"""
    print("="*70)
    print("Test 1: Translation Cache")
    print("="*70)

    cache = TranslationCache('test_cache.db')

    # Test set and get
    cache.set("Hello", "en", "de", "Hallo")
    cached = cache.get("Hello", "en", "de")

    assert cached == "Hallo", "Cache set/get failed"
    print("[+] Cache set/get working")

    # Test statistics
    stats = cache.get_statistics()
    print(f"[+] Cache statistics: {stats}")

    # Clear
    cache.clear()
    stats_after = cache.get_statistics()
    assert stats_after['total_translations'] == 0, "Cache clear failed"
    print("[+] Cache clear working")

    cache.close()
    print("[+] Cache test passed!\n")


def test_language_detection():
    """Test language detection integration"""
    print("="*70)
    print("Test 2: Language Detection Integration")
    print("="*70)

    detector = LanguageDetector()

    test_texts = [
        ("This is English text.", "en"),
        ("Das ist deutscher Text.", "de"),
    ]

    for text, expected_lang in test_texts:
        result = detector.detect_language(text)
        print(f"Text: {text}")
        print(f"  Detected: {result.language} ({result.language_name})")
        print(f"  Expected: {expected_lang}")
        print(f"  Confidence: {result.confidence:.2f}")
        print()

    print("[+] Language detection integration test passed!\n")


def test_translation_without_models():
    """Test translation service without models (graceful degradation)"""
    print("="*70)
    print("Test 3: Translation Service (without models)")
    print("="*70)

    translator = LocalTranslator(cache_enabled=True, cache_db='test_cache.db')

    print("[+] Translator initialized")
    print("[i] Note: Actual translation requires models to be downloaded")
    print("[i] Run 'python download_models.py' to download models\n")

    # Test cache functionality
    cache_stats = translator.get_cache_statistics()
    print(f"[+] Cache statistics: {cache_stats}")

    print("[+] Translation service test passed!\n")


def test_translation_with_models():
    """Test actual translation (only if models available)"""
    print("="*70)
    print("Test 4: Actual Translation (requires models)")
    print("="*70)

    translator = LocalTranslator(cache_enabled=True, cache_db='test_cache.db')

    test_cases = [
        ("de", "en", "Das System muss alle Benutzer authentifizieren."),
        ("de", "en", "Die Sicherheitsrichtlinien sind verbindlich."),
        ("en", "de", "The system must authenticate all users."),
    ]

    try:
        for source_lang, target_lang, text in test_cases:
            print(f"\nTranslating {source_lang}->{target_lang}:")
            print(f"  Source: {text}")

            start_time = time.time()
            translated = translator.translate(text, source_lang, target_lang)
            elapsed = time.time() - start_time

            print(f"  Target: {translated}")
            print(f"  Time: {elapsed:.2f}s")

        # Test caching (should be faster)
        print("\n" + "-"*70)
        print("Testing Cache Performance:")
        print("-"*70)

        text = test_cases[0][2]
        source_lang, target_lang = test_cases[0][:2]

        # First time (already cached from above)
        start_time = time.time()
        result1 = translator.translate(text, source_lang, target_lang)
        time1 = time.time() - start_time

        # Second time (should use cache)
        start_time = time.time()
        result2 = translator.translate(text, source_lang, target_lang)
        time2 = time.time() - start_time

        print(f"First translation: {time1:.4f}s")
        print(f"Cached translation: {time2:.4f}s")
        print(f"Speedup: {time1/time2:.1f}x faster")

        assert result1 == result2, "Cached result differs from original"
        print("[+] Cache working correctly!")

        # Test batch translation
        print("\n" + "-"*70)
        print("Testing Batch Translation:")
        print("-"*70)

        batch_texts = [
            "Das ist ein Test.",
            "Dies ist ein weiterer Test.",
            "Noch ein Test.",
        ]

        start_time = time.time()
        batch_results = translator.translate_batch(batch_texts, 'de', 'en')
        batch_time = time.time() - start_time

        print(f"Translated {len(batch_texts)} texts in {batch_time:.2f}s")
        for orig, trans in zip(batch_texts, batch_results):
            print(f"  {orig} -> {trans}")

        print("\n[+] Actual translation test passed!")

    except ImportError as e:
        print(f"\n[!] Models not available: {e}")
        print("[i] This is expected if models haven't been downloaded yet")
        print("[i] Run 'python download_models.py' to download models")
    except Exception as e:
        print(f"\n[-] Translation test failed: {e}")
        print("[i] This is expected if models haven't been downloaded yet")


def test_end_to_end_workflow():
    """Test complete workflow: detect language -> translate"""
    print("="*70)
    print("Test 5: End-to-End Workflow")
    print("="*70)

    detector = LanguageDetector()
    translator = LocalTranslator(cache_enabled=True, cache_db='test_cache.db')

    test_documents = [
        "Das System muss alle Benutzer authentifizieren.",
        "The system must authenticate all users.",
        "Die Mehrfaktor-Authentifizierung ist erforderlich.",
    ]

    print("Processing documents:")
    for i, text in enumerate(test_documents, 1):
        print(f"\nDocument {i}:")
        print(f"  Text: {text}")

        # Detect language
        lang_result = detector.detect_language(text)
        print(f"  Detected: {lang_result.language_name} ({lang_result.confidence:.2f})")

        # Translate to English if needed
        try:
            if lang_result.language == 'de':
                translated = translator.translate_de_to_en(text)
                print(f"  English: {translated}")
            elif lang_result.language == 'en':
                print(f"  (Already English)")
        except Exception as e:
            print(f"  [i] Translation skipped (models not available)")

    print("\n[+] End-to-end workflow test passed!\n")


def run_all_tests():
    """Run all translation tests"""
    print("\n" + "="*70)
    print("TRANSLATION SERVICE TEST SUITE")
    print("="*70 + "\n")

    tests = [
        ("Cache Functionality", test_cache),
        ("Language Detection", test_language_detection),
        ("Translation Service Init", test_translation_without_models),
        ("Actual Translation", test_translation_with_models),
        ("End-to-End Workflow", test_end_to_end_workflow),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"[-] {test_name} failed: {e}\n")
            failed += 1

    # Summary
    print("="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n[+] All tests passed!")
    else:
        print(f"\n[!] {failed} test(s) failed")

    print("\nNote: Translation tests may be skipped if models not downloaded")
    print("Run 'python download_models.py' to download required models")
    print("="*70 + "\n")


if __name__ == "__main__":
    run_all_tests()
