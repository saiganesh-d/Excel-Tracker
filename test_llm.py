"""
Test Suite for Local LLM Integration

Tests local_llm.py functionality including LLM initialization,
explanation generation, and high-level explanation generator.

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
    """Test 1: Import local LLM"""
    test_header("Local LLM Imports")

    try:
        from local_llm import (
            LocalLLM, ExplanationGenerator, LLMResponse,
            ExplanationTask
        )
        assert_true(True, "All imports successful")
        return True
    except Exception as e:
        assert_true(False, f"Import failed: {e}")
        return False


def test_llm_initialization():
    """Test 2: Initialize LocalLLM"""
    test_header("LLM Initialization")

    try:
        from local_llm import LocalLLM

        llm = LocalLLM(
            model_path=None,  # No model for testing
            use_gpu=True,
            max_tokens=100
        )

        assert_true(llm is not None, "LocalLLM initialized")
        assert_true(hasattr(llm, 'generate_explanation'), "Has generate_explanation method")
        assert_true(hasattr(llm, 'explain_change'), "Has explain_change method")

        return True

    except Exception as e:
        assert_true(False, f"LLM initialization failed: {e}")
        return False


def test_task_types():
    """Test 3: Explanation task types"""
    test_header("Explanation Task Types")

    try:
        from local_llm import ExplanationTask

        # Check all task types exist
        task_types = [
            'CHANGE_SUMMARY',
            'REQUIREMENT_CHANGE',
            'SEMANTIC_DIFF',
            'PARAGRAPH_CHANGE',
            'CRITICAL_ANALYSIS'
        ]

        for task_name in task_types:
            has_task = hasattr(ExplanationTask, task_name)
            assert_true(has_task, f"Has task type: {task_name}")

        return True

    except Exception as e:
        assert_true(False, f"Task types test failed: {e}")
        return False


def test_change_explanation():
    """Test 4: Generate change explanation"""
    test_header("Change Explanation")

    try:
        from local_llm import LocalLLM

        llm = LocalLLM(model_path=None)

        old_text = "The system must authenticate users."
        new_text = "The system shall verify user credentials."

        response = llm.explain_change(old_text, new_text)

        assert_true(response is not None, "Response generated")
        assert_true(hasattr(response, 'text'), "Response has text")
        assert_true(hasattr(response, 'task'), "Response has task")
        assert_true(hasattr(response, 'tokens_used'), "Response has tokens_used")

        print(f"[i] Response: {response.text[:100]}")

        return True

    except Exception as e:
        assert_true(False, f"Change explanation failed: {e}")
        return False


def test_requirement_explanation():
    """Test 5: Generate requirement change explanation"""
    test_header("Requirement Change Explanation")

    try:
        from local_llm import LocalLLM

        llm = LocalLLM(model_path=None)

        old_req = "The interface should be user-friendly."
        new_req = "The interface must be intuitive."

        response = llm.explain_requirement_change(old_req, new_req)

        assert_true(response is not None, "Response generated")
        assert_true(len(response.text) > 0, "Response has content")

        print(f"[i] Response: {response.text[:100]}")

        return True

    except Exception as e:
        assert_true(False, f"Requirement explanation failed: {e}")
        return False


def test_semantic_difference():
    """Test 6: Explain semantic difference"""
    test_header("Semantic Difference Explanation")

    try:
        from local_llm import LocalLLM

        llm = LocalLLM(model_path=None)

        text1 = "Users can login with email."
        text2 = "Email-based authentication is supported."

        response = llm.explain_semantic_difference(text1, text2)

        assert_true(response is not None, "Response generated")
        assert_true(len(response.text) > 0, "Response has content")

        print(f"[i] Response: {response.text[:100]}")

        return True

    except Exception as e:
        assert_true(False, f"Semantic difference failed: {e}")
        return False


def test_paragraph_change():
    """Test 7: Explain paragraph change"""
    test_header("Paragraph Change Explanation")

    try:
        from local_llm import LocalLLM

        llm = LocalLLM(model_path=None)

        old_para = "The system provides basic functionality."
        new_para = "The system offers comprehensive features."

        response = llm.explain_paragraph_change(old_para, new_para)

        assert_true(response is not None, "Response generated")
        assert_true(len(response.text) > 0, "Response has content")

        print(f"[i] Response: {response.text[:100]}")

        return True

    except Exception as e:
        assert_true(False, f"Paragraph change failed: {e}")
        return False


def test_critical_analysis():
    """Test 8: Analyze critical changes"""
    test_header("Critical Changes Analysis")

    try:
        from local_llm import LocalLLM

        llm = LocalLLM(model_path=None)

        changes = [
            {'description': 'Authentication requirement changed from SHOULD to MUST'},
            {'description': 'Password encryption standard upgraded'},
            {'description': 'New GDPR compliance requirement added'}
        ]

        response = llm.analyze_critical_changes(changes)

        assert_true(response is not None, "Response generated")
        assert_true(len(response.text) > 0, "Response has content")

        print(f"[i] Response: {response.text[:100]}")

        return True

    except Exception as e:
        assert_true(False, f"Critical analysis failed: {e}")
        return False


def test_batch_explain():
    """Test 9: Batch explanation generation"""
    test_header("Batch Explanation")

    try:
        from local_llm import LocalLLM, ExplanationTask

        llm = LocalLLM(model_path=None)

        tasks = [
            (ExplanationTask.CHANGE_SUMMARY, {
                'old_text': 'Text A',
                'new_text': 'Text B'
            }),
            (ExplanationTask.SEMANTIC_DIFF, {
                'text1': 'First text',
                'text2': 'Second text'
            })
        ]

        responses = llm.batch_explain(tasks)

        assert_true(len(responses) == 2, f"Generated {len(responses)} responses")
        assert_true(all(r is not None for r in responses), "All responses generated")

        return True

    except Exception as e:
        assert_true(False, f"Batch explain failed: {e}")
        return False


def test_explanation_generator():
    """Test 10: High-level explanation generator"""
    test_header("Explanation Generator")

    try:
        from local_llm import ExplanationGenerator, LocalLLM

        llm = LocalLLM(model_path=None)
        generator = ExplanationGenerator(llm)

        assert_true(generator is not None, "ExplanationGenerator initialized")
        assert_true(hasattr(generator, 'explain_matches'), "Has explain_matches method")
        assert_true(hasattr(generator, 'explain_requirements'), "Has explain_requirements method")
        assert_true(hasattr(generator, 'generate_summary'), "Has generate_summary method")

        return True

    except Exception as e:
        assert_true(False, f"Explanation generator failed: {e}")
        return False


def test_explain_matches():
    """Test 11: Explain paragraph matches"""
    test_header("Explain Matches")

    try:
        from local_llm import ExplanationGenerator, LocalLLM

        llm = LocalLLM(model_path=None)
        generator = ExplanationGenerator(llm)

        matches = [
            {
                'old_text': 'Original paragraph.',
                'new_text': 'Modified paragraph.',
                'change_type': 'modified'
            },
            {
                'old_text': 'Unchanged text.',
                'new_text': 'Unchanged text.',
                'change_type': 'unchanged'
            }
        ]

        explained = generator.explain_matches(matches)

        assert_true(len(explained) == 2, f"Processed {len(explained)} matches")
        assert_true('llm_explanation' in explained[0], "First match has explanation")

        print(f"[i] First explanation: {explained[0].get('llm_explanation', 'N/A')[:50]}")

        return True

    except Exception as e:
        assert_true(False, f"Explain matches failed: {e}")
        return False


def test_explain_requirements():
    """Test 12: Explain requirement changes"""
    test_header("Explain Requirements")

    try:
        from local_llm import ExplanationGenerator, LocalLLM

        llm = LocalLLM(model_path=None)
        generator = ExplanationGenerator(llm)

        requirement_changes = [
            {
                'old_requirement': {'text': 'System should be fast'},
                'new_requirement': {'text': 'System must respond within 2s'},
                'change_type': 'level_changed'
            }
        ]

        explained = generator.explain_requirements(requirement_changes)

        assert_true(len(explained) == 1, "Processed 1 requirement change")
        assert_true('llm_explanation' in explained[0], "Has explanation")

        print(f"[i] Explanation: {explained[0].get('llm_explanation', 'N/A')[:50]}")

        return True

    except Exception as e:
        assert_true(False, f"Explain requirements failed: {e}")
        return False


def test_generate_summary():
    """Test 13: Generate comparison summary"""
    test_header("Generate Summary")

    try:
        from local_llm import ExplanationGenerator, LocalLLM

        llm = LocalLLM(model_path=None)
        generator = ExplanationGenerator(llm)

        comparison_result = {
            'summary': {
                'total_old': 10,
                'total_new': 12,
                'unchanged': 5,
                'modified': 3,
                'added': 2,
                'deleted': 0
            }
        }

        summary = generator.generate_summary(comparison_result)

        assert_true(summary is not None, "Summary generated")
        assert_true(len(summary) > 0, "Summary has content")
        assert_true('10 paragraphs' in summary, "Contains old paragraph count")
        assert_true('12 paragraphs' in summary, "Contains new paragraph count")

        print(f"[i] Summary (first 100 chars):\n{summary[:100]}...")

        return True

    except Exception as e:
        assert_true(False, f"Generate summary failed: {e}")
        return False


def test_response_serialization():
    """Test 14: Serialize LLMResponse to dict"""
    test_header("Response Serialization")

    try:
        from local_llm import LocalLLM

        llm = LocalLLM(model_path=None)

        response = llm.explain_change("Old text", "New text")

        if response:
            response_dict = response.to_dict()

            assert_true(isinstance(response_dict, dict), "Response converted to dict")
            assert_true('text' in response_dict, "Dict contains text")
            assert_true('task' in response_dict, "Dict contains task")
            assert_true('tokens_used' in response_dict, "Dict contains tokens_used")
            assert_true('confidence' in response_dict, "Dict contains confidence")

            print(f"[i] Response dict keys: {list(response_dict.keys())}")
        else:
            assert_true(False, "Failed to generate response")

        return True

    except Exception as e:
        assert_true(False, f"Response serialization failed: {e}")
        return False


def test_mock_responses():
    """Test 15: Mock responses when model unavailable"""
    test_header("Mock Responses")

    try:
        from local_llm import LocalLLM

        llm = LocalLLM(model_path=None)

        # Generate response without model
        response = llm.explain_change("Text 1", "Text 2")

        assert_true(response is not None, "Mock response generated")
        assert_true(response.confidence == 0.0, "Mock response has 0 confidence")

        print(f"[i] Mock response: {response.text}")
        print(f"[i] Confidence: {response.confidence}")

        return True

    except Exception as e:
        assert_true(False, f"Mock responses test failed: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("LOCAL LLM TEST SUITE")
    print("=" * 60)

    # Run tests
    tests = [
        test_imports,
        test_llm_initialization,
        test_task_types,
        test_change_explanation,
        test_requirement_explanation,
        test_semantic_difference,
        test_paragraph_change,
        test_critical_analysis,
        test_batch_explain,
        test_explanation_generator,
        test_explain_matches,
        test_explain_requirements,
        test_generate_summary,
        test_response_serialization,
        test_mock_responses
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
