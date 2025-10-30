"""
Test Suite for Advanced PDF Comparator

Integration tests for advanced_pdf_comparator.py including full workflow
testing, component integration, and end-to-end comparison.

Author: Advanced PDF Comparison System
Date: 2025-10-30
"""

import sys

# Test counters
tests_passed = 0
tests_failed = 0


def test_header(name: str):
    """Print test header"""
    print("\n" + "=" * 60)
    print(f"TEST: {name}")
    print("=" * 60)


def assert_true(condition: bool, message: str):
    """Assert condition is true"""
    global tests_passed, tests_failed
    if condition:
        print(f"[+] PASS: {message}")
        tests_passed += 1
    else:
        print(f"[-] FAIL: {message}")
        tests_failed += 1


def assert_equals(actual, expected, message: str):
    """Assert values are equal"""
    global tests_passed, tests_failed
    if actual == expected:
        print(f"[+] PASS: {message}")
        tests_passed += 1
    else:
        print(f"[-] FAIL: {message}")
        print(f"    Expected: {expected}")
        print(f"    Actual: {actual}")
        tests_failed += 1


def test_imports():
    """Test 1: Import comparator"""
    test_header("Comparator Imports")

    try:
        from advanced_pdf_comparator import (
            AdvancedPDFComparator, ComparisonConfig,
            DocumentInfo, ComparisonReport
        )
        assert_true(True, "All imports successful")
        return True
    except Exception as e:
        assert_true(False, f"Import failed: {e}")
        return False


def test_config_creation():
    """Test 2: Create comparison configuration"""
    test_header("Configuration Creation")

    try:
        from advanced_pdf_comparator import ComparisonConfig

        config = ComparisonConfig(
            enable_translation=True,
            enable_requirements=True,
            enable_llm=False,
            similarity_threshold=0.75
        )

        assert_true(config is not None, "Config created")
        assert_true(config.enable_translation, "Translation enabled")
        assert_true(config.enable_requirements, "Requirements enabled")
        assert_true(not config.enable_llm, "LLM disabled")
        assert_equals(config.similarity_threshold, 0.75, "Similarity threshold correct")

        return True

    except Exception as e:
        assert_true(False, f"Config creation failed: {e}")
        return False


def test_comparator_initialization():
    """Test 3: Initialize comparator"""
    test_header("Comparator Initialization")

    try:
        from advanced_pdf_comparator import AdvancedPDFComparator, ComparisonConfig

        config = ComparisonConfig(
            enable_translation=False,  # Disable for speed
            enable_requirements=True,
            enable_llm=False
        )

        comparator = AdvancedPDFComparator(config)

        assert_true(comparator is not None, "Comparator initialized")
        assert_true(hasattr(comparator, 'paragraph_extractor'), "Has paragraph extractor")
        assert_true(hasattr(comparator, 'language_detector'), "Has language detector")
        assert_true(hasattr(comparator, 'embedder'), "Has embedder")
        assert_true(hasattr(comparator, 'comparator'), "Has comparator")
        assert_true(hasattr(comparator, 'requirement_analyzer'), "Has requirement analyzer")

        return True

    except Exception as e:
        assert_true(False, f"Comparator initialization failed: {e}")
        return False


def test_text_comparison():
    """Test 4: Compare text strings"""
    test_header("Text Comparison")

    try:
        from advanced_pdf_comparator import AdvancedPDFComparator, ComparisonConfig

        config = ComparisonConfig(
            enable_translation=False,
            enable_requirements=True,
            enable_llm=False
        )

        comparator = AdvancedPDFComparator(config)

        old_text = """
        The system must authenticate users.
        Data shall be encrypted.
        """

        new_text = """
        The system must verify users.
        Data shall be encrypted using AES-256.
        """

        report = comparator.compare_texts(old_text, new_text)

        assert_true(report is not None, "Report generated")
        assert_true(hasattr(report, 'comparison_result'), "Has comparison result")
        assert_true(hasattr(report, 'old_doc_info'), "Has old doc info")
        assert_true(hasattr(report, 'new_doc_info'), "Has new doc info")

        print(f"[i] Processing time: {report.processing_time:.2f}s")

        return True

    except Exception as e:
        assert_true(False, f"Text comparison failed: {e}")
        return False


def test_document_info():
    """Test 5: Document info structure"""
    test_header("Document Info")

    try:
        from advanced_pdf_comparator import AdvancedPDFComparator, ComparisonConfig

        config = ComparisonConfig(enable_translation=False, enable_llm=False)
        comparator = AdvancedPDFComparator(config)

        text = "The system must authenticate all users before access."
        report = comparator.compare_texts(text, text)

        doc_info = report.old_doc_info

        assert_true(hasattr(doc_info, 'language'), "Has language")
        assert_true(hasattr(doc_info, 'paragraph_count'), "Has paragraph count")
        assert_true(hasattr(doc_info, 'character_count'), "Has character count")

        print(f"[i] Language: {doc_info.language}")
        print(f"[i] Paragraphs: {doc_info.paragraph_count}")
        print(f"[i] Characters: {doc_info.character_count}")

        return True

    except Exception as e:
        assert_true(False, f"Document info test failed: {e}")
        return False


def test_comparison_result():
    """Test 6: Comparison result structure"""
    test_header("Comparison Result")

    try:
        from advanced_pdf_comparator import AdvancedPDFComparator, ComparisonConfig

        config = ComparisonConfig(enable_translation=False, enable_llm=False)
        comparator = AdvancedPDFComparator(config)

        old_text = "Original text."
        new_text = "Modified text."

        report = comparator.compare_texts(old_text, new_text)

        result = report.comparison_result

        assert_true('summary' in result, "Has summary")
        assert_true('matches' in result, "Has matches")

        summary = result['summary']
        assert_true('total_old' in summary, "Summary has total_old")
        assert_true('total_new' in summary, "Summary has total_new")
        assert_true('unchanged' in summary, "Summary has unchanged")
        assert_true('modified' in summary, "Summary has modified")
        assert_true('added' in summary, "Summary has added")
        assert_true('deleted' in summary, "Summary has deleted")

        print(f"[i] Summary: {summary}")

        return True

    except Exception as e:
        assert_true(False, f"Comparison result test failed: {e}")
        return False


def test_requirement_detection():
    """Test 7: Requirement detection in comparison"""
    test_header("Requirement Detection")

    try:
        from advanced_pdf_comparator import AdvancedPDFComparator, ComparisonConfig

        config = ComparisonConfig(
            enable_translation=False,
            enable_requirements=True,
            enable_llm=False
        )

        comparator = AdvancedPDFComparator(config)

        old_text = "The system should authenticate users."
        new_text = "The system must authenticate users."

        report = comparator.compare_texts(old_text, new_text)

        req_changes = report.requirement_changes

        assert_true(isinstance(req_changes, list), "Requirement changes is a list")
        print(f"[i] Requirement changes: {len(req_changes)}")

        if req_changes:
            first_change = req_changes[0]
            assert_true('change_type' in first_change, "Has change_type")
            print(f"[i] First change type: {first_change.get('change_type')}")

        return True

    except Exception as e:
        assert_true(False, f"Requirement detection failed: {e}")
        return False


def test_report_serialization():
    """Test 8: Report to dict conversion"""
    test_header("Report Serialization")

    try:
        from advanced_pdf_comparator import AdvancedPDFComparator, ComparisonConfig

        config = ComparisonConfig(enable_translation=False, enable_llm=False)
        comparator = AdvancedPDFComparator(config)

        text = "Test text for serialization."
        report = comparator.compare_texts(text, text)

        report_dict = report.to_dict()

        assert_true(isinstance(report_dict, dict), "Report converted to dict")
        assert_true('timestamp' in report_dict, "Has timestamp")
        assert_true('processing_time' in report_dict, "Has processing time")
        assert_true('old_document' in report_dict, "Has old_document")
        assert_true('new_document' in report_dict, "Has new_document")
        assert_true('comparison' in report_dict, "Has comparison")
        assert_true('config' in report_dict, "Has config")

        print(f"[i] Report keys: {list(report_dict.keys())}")

        return True

    except Exception as e:
        assert_true(False, f"Report serialization failed: {e}")
        return False


def test_multi_paragraph_comparison():
    """Test 9: Multi-paragraph comparison"""
    test_header("Multi-paragraph Comparison")

    try:
        from advanced_pdf_comparator import AdvancedPDFComparator, ComparisonConfig

        config = ComparisonConfig(enable_translation=False, enable_llm=False)
        comparator = AdvancedPDFComparator(config)

        old_text = """
        First paragraph stays the same.
        Second paragraph will be modified.
        Third paragraph will be deleted.
        """

        new_text = """
        First paragraph stays the same.
        Second paragraph has been changed.
        Fourth paragraph is newly added.
        """

        report = comparator.compare_texts(old_text, new_text)

        summary = report.comparison_result['summary']

        print(f"[i] Unchanged: {summary['unchanged']}")
        print(f"[i] Modified: {summary['modified']}")
        print(f"[i] Added: {summary['added']}")
        print(f"[i] Deleted: {summary['deleted']}")

        total_changes = (summary['unchanged'] + summary['modified'] +
                        summary['added'] + summary['deleted'])

        assert_true(total_changes > 0, f"Detected {total_changes} total changes")

        return True

    except Exception as e:
        assert_true(False, f"Multi-paragraph comparison failed: {e}")
        return False


def test_language_detection_integration():
    """Test 10: Language detection in workflow"""
    test_header("Language Detection Integration")

    try:
        from advanced_pdf_comparator import AdvancedPDFComparator, ComparisonConfig

        config = ComparisonConfig(enable_translation=False, enable_llm=False)
        comparator = AdvancedPDFComparator(config)

        english_text = "The system must be secure."
        report = comparator.compare_texts(english_text, english_text)

        language = report.old_doc_info.language

        print(f"[i] Detected language: {language}")

        assert_true(language is not None, "Language detected")
        assert_true(len(language) > 0, "Language has value")

        return True

    except Exception as e:
        assert_true(False, f"Language detection integration failed: {e}")
        return False


def test_processing_time():
    """Test 11: Processing time tracking"""
    test_header("Processing Time")

    try:
        from advanced_pdf_comparator import AdvancedPDFComparator, ComparisonConfig

        config = ComparisonConfig(enable_translation=False, enable_llm=False)
        comparator = AdvancedPDFComparator(config)

        text = "The system must authenticate users."
        report = comparator.compare_texts(text, text)

        processing_time = report.processing_time

        assert_true(processing_time > 0, f"Processing time tracked: {processing_time:.2f}s")
        assert_true(processing_time < 60, "Processing completed in reasonable time")

        return True

    except Exception as e:
        assert_true(False, f"Processing time test failed: {e}")
        return False


def test_config_in_report():
    """Test 12: Config stored in report"""
    test_header("Config in Report")

    try:
        from advanced_pdf_comparator import AdvancedPDFComparator, ComparisonConfig

        config = ComparisonConfig(
            enable_translation=True,
            enable_requirements=False,
            similarity_threshold=0.8
        )

        comparator = AdvancedPDFComparator(config)

        text = "Test text."
        report = comparator.compare_texts(text, text)

        report_dict = report.to_dict()
        config_data = report_dict['config']

        assert_true('translation' in config_data, "Config has translation setting")
        assert_true('requirements' in config_data, "Config has requirements setting")
        assert_true('similarity_threshold' in config_data, "Config has threshold")

        assert_equals(config_data['translation'], True, "Translation setting preserved")
        assert_equals(config_data['requirements'], False, "Requirements setting preserved")

        print(f"[i] Config in report: {config_data}")

        return True

    except Exception as e:
        assert_true(False, f"Config in report test failed: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("ADVANCED PDF COMPARATOR TEST SUITE")
    print("=" * 60)

    # Run tests
    tests = [
        test_imports,
        test_config_creation,
        test_comparator_initialization,
        test_text_comparison,
        test_document_info,
        test_comparison_result,
        test_requirement_detection,
        test_report_serialization,
        test_multi_paragraph_comparison,
        test_language_detection_integration,
        test_processing_time,
        test_config_in_report
    ]

    for test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"\n[-] EXCEPTION in {test_func.__name__}: {e}")
            global tests_failed
            tests_failed += 1

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    total_tests = tests_passed + tests_failed
    print(f"Total assertions: {total_tests}")
    print(f"Passed: {tests_passed}/{total_tests}")
    print(f"Failed: {tests_failed}/{total_tests}")

    if tests_failed == 0:
        print("\n[+] All tests passed!")
        return 0
    else:
        print(f"\n[-] {tests_failed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
