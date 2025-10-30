"""
Local LLM Integration - Generate intelligent explanations for document changes

This module integrates a local LLM (Large Language Model) to generate
human-readable explanations for document changes, requirement modifications,
and semantic differences. Uses llama-cpp-python for 100% local processing.

Key Features:
- Local LLM execution (no external APIs)
- Change explanation generation
- Requirement interpretation
- Context-aware analysis
- GPU acceleration support
- Prompt templates for different tasks

Author: Advanced PDF Comparison System
Date: 2025-10-30
"""

import json
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum

try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False
    print("[!] llama-cpp-python not available. Run: pip install llama-cpp-python")
    Llama = None


class ExplanationTask(Enum):
    """Types of explanation tasks"""
    CHANGE_SUMMARY = "change_summary"           # Summarize document changes
    REQUIREMENT_CHANGE = "requirement_change"   # Explain requirement changes
    SEMANTIC_DIFF = "semantic_diff"             # Explain semantic differences
    PARAGRAPH_CHANGE = "paragraph_change"       # Explain paragraph changes
    CRITICAL_ANALYSIS = "critical_analysis"     # Analyze critical changes


@dataclass
class LLMResponse:
    """
    Response from LLM

    Attributes:
        text: Generated text response
        task: Task type that generated this response
        tokens_used: Number of tokens used
        confidence: Confidence score (0-1) if available
        metadata: Additional metadata
    """
    text: str
    task: ExplanationTask
    tokens_used: int = 0
    confidence: float = 1.0
    metadata: Dict = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'text': self.text,
            'task': self.task.value,
            'tokens_used': self.tokens_used,
            'confidence': self.confidence,
            'metadata': self.metadata or {}
        }


class LocalLLM:
    """
    Local LLM integration for generating explanations

    This class provides a wrapper around llama-cpp-python to generate
    intelligent explanations for document changes. All processing is
    done locally for privacy.
    """

    # Prompt templates for different tasks
    PROMPTS = {
        ExplanationTask.CHANGE_SUMMARY: """You are analyzing changes between two document versions.

Old text: {old_text}
New text: {new_text}

Provide a concise summary (1-2 sentences) of the key changes:""",

        ExplanationTask.REQUIREMENT_CHANGE: """You are analyzing requirement changes in a technical document.

Old requirement: {old_req}
New requirement: {new_req}

Explain the impact and significance of this change (1-2 sentences):""",

        ExplanationTask.SEMANTIC_DIFF: """You are comparing the meaning of two text passages.

First passage: {text1}
Second passage: {text2}

Are these semantically equivalent? If not, explain the key difference (1 sentence):""",

        ExplanationTask.PARAGRAPH_CHANGE: """You are analyzing changes to a paragraph.

Original: {old_para}
Modified: {new_para}

Describe what changed and why it matters (1-2 sentences):""",

        ExplanationTask.CRITICAL_ANALYSIS: """You are reviewing critical changes in a document.

Changes: {changes}

Identify the most critical change and explain its potential impact (2-3 sentences):"""
    }

    def __init__(
        self,
        model_path: Optional[str] = None,
        use_gpu: bool = True,
        n_ctx: int = 2048,
        n_threads: int = 4,
        temperature: float = 0.7,
        max_tokens: int = 150
    ):
        """
        Initialize local LLM

        Args:
            model_path: Path to GGUF model file
            use_gpu: Whether to use GPU acceleration
            n_ctx: Context window size
            n_threads: Number of CPU threads
            temperature: Sampling temperature (0=deterministic, 1=creative)
            max_tokens: Maximum tokens to generate
        """
        self.model_path = model_path
        self.use_gpu = use_gpu
        self.n_ctx = n_ctx
        self.n_threads = n_threads
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._model = None

        print(f"[i] LocalLLM initialized")
        print(f"    Model path: {model_path or 'Not specified'}")
        print(f"    GPU: {use_gpu}")
        print(f"    Context window: {n_ctx}")
        print(f"    Max tokens: {max_tokens}")

    def _load_model(self) -> Optional[Any]:
        """Load LLM model (lazy loading)"""
        if self._model is not None:
            return self._model

        if not LLAMA_CPP_AVAILABLE or Llama is None:
            print("[!] llama-cpp-python not available")
            return None

        if not self.model_path:
            print("[!] No model path specified")
            return None

        try:
            print(f"[i] Loading LLM model: {self.model_path}...")

            # Determine GPU layers
            n_gpu_layers = -1 if self.use_gpu else 0

            self._model = Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_threads=self.n_threads,
                n_gpu_layers=n_gpu_layers,
                verbose=False
            )

            print("[+] Model loaded successfully")
            return self._model

        except Exception as e:
            print(f"[-] Error loading model: {e}")
            return None

    def generate_explanation(
        self,
        task: ExplanationTask,
        **kwargs
    ) -> Optional[LLMResponse]:
        """
        Generate explanation for a task

        Args:
            task: Type of explanation task
            **kwargs: Task-specific parameters

        Returns:
            LLMResponse with generated text
        """
        # Get prompt template
        if task not in self.PROMPTS:
            print(f"[-] Unknown task: {task}")
            return None

        prompt_template = self.PROMPTS[task]

        # Format prompt with provided arguments
        try:
            prompt = prompt_template.format(**kwargs)
        except KeyError as e:
            print(f"[-] Missing required parameter: {e}")
            return None

        # Generate response
        return self._generate(prompt, task)

    def _generate(
        self,
        prompt: str,
        task: ExplanationTask
    ) -> Optional[LLMResponse]:
        """
        Generate text using LLM

        Args:
            prompt: Input prompt
            task: Task type

        Returns:
            LLMResponse with generated text
        """
        model = self._load_model()

        if model is None:
            # Return mock response when model not available
            return LLMResponse(
                text="[LLM not available - mock response]",
                task=task,
                tokens_used=0,
                confidence=0.0
            )

        try:
            # Generate response
            output = model(
                prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stop=["User:", "Question:", "\n\n\n"],
                echo=False
            )

            # Extract generated text
            generated_text = output['choices'][0]['text'].strip()
            tokens_used = output['usage']['completion_tokens']

            return LLMResponse(
                text=generated_text,
                task=task,
                tokens_used=tokens_used,
                confidence=1.0
            )

        except Exception as e:
            print(f"[-] Error generating response: {e}")
            return LLMResponse(
                text=f"[Error: {e}]",
                task=task,
                tokens_used=0,
                confidence=0.0
            )

    def explain_change(
        self,
        old_text: str,
        new_text: str
    ) -> Optional[LLMResponse]:
        """
        Generate explanation for text change

        Args:
            old_text: Original text
            new_text: Modified text

        Returns:
            LLMResponse with explanation
        """
        return self.generate_explanation(
            ExplanationTask.CHANGE_SUMMARY,
            old_text=old_text,
            new_text=new_text
        )

    def explain_requirement_change(
        self,
        old_requirement: str,
        new_requirement: str
    ) -> Optional[LLMResponse]:
        """
        Generate explanation for requirement change

        Args:
            old_requirement: Original requirement
            new_requirement: Modified requirement

        Returns:
            LLMResponse with explanation
        """
        return self.generate_explanation(
            ExplanationTask.REQUIREMENT_CHANGE,
            old_req=old_requirement,
            new_req=new_requirement
        )

    def explain_semantic_difference(
        self,
        text1: str,
        text2: str
    ) -> Optional[LLMResponse]:
        """
        Explain semantic difference between two texts

        Args:
            text1: First text
            text2: Second text

        Returns:
            LLMResponse with explanation
        """
        return self.generate_explanation(
            ExplanationTask.SEMANTIC_DIFF,
            text1=text1,
            text2=text2
        )

    def explain_paragraph_change(
        self,
        old_paragraph: str,
        new_paragraph: str
    ) -> Optional[LLMResponse]:
        """
        Explain paragraph change

        Args:
            old_paragraph: Original paragraph
            new_paragraph: Modified paragraph

        Returns:
            LLMResponse with explanation
        """
        return self.generate_explanation(
            ExplanationTask.PARAGRAPH_CHANGE,
            old_para=old_paragraph,
            new_para=new_paragraph
        )

    def analyze_critical_changes(
        self,
        changes: List[Dict]
    ) -> Optional[LLMResponse]:
        """
        Analyze critical changes

        Args:
            changes: List of change dictionaries

        Returns:
            LLMResponse with analysis
        """
        # Format changes as text
        changes_text = "\n".join([
            f"- {change.get('description', str(change))}"
            for change in changes[:10]  # Limit to 10 changes
        ])

        return self.generate_explanation(
            ExplanationTask.CRITICAL_ANALYSIS,
            changes=changes_text
        )

    def batch_explain(
        self,
        tasks: List[tuple]
    ) -> List[Optional[LLMResponse]]:
        """
        Generate explanations for multiple tasks

        Args:
            tasks: List of (task_type, kwargs) tuples

        Returns:
            List of LLMResponse objects
        """
        responses = []

        for task_type, kwargs in tasks:
            response = self.generate_explanation(task_type, **kwargs)
            responses.append(response)

        return responses


class ExplanationGenerator:
    """
    High-level explanation generator

    This class provides convenient methods for generating explanations
    for common document comparison scenarios.
    """

    def __init__(self, llm: Optional[LocalLLM] = None):
        """
        Initialize explanation generator

        Args:
            llm: Optional LocalLLM instance
        """
        self.llm = llm or LocalLLM()

        print(f"[i] ExplanationGenerator initialized")

    def explain_matches(
        self,
        matches: List[Dict],
        max_explanations: int = 10
    ) -> List[Dict]:
        """
        Generate explanations for paragraph matches

        Args:
            matches: List of match dictionaries
            max_explanations: Maximum number of explanations to generate

        Returns:
            List of matches with explanations added
        """
        explained_matches = []

        for i, match in enumerate(matches[:max_explanations]):
            old_text = match.get('old_text', '')
            new_text = match.get('new_text', '')
            change_type = match.get('change_type', 'unknown')

            # Skip unchanged matches
            if change_type == 'unchanged':
                explained_matches.append(match)
                continue

            # Generate explanation
            if old_text and new_text:
                response = self.llm.explain_change(old_text, new_text)
                if response:
                    match['llm_explanation'] = response.text
                    match['llm_tokens'] = response.tokens_used

            explained_matches.append(match)

        return explained_matches

    def explain_requirements(
        self,
        requirement_changes: List[Dict]
    ) -> List[Dict]:
        """
        Generate explanations for requirement changes

        Args:
            requirement_changes: List of requirement change dictionaries

        Returns:
            List of changes with explanations added
        """
        explained_changes = []

        for change in requirement_changes:
            old_req = change.get('old_requirement', {})
            new_req = change.get('new_requirement', {})
            change_type = change.get('change_type', 'unknown')

            # Skip unchanged
            if change_type == 'unchanged':
                explained_changes.append(change)
                continue

            # Generate explanation for modified requirements
            if old_req and new_req and change_type in ['modified', 'level_changed']:
                old_text = old_req.get('text', '')
                new_text = new_req.get('text', '')

                response = self.llm.explain_requirement_change(old_text, new_text)
                if response:
                    change['llm_explanation'] = response.text
                    change['llm_tokens'] = response.tokens_used

            explained_changes.append(change)

        return explained_changes

    def generate_summary(
        self,
        comparison_result: Dict
    ) -> Optional[str]:
        """
        Generate overall summary of comparison

        Args:
            comparison_result: Comparison result dictionary

        Returns:
            Summary text
        """
        # Extract key statistics
        summary = comparison_result.get('summary', {})
        total_old = summary.get('total_old', 0)
        total_new = summary.get('total_new', 0)
        unchanged = summary.get('unchanged', 0)
        modified = summary.get('modified', 0)
        added = summary.get('added', 0)
        deleted = summary.get('deleted', 0)

        # Create summary text
        summary_text = f"""
Document Comparison Summary:
- Original: {total_old} paragraphs
- Modified: {total_new} paragraphs
- Unchanged: {unchanged}
- Modified: {modified}
- Added: {added}
- Deleted: {deleted}

Key changes need to be reviewed for impact analysis.
"""

        return summary_text.strip()


def main():
    """Example usage and testing"""
    print("=" * 60)
    print("LOCAL LLM TEST")
    print("=" * 60)

    # Initialize LLM
    llm = LocalLLM(
        model_path=None,  # No model specified for testing
        use_gpu=True,
        max_tokens=100
    )

    print("\n[TEST 1] Change explanation")
    old_text = "The system must authenticate users."
    new_text = "The system shall verify user credentials."

    response = llm.explain_change(old_text, new_text)
    if response:
        print(f"[+] Explanation: {response.text}")
        print(f"[i] Tokens used: {response.tokens_used}")
    else:
        print("[-] Failed to generate explanation")

    print("\n[TEST 2] Requirement change")
    old_req = "The interface should be user-friendly."
    new_req = "The interface must be intuitive and accessible."

    response = llm.explain_requirement_change(old_req, new_req)
    if response:
        print(f"[+] Explanation: {response.text}")
        print(f"[i] Tokens used: {response.tokens_used}")
    else:
        print("[-] Failed to generate explanation")

    print("\n[TEST 3] Semantic difference")
    text1 = "Users can login with email."
    text2 = "Email-based authentication is supported."

    response = llm.explain_semantic_difference(text1, text2)
    if response:
        print(f"[+] Explanation: {response.text}")
        print(f"[i] Tokens used: {response.tokens_used}")
    else:
        print("[-] Failed to generate explanation")

    # Test explanation generator
    print("\n[TEST 4] Explanation generator")
    generator = ExplanationGenerator(llm)

    matches = [
        {
            'old_text': 'Original paragraph.',
            'new_text': 'Modified paragraph.',
            'change_type': 'modified'
        }
    ]

    explained = generator.explain_matches(matches)
    print(f"[+] Generated {len(explained)} explanations")

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
