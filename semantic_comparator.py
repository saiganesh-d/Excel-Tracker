"""
Semantic Comparator - Compare documents using semantic embeddings

This module provides functionality to compare paragraphs and documents
using semantic similarity. It handles paragraph matching, change detection,
and generates detailed comparison reports.

Key Features:
- Paragraph-level semantic comparison
- Optimal matching using Hungarian algorithm
- Detects additions, deletions, modifications, moves
- Change classification (critical, major, minor)
- Handles paraphrasing and reordering

Author: Advanced PDF Comparison System
Date: 2025-10-30
"""

from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import re

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("[!] numpy not available. Run: pip install numpy")
    np = None

try:
    from scipy.optimize import linear_sum_assignment
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("[!] scipy not available. Run: pip install scipy")

from semantic_embedder import SemanticEmbedder, Embedding


class ChangeType(Enum):
    """Type of change detected"""
    UNCHANGED = "unchanged"
    MODIFIED = "modified"
    ADDED = "added"
    DELETED = "deleted"
    MOVED = "moved"


class ChangeSeverity(Enum):
    """Severity of detected change"""
    CRITICAL = "critical"  # Requirement changes, legal terms
    MAJOR = "major"       # Significant content changes
    MINOR = "minor"       # Minor wording changes
    TRIVIAL = "trivial"   # Formatting, whitespace


@dataclass
class ParagraphMatch:
    """
    Represents a match between paragraphs from two documents

    Attributes:
        old_index: Index in old document (-1 if added)
        new_index: Index in new document (-1 if deleted)
        old_text: Text from old document
        new_text: Text from new document
        similarity: Semantic similarity score (0-1)
        change_type: Type of change detected
        severity: Severity of change
        is_moved: Whether paragraph was moved
        explanation: Human-readable explanation of change
    """
    old_index: int
    new_index: int
    old_text: str
    new_text: str
    similarity: float
    change_type: ChangeType
    severity: ChangeSeverity = ChangeSeverity.MINOR
    is_moved: bool = False
    explanation: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'old_index': self.old_index,
            'new_index': self.new_index,
            'old_text': self.old_text,
            'new_text': self.new_text,
            'similarity': round(self.similarity, 4),
            'change_type': self.change_type.value,
            'severity': self.severity.value,
            'is_moved': self.is_moved,
            'explanation': self.explanation
        }


@dataclass
class ComparisonResult:
    """
    Complete comparison result between two documents

    Attributes:
        matches: List of paragraph matches
        total_old: Total paragraphs in old document
        total_new: Total paragraphs in new document
        unchanged_count: Number of unchanged paragraphs
        modified_count: Number of modified paragraphs
        added_count: Number of added paragraphs
        deleted_count: Number of deleted paragraphs
        moved_count: Number of moved paragraphs
        average_similarity: Average similarity across all matches
        critical_changes: List of critical changes
        major_changes: List of major changes
    """
    matches: List[ParagraphMatch] = field(default_factory=list)
    total_old: int = 0
    total_new: int = 0
    unchanged_count: int = 0
    modified_count: int = 0
    added_count: int = 0
    deleted_count: int = 0
    moved_count: int = 0
    average_similarity: float = 0.0
    critical_changes: List[ParagraphMatch] = field(default_factory=list)
    major_changes: List[ParagraphMatch] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'summary': {
                'total_old': self.total_old,
                'total_new': self.total_new,
                'unchanged': self.unchanged_count,
                'modified': self.modified_count,
                'added': self.added_count,
                'deleted': self.deleted_count,
                'moved': self.moved_count,
                'average_similarity': round(self.average_similarity, 4)
            },
            'matches': [m.to_dict() for m in self.matches],
            'critical_changes': [m.to_dict() for m in self.critical_changes],
            'major_changes': [m.to_dict() for m in self.major_changes]
        }


class SemanticComparator:
    """
    Compare documents using semantic embeddings

    This class handles document comparison at the paragraph level using
    semantic similarity. It can detect various types of changes including
    modifications, additions, deletions, and moved content.
    """

    def __init__(
        self,
        embedder: Optional[SemanticEmbedder] = None,
        similarity_threshold: float = 0.75,
        move_detection_threshold: float = 0.85,
        critical_keywords: Optional[List[str]] = None
    ):
        """
        Initialize semantic comparator

        Args:
            embedder: Optional SemanticEmbedder instance
            similarity_threshold: Minimum similarity to consider as match (0-1)
            move_detection_threshold: Minimum similarity to detect moves (0-1)
            critical_keywords: Keywords that indicate critical changes
        """
        self.embedder = embedder or SemanticEmbedder()
        self.similarity_threshold = similarity_threshold
        self.move_detection_threshold = move_detection_threshold

        # Default critical keywords (requirements, legal, etc.)
        self.critical_keywords = critical_keywords or [
            'must', 'shall', 'required', 'mandatory',
            'legal', 'compliance', 'regulation',
            'contract', 'agreement', 'liability',
            'confidential', 'proprietary', 'patent'
        ]

        print(f"[i] SemanticComparator initialized")
        print(f"    Similarity threshold: {similarity_threshold}")
        print(f"    Move detection threshold: {move_detection_threshold}")

    def compare_paragraphs(
        self,
        old_paragraphs: List[str],
        new_paragraphs: List[str]
    ) -> ComparisonResult:
        """
        Compare two sets of paragraphs semantically

        Args:
            old_paragraphs: Paragraphs from old document
            new_paragraphs: Paragraphs from new document

        Returns:
            ComparisonResult with detailed matches
        """
        print(f"[i] Comparing {len(old_paragraphs)} old vs {len(new_paragraphs)} new paragraphs...")

        # Generate embeddings
        print("[i] Generating embeddings...")
        old_embeddings = self.embedder.embed_batch(old_paragraphs)
        new_embeddings = self.embedder.embed_batch(new_paragraphs)

        # Compute similarity matrix
        print("[i] Computing similarity matrix...")
        similarity_matrix = self._compute_similarity_matrix(old_embeddings, new_embeddings)

        # Find optimal matches using Hungarian algorithm
        print("[i] Finding optimal matches...")
        matches = self._find_optimal_matches(
            old_paragraphs,
            new_paragraphs,
            similarity_matrix
        )

        # Detect moved paragraphs
        print("[i] Detecting moved paragraphs...")
        matches = self._detect_moves(matches, similarity_matrix)

        # Classify change severity
        print("[i] Classifying change severity...")
        matches = self._classify_severity(matches)

        # Generate explanations
        print("[i] Generating explanations...")
        matches = self._generate_explanations(matches)

        # Build result
        result = self._build_result(
            matches,
            len(old_paragraphs),
            len(new_paragraphs)
        )

        print(f"[+] Comparison complete:")
        print(f"    Unchanged: {result.unchanged_count}")
        print(f"    Modified: {result.modified_count}")
        print(f"    Added: {result.added_count}")
        print(f"    Deleted: {result.deleted_count}")
        print(f"    Moved: {result.moved_count}")
        print(f"    Average similarity: {result.average_similarity:.2%}")

        return result

    def _compute_similarity_matrix(
        self,
        old_embeddings: List[Optional[Embedding]],
        new_embeddings: List[Optional[Embedding]]
    ):
        """Compute similarity matrix between old and new embeddings"""
        if not NUMPY_AVAILABLE or np is None:
            # Return simple 2D list if numpy not available
            n_old = len(old_embeddings)
            n_new = len(new_embeddings)
            return [[0.0] * n_new for _ in range(n_old)]

        n_old = len(old_embeddings)
        n_new = len(new_embeddings)
        matrix = np.zeros((n_old, n_new))

        for i, old_emb in enumerate(old_embeddings):
            for j, new_emb in enumerate(new_embeddings):
                if old_emb is not None and new_emb is not None:
                    matrix[i, j] = old_emb.similarity(new_emb)

        return matrix

    def _find_optimal_matches(
        self,
        old_paragraphs: List[str],
        new_paragraphs: List[str],
        similarity_matrix
    ) -> List[ParagraphMatch]:
        """
        Find optimal paragraph matches using Hungarian algorithm

        This ensures each paragraph is matched at most once, maximizing
        total similarity.
        """
        matches = []
        n_old = len(old_paragraphs)
        n_new = len(new_paragraphs)

        if not SCIPY_AVAILABLE:
            print("[!] scipy not available, using greedy matching")
            return self._greedy_matching(old_paragraphs, new_paragraphs, similarity_matrix)

        # Use Hungarian algorithm for optimal matching
        # Convert similarity to cost (1 - similarity)
        cost_matrix = 1 - similarity_matrix

        # Pad matrix to make it square
        max_dim = max(n_old, n_new)
        padded_cost = np.ones((max_dim, max_dim))
        padded_cost[:n_old, :n_new] = cost_matrix

        # Find optimal assignment
        old_indices, new_indices = linear_sum_assignment(padded_cost)

        # Track matched indices
        matched_old = set()
        matched_new = set()

        # Create matches for valid assignments
        for old_idx, new_idx in zip(old_indices, new_indices):
            # Skip padding
            if old_idx >= n_old or new_idx >= n_new:
                continue

            similarity = similarity_matrix[old_idx, new_idx]

            # Only match if above threshold
            if similarity >= self.similarity_threshold:
                change_type = ChangeType.UNCHANGED if similarity > 0.95 else ChangeType.MODIFIED

                match = ParagraphMatch(
                    old_index=old_idx,
                    new_index=new_idx,
                    old_text=old_paragraphs[old_idx],
                    new_text=new_paragraphs[new_idx],
                    similarity=similarity,
                    change_type=change_type
                )
                matches.append(match)
                matched_old.add(old_idx)
                matched_new.add(new_idx)

        # Add deleted paragraphs (in old but not matched)
        for old_idx in range(n_old):
            if old_idx not in matched_old:
                match = ParagraphMatch(
                    old_index=old_idx,
                    new_index=-1,
                    old_text=old_paragraphs[old_idx],
                    new_text="",
                    similarity=0.0,
                    change_type=ChangeType.DELETED
                )
                matches.append(match)

        # Add new paragraphs (in new but not matched)
        for new_idx in range(n_new):
            if new_idx not in matched_new:
                match = ParagraphMatch(
                    old_index=-1,
                    new_index=new_idx,
                    old_text="",
                    new_text=new_paragraphs[new_idx],
                    similarity=0.0,
                    change_type=ChangeType.ADDED
                )
                matches.append(match)

        return matches

    def _greedy_matching(
        self,
        old_paragraphs: List[str],
        new_paragraphs: List[str],
        similarity_matrix
    ) -> List[ParagraphMatch]:
        """Fallback greedy matching when scipy not available"""
        matches = []
        n_old = len(old_paragraphs)
        n_new = len(new_paragraphs)

        matched_old = set()
        matched_new = set()

        # Greedy: match highest similarity first
        while True:
            max_sim = 0
            max_i, max_j = -1, -1

            for i in range(n_old):
                if i in matched_old:
                    continue
                for j in range(n_new):
                    if j in matched_new:
                        continue
                    # Handle both numpy array and list of lists
                    sim = similarity_matrix[i][j] if isinstance(similarity_matrix, list) else similarity_matrix[i, j]
                    if sim > max_sim:
                        max_sim = sim
                        max_i, max_j = i, j

            if max_sim < self.similarity_threshold:
                break

            # Create match
            change_type = ChangeType.UNCHANGED if max_sim > 0.95 else ChangeType.MODIFIED
            match = ParagraphMatch(
                old_index=max_i,
                new_index=max_j,
                old_text=old_paragraphs[max_i],
                new_text=new_paragraphs[max_j],
                similarity=max_sim,
                change_type=change_type
            )
            matches.append(match)
            matched_old.add(max_i)
            matched_new.add(max_j)

        # Add unmatched
        for i in range(n_old):
            if i not in matched_old:
                matches.append(ParagraphMatch(
                    old_index=i, new_index=-1,
                    old_text=old_paragraphs[i], new_text="",
                    similarity=0.0, change_type=ChangeType.DELETED
                ))

        for j in range(n_new):
            if j not in matched_new:
                matches.append(ParagraphMatch(
                    old_index=-1, new_index=j,
                    old_text="", new_text=new_paragraphs[j],
                    similarity=0.0, change_type=ChangeType.ADDED
                ))

        return matches

    def _detect_moves(
        self,
        matches: List[ParagraphMatch],
        similarity_matrix
    ) -> List[ParagraphMatch]:
        """Detect if paragraphs were moved (reordered)"""
        for match in matches:
            if match.change_type == ChangeType.MODIFIED:
                # Check if high similarity but different position
                if match.similarity >= self.move_detection_threshold:
                    # Check if position changed significantly
                    if abs(match.old_index - match.new_index) > 2:
                        match.is_moved = True
                        match.change_type = ChangeType.MOVED

        return matches

    def _classify_severity(self, matches: List[ParagraphMatch]) -> List[ParagraphMatch]:
        """Classify severity of each change"""
        for match in matches:
            if match.change_type == ChangeType.UNCHANGED:
                match.severity = ChangeSeverity.TRIVIAL
                continue

            # Check for critical keywords
            text = (match.old_text + " " + match.new_text).lower()
            has_critical_keyword = any(kw in text for kw in self.critical_keywords)

            if has_critical_keyword:
                match.severity = ChangeSeverity.CRITICAL
            elif match.change_type in [ChangeType.ADDED, ChangeType.DELETED]:
                match.severity = ChangeSeverity.MAJOR
            elif match.similarity < 0.5:
                match.severity = ChangeSeverity.MAJOR
            elif match.similarity < 0.85:
                match.severity = ChangeSeverity.MINOR
            else:
                match.severity = ChangeSeverity.TRIVIAL

        return matches

    def _generate_explanations(self, matches: List[ParagraphMatch]) -> List[ParagraphMatch]:
        """Generate human-readable explanations for changes"""
        for match in matches:
            if match.change_type == ChangeType.UNCHANGED:
                match.explanation = "No changes detected"
            elif match.change_type == ChangeType.ADDED:
                match.explanation = f"New paragraph added at position {match.new_index + 1}"
            elif match.change_type == ChangeType.DELETED:
                match.explanation = f"Paragraph removed from position {match.old_index + 1}"
            elif match.change_type == ChangeType.MOVED:
                match.explanation = f"Paragraph moved from position {match.old_index + 1} to {match.new_index + 1}"
            elif match.change_type == ChangeType.MODIFIED:
                sim_percent = match.similarity * 100
                match.explanation = f"Content modified (similarity: {sim_percent:.1f}%)"

        return matches

    def _build_result(
        self,
        matches: List[ParagraphMatch],
        total_old: int,
        total_new: int
    ) -> ComparisonResult:
        """Build complete comparison result"""
        result = ComparisonResult(
            matches=matches,
            total_old=total_old,
            total_new=total_new
        )

        # Count changes
        for match in matches:
            if match.change_type == ChangeType.UNCHANGED:
                result.unchanged_count += 1
            elif match.change_type == ChangeType.MODIFIED:
                result.modified_count += 1
            elif match.change_type == ChangeType.ADDED:
                result.added_count += 1
            elif match.change_type == ChangeType.DELETED:
                result.deleted_count += 1
            elif match.change_type == ChangeType.MOVED:
                result.moved_count += 1

            # Track critical and major changes
            if match.severity == ChangeSeverity.CRITICAL:
                result.critical_changes.append(match)
            elif match.severity == ChangeSeverity.MAJOR:
                result.major_changes.append(match)

        # Calculate average similarity
        if matches:
            total_similarity = sum(m.similarity for m in matches)
            result.average_similarity = total_similarity / len(matches)

        return result


def main():
    """Example usage and testing"""
    print("=" * 60)
    print("SEMANTIC COMPARATOR TEST")
    print("=" * 60)

    # Initialize comparator
    comparator = SemanticComparator(similarity_threshold=0.7)

    # Test documents
    old_doc = [
        "The system must authenticate users before granting access.",
        "Data shall be encrypted using AES-256 standard.",
        "The application should provide a user-friendly interface.",
        "Performance requirements: response time under 2 seconds."
    ]

    new_doc = [
        "Users must be authenticated before access is granted.",
        "All data should be encrypted with AES-256 encryption.",
        "The UI must be intuitive and easy to use.",
        "System must support at least 1000 concurrent users.",
        "Response time should be under 2 seconds for best performance."
    ]

    print("\n[TEST] Comparing documents...")
    print(f"Old document: {len(old_doc)} paragraphs")
    print(f"New document: {len(new_doc)} paragraphs")

    # Compare
    result = comparator.compare_paragraphs(old_doc, new_doc)

    print("\n[RESULTS]")
    print(f"Total changes: {len(result.matches)}")
    print(f"Unchanged: {result.unchanged_count}")
    print(f"Modified: {result.modified_count}")
    print(f"Added: {result.added_count}")
    print(f"Deleted: {result.deleted_count}")
    print(f"Moved: {result.moved_count}")
    print(f"Average similarity: {result.average_similarity:.2%}")

    print(f"\nCritical changes: {len(result.critical_changes)}")
    print(f"Major changes: {len(result.major_changes)}")

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
