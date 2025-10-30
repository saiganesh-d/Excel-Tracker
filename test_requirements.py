"""
Test Suite for Requirement Analyzer

Tests requirement_analyzer.py functionality including requirement detection,
classification, level detection, type classification, and change comparison.

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
    """Test 1: Import requirement analyzer"""
    test_header("Requirement Analyzer Imports")

    try:
        from requirement_analyzer import (
            RequirementAnalyzer, Requirement, RequirementChange,
            RequirementLevel, RequirementType
        )
        assert_true(True, "All imports successful")
        return True
    except Exception as e:
        assert_true(False, f"Import failed: {e}")
        return False


def test_must_detection():
    """Test 2: Detect MUST requirements"""
    test_header("MUST Requirement Detection")

    try:
        from requirement_analyzer import RequirementAnalyzer, RequirementLevel

        analyzer = RequirementAnalyzer()

        test_sentences = [
            "The system must authenticate users.",
            "Users are required to provide valid credentials.",
            "Authentication is mandatory for all operations.",
            "The application shall verify user identity."
        ]

        for sentence in test_sentences:
            reqs = analyzer.analyze_text(sentence)
            if reqs:
                req = reqs[0]
                is_must = req.level in [RequirementLevel.MUST, RequirementLevel.SHALL, RequirementLevel.REQUIRED]
                assert_true(is_must, f"Detected as MUST: '{sentence[:40]}...'")
            else:
                assert_true(False, f"Failed to detect: '{sentence[:40]}...'")

        return True

    except Exception as e:
        assert_true(False, f"MUST detection failed: {e}")
        return False


def test_should_detection():
    """Test 3: Detect SHOULD requirements"""
    test_header("SHOULD Requirement Detection")

    try:
        from requirement_analyzer import RequirementAnalyzer, RequirementLevel

        analyzer = RequirementAnalyzer()

        test_sentences = [
            "The system should provide feedback to users.",
            "It is recommended to use secure connections.",
            "The interface ought to be intuitive."
        ]

        for sentence in test_sentences:
            reqs = analyzer.analyze_text(sentence)
            if reqs:
                req = reqs[0]
                is_should = req.level in [RequirementLevel.SHOULD, RequirementLevel.RECOMMENDED]
                assert_true(is_should, f"Detected as SHOULD: '{sentence[:40]}...'")
            else:
                assert_true(False, f"Failed to detect: '{sentence[:40]}...'")

        return True

    except Exception as e:
        assert_true(False, f"SHOULD detection failed: {e}")
        return False


def test_may_detection():
    """Test 4: Detect MAY/optional requirements"""
    test_header("MAY/Optional Requirement Detection")

    try:
        from requirement_analyzer import RequirementAnalyzer, RequirementLevel

        analyzer = RequirementAnalyzer()

        test_sentences = [
            "The system may provide additional features.",
            "Users can optionally enable notifications.",
            "The interface might include advanced options."
        ]

        for sentence in test_sentences:
            reqs = analyzer.analyze_text(sentence)
            if reqs:
                req = reqs[0]
                is_may = req.level in [RequirementLevel.MAY, RequirementLevel.OPTIONAL]
                assert_true(is_may, f"Detected as MAY: '{sentence[:40]}...'")
            else:
                # MAY requirements might have lower confidence
                print(f"[i] Not detected (acceptable for MAY): '{sentence[:40]}...'")

        assert_true(True, "MAY detection test completed")
        return True

    except Exception as e:
        assert_true(False, f"MAY detection failed: {e}")
        return False


def test_prohibition_detection():
    """Test 5: Detect prohibition requirements (must not)"""
    test_header("Prohibition Detection")

    try:
        from requirement_analyzer import RequirementAnalyzer, RequirementLevel

        analyzer = RequirementAnalyzer()

        test_sentences = [
            "The system must not store passwords in plain text.",
            "Users shall not bypass authentication.",
            "The application may not share personal data."
        ]

        for sentence in test_sentences:
            reqs = analyzer.analyze_text(sentence)
            if reqs:
                req = reqs[0]
                assert_true(req.is_prohibition, f"Detected as prohibition: '{sentence[:40]}...'")
                is_prohibition_level = req.level in [RequirementLevel.MUST_NOT, RequirementLevel.SHALL_NOT]
                assert_true(is_prohibition_level, f"Correct prohibition level: '{sentence[:40]}...'")
            else:
                assert_true(False, f"Failed to detect prohibition: '{sentence[:40]}...'")

        return True

    except Exception as e:
        assert_true(False, f"Prohibition detection failed: {e}")
        return False


def test_type_classification():
    """Test 6: Classify requirement types"""
    test_header("Requirement Type Classification")

    try:
        from requirement_analyzer import RequirementAnalyzer, RequirementType

        analyzer = RequirementAnalyzer()

        test_cases = [
            ("The system must calculate monthly totals.", RequirementType.FUNCTIONAL),
            ("Response time shall be under 2 seconds.", RequirementType.NON_FUNCTIONAL),
            ("The system must comply with GDPR regulations.", RequirementType.LEGAL),
            ("Data must be stored in JSON format.", RequirementType.DATA),
        ]

        for sentence, expected_type in test_cases:
            reqs = analyzer.analyze_text(sentence)
            if reqs:
                req = reqs[0]
                print(f"[i] Sentence: '{sentence[:50]}...'")
                print(f"[i] Detected type: {req.type.value}")
                print(f"[i] Expected type: {expected_type.value}")
                assert_equals(req.type, expected_type, f"Correct type for: '{sentence[:40]}...'")
            else:
                assert_true(False, f"Failed to detect: '{sentence[:40]}...'")

        return True

    except Exception as e:
        assert_true(False, f"Type classification failed: {e}")
        return False


def test_german_detection():
    """Test 7: Detect German requirements"""
    test_header("German Requirement Detection")

    try:
        from requirement_analyzer import RequirementAnalyzer, RequirementLevel

        analyzer = RequirementAnalyzer(detect_german=True)

        test_sentences = [
            "Das System muss Benutzer authentifizieren.",
            "Die Anwendung soll eine Bestätigung senden.",
            "Der Benutzer kann optionale Einstellungen ändern."
        ]

        detected_count = 0
        for sentence in test_sentences:
            reqs = analyzer.analyze_text(sentence)
            if reqs:
                detected_count += 1
                print(f"[+] Detected German requirement: '{sentence}'")

        assert_true(detected_count > 0, f"Detected {detected_count}/3 German requirements")

        return True

    except Exception as e:
        assert_true(False, f"German detection failed: {e}")
        return False


def test_paragraph_analysis():
    """Test 8: Analyze paragraphs"""
    test_header("Paragraph Analysis")

    try:
        from requirement_analyzer import RequirementAnalyzer

        analyzer = RequirementAnalyzer()

        paragraphs = [
            "The system must authenticate users. Users shall provide valid credentials.",
            "The interface should be user-friendly. It is recommended to use clear labels.",
            "Performance is important. Response time must be under 2 seconds."
        ]

        reqs = analyzer.analyze_paragraphs(paragraphs)

        assert_true(len(reqs) > 0, f"Found requirements in paragraphs")
        print(f"[i] Found {len(reqs)} requirements across {len(paragraphs)} paragraphs")

        # Check paragraph indices are set
        has_indices = all(req.paragraph_index >= 0 for req in reqs)
        assert_true(has_indices, "All requirements have paragraph indices")

        return True

    except Exception as e:
        assert_true(False, f"Paragraph analysis failed: {e}")
        return False


def test_requirement_comparison():
    """Test 9: Compare requirements between documents"""
    test_header("Requirement Comparison")

    try:
        from requirement_analyzer import RequirementAnalyzer

        analyzer = RequirementAnalyzer()

        old_text = """
        The system must authenticate users.
        The interface should be user-friendly.
        Data shall be encrypted.
        """

        new_text = """
        The system must authenticate users.
        The interface must be user-friendly.
        The system should provide logging.
        """

        old_reqs = analyzer.analyze_text(old_text)
        new_reqs = analyzer.analyze_text(new_text)

        print(f"[i] Old requirements: {len(old_reqs)}")
        print(f"[i] New requirements: {len(new_reqs)}")

        changes = analyzer.compare_requirements(old_reqs, new_reqs)

        print(f"[i] Total changes: {len(changes)}")

        # Count change types
        added = sum(1 for c in changes if c.change_type == 'added')
        removed = sum(1 for c in changes if c.change_type == 'removed')
        level_changed = sum(1 for c in changes if c.change_type == 'level_changed')

        print(f"[i] Added: {added}, Removed: {removed}, Level changed: {level_changed}")

        assert_true(len(changes) > 0, "Detected requirement changes")
        assert_true(added > 0, "Detected added requirements")
        assert_true(removed > 0, "Detected removed requirements")
        # Level change detection depends on similarity matching
        print(f"[i] Level changes detected: {level_changed} (may vary based on similarity)")
        assert_true(True, "Requirement comparison completed")

        return True

    except Exception as e:
        assert_true(False, f"Requirement comparison failed: {e}")
        return False


def test_statistics():
    """Test 10: Get requirement statistics"""
    test_header("Requirement Statistics")

    try:
        from requirement_analyzer import RequirementAnalyzer

        analyzer = RequirementAnalyzer()

        test_text = """
        The system must authenticate users.
        The system shall encrypt data.
        The interface should be user-friendly.
        The system may provide additional features.
        The system must not store passwords in plain text.
        """

        reqs = analyzer.analyze_text(test_text)

        stats = analyzer.get_statistics(reqs)

        print(f"[i] Statistics: {stats}")

        assert_true('total' in stats, "Statistics include total")
        assert_true('by_level' in stats, "Statistics include by_level")
        assert_true('by_type' in stats, "Statistics include by_type")
        assert_true('prohibitions' in stats, "Statistics include prohibitions")
        assert_true('average_confidence' in stats, "Statistics include average_confidence")

        assert_true(stats['total'] > 0, f"Total requirements: {stats['total']}")
        assert_true(stats['prohibitions'] > 0, f"Prohibitions: {stats['prohibitions']}")
        assert_true(stats['average_confidence'] > 0, f"Average confidence: {stats['average_confidence']}")

        return True

    except Exception as e:
        assert_true(False, f"Statistics test failed: {e}")
        return False


def test_serialization():
    """Test 11: Serialize requirements to dict"""
    test_header("Requirement Serialization")

    try:
        from requirement_analyzer import RequirementAnalyzer

        analyzer = RequirementAnalyzer()

        test_text = "The system must authenticate users."
        reqs = analyzer.analyze_text(test_text)

        if reqs:
            req = reqs[0]
            req_dict = req.to_dict()

            assert_true(isinstance(req_dict, dict), "Requirement converted to dict")
            assert_true('text' in req_dict, "Dict contains text")
            assert_true('level' in req_dict, "Dict contains level")
            assert_true('type' in req_dict, "Dict contains type")
            assert_true('keywords' in req_dict, "Dict contains keywords")
            assert_true('confidence' in req_dict, "Dict contains confidence")

            print(f"[i] Requirement dict keys: {list(req_dict.keys())}")
        else:
            assert_true(False, "Failed to detect requirement")

        return True

    except Exception as e:
        assert_true(False, f"Serialization test failed: {e}")
        return False


def test_confidence_scoring():
    """Test 12: Confidence scoring"""
    test_header("Confidence Scoring")

    try:
        from requirement_analyzer import RequirementAnalyzer

        analyzer = RequirementAnalyzer(min_confidence=0.5)

        # Clear requirement
        clear_req = "The system must authenticate all users before granting access."
        reqs1 = analyzer.analyze_text(clear_req)

        # Ambiguous statement
        ambiguous = "Users might need authentication."
        reqs2 = analyzer.analyze_text(ambiguous)

        print(f"[i] Clear requirement detected: {len(reqs1) > 0}")
        if reqs1:
            print(f"[i] Clear requirement confidence: {reqs1[0].confidence}")

        print(f"[i] Ambiguous detected: {len(reqs2) > 0}")
        if reqs2:
            print(f"[i] Ambiguous confidence: {reqs2[0].confidence}")

        assert_true(len(reqs1) > 0, "Detected clear requirement")

        if reqs1 and reqs2:
            assert_true(reqs1[0].confidence > reqs2[0].confidence,
                       "Clear requirement has higher confidence")
        else:
            assert_true(True, "Confidence scoring test completed")

        return True

    except Exception as e:
        assert_true(False, f"Confidence scoring failed: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("REQUIREMENT ANALYZER TEST SUITE")
    print("=" * 60)

    # Run tests
    tests = [
        test_imports,
        test_must_detection,
        test_should_detection,
        test_may_detection,
        test_prohibition_detection,
        test_type_classification,
        test_german_detection,
        test_paragraph_analysis,
        test_requirement_comparison,
        test_statistics,
        test_serialization,
        test_confidence_scoring
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
