"""
Requirement Analyzer - Detect and classify requirements in documents

This module analyzes text to identify requirements (must/shall/should) and
classifies them by type, priority, and importance. Essential for comparing
technical specifications, contracts, and legal documents.

Key Features:
- Requirement keyword detection (must, shall, should, may, etc.)
- Requirement type classification (functional, non-functional, constraint)
- Priority levels (mandatory, recommended, optional)
- Change tracking for requirements
- Multi-language support (English, German)

Author: Advanced PDF Comparison System
Date: 2025-10-30
"""

import re
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum


class RequirementLevel(Enum):
    """Requirement priority levels (RFC 2119 compliant)"""
    MUST = "must"           # Absolute requirement
    SHALL = "shall"         # Absolute requirement (formal)
    REQUIRED = "required"   # Absolute requirement
    SHOULD = "should"       # Recommended
    RECOMMENDED = "recommended"  # Recommended
    MAY = "may"             # Optional
    OPTIONAL = "optional"   # Optional
    MUST_NOT = "must_not"   # Absolute prohibition
    SHALL_NOT = "shall_not" # Absolute prohibition


class RequirementType(Enum):
    """Types of requirements"""
    FUNCTIONAL = "functional"           # What the system must do
    NON_FUNCTIONAL = "non_functional"   # Quality attributes (performance, security)
    CONSTRAINT = "constraint"           # Limitations and restrictions
    INTERFACE = "interface"             # System interfaces
    DATA = "data"                       # Data requirements
    LEGAL = "legal"                     # Legal/compliance requirements
    BUSINESS = "business"               # Business rules
    UNKNOWN = "unknown"                 # Could not classify


@dataclass
class Requirement:
    """
    Represents a single requirement detected in text

    Attributes:
        text: Full text of the requirement
        level: Priority level (must/shall/should/may)
        type: Type of requirement (functional, non-functional, etc.)
        keywords: Keywords that identified this as a requirement
        position: Character position in original text
        paragraph_index: Index of paragraph containing requirement
        is_prohibition: Whether this is a negative requirement (must not)
        confidence: Confidence score (0-1) that this is a requirement
    """
    text: str
    level: RequirementLevel
    type: RequirementType = RequirementType.UNKNOWN
    keywords: List[str] = field(default_factory=list)
    position: int = 0
    paragraph_index: int = 0
    is_prohibition: bool = False
    confidence: float = 1.0

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'text': self.text,
            'level': self.level.value,
            'type': self.type.value,
            'keywords': self.keywords,
            'position': self.position,
            'paragraph_index': self.paragraph_index,
            'is_prohibition': self.is_prohibition,
            'confidence': round(self.confidence, 2)
        }


@dataclass
class RequirementChange:
    """
    Represents a change in requirements between documents

    Attributes:
        old_requirement: Requirement from old document (None if added)
        new_requirement: Requirement from new document (None if removed)
        change_type: Type of change (added, removed, modified, level_changed)
        severity: Impact of change (critical, major, minor)
        explanation: Human-readable explanation
    """
    old_requirement: Optional[Requirement]
    new_requirement: Optional[Requirement]
    change_type: str  # 'added', 'removed', 'modified', 'level_changed', 'unchanged'
    severity: str = 'minor'  # 'critical', 'major', 'minor'
    explanation: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'old_requirement': self.old_requirement.to_dict() if self.old_requirement else None,
            'new_requirement': self.new_requirement.to_dict() if self.new_requirement else None,
            'change_type': self.change_type,
            'severity': self.severity,
            'explanation': self.explanation
        }


class RequirementAnalyzer:
    """
    Analyze text to detect and classify requirements

    This class identifies requirement statements in documents using
    keyword detection and pattern matching. It supports multiple languages
    and requirement standards (RFC 2119, IEEE 830).
    """

    # Requirement keywords by level (English)
    MUST_KEYWORDS = [
        'must', 'required', 'shall', 'needs to', 'has to', 'is required to',
        'is mandatory', 'mandatory', 'obligatory', 'compulsory'
    ]

    SHOULD_KEYWORDS = [
        'should', 'recommended', 'it is recommended', 'ought to',
        'advisable', 'suggested', 'preferred'
    ]

    MAY_KEYWORDS = [
        'may', 'optional', 'can', 'could', 'might', 'possibly',
        'optionally', 'at discretion'
    ]

    PROHIBITION_KEYWORDS = [
        'must not', 'shall not', 'may not', 'cannot', 'prohibited',
        'forbidden', 'not allowed', 'not permitted'
    ]

    # German requirement keywords
    GERMAN_MUST_KEYWORDS = [
        'muss', 'müssen', 'erforderlich', 'notwendig', 'zwingend',
        'verpflichtend', 'obligatorisch'
    ]

    GERMAN_SHOULD_KEYWORDS = [
        'soll', 'sollte', 'empfohlen', 'ratsam', 'angeraten'
    ]

    GERMAN_MAY_KEYWORDS = [
        'kann', 'könnte', 'darf', 'optional', 'möglich'
    ]

    # Type classification keywords
    FUNCTIONAL_KEYWORDS = [
        'function', 'feature', 'capability', 'operation', 'behavior',
        'process', 'calculate', 'display', 'provide', 'enable'
    ]

    NON_FUNCTIONAL_KEYWORDS = [
        'performance', 'speed', 'response time', 'throughput', 'latency',
        'security', 'reliability', 'availability', 'scalability',
        'usability', 'maintainability', 'portability'
    ]

    CONSTRAINT_KEYWORDS = [
        'constraint', 'limitation', 'restriction', 'bound by', 'limited to',
        'not exceed', 'maximum', 'minimum', 'within', 'comply with'
    ]

    LEGAL_KEYWORDS = [
        'legal', 'regulation', 'compliance', 'law', 'statute',
        'gdpr', 'hipaa', 'iso', 'standard', 'audit', 'liability'
    ]

    INTERFACE_KEYWORDS = [
        'interface', 'api', 'protocol', 'communication', 'integration',
        'connect', 'interact', 'exchange'
    ]

    DATA_KEYWORDS = [
        'data', 'database', 'storage', 'information', 'record',
        'file', 'format', 'structure'
    ]

    def __init__(
        self,
        language: str = 'en',
        min_confidence: float = 0.6,
        detect_german: bool = True
    ):
        """
        Initialize requirement analyzer

        Args:
            language: Primary language ('en' or 'de')
            min_confidence: Minimum confidence to consider as requirement
            detect_german: Whether to detect German requirements
        """
        self.language = language
        self.min_confidence = min_confidence
        self.detect_german = detect_german

        print(f"[i] RequirementAnalyzer initialized")
        print(f"    Language: {language}")
        print(f"    Min confidence: {min_confidence}")
        print(f"    German detection: {detect_german}")

    def analyze_text(self, text: str) -> List[Requirement]:
        """
        Analyze text to find all requirements

        Args:
            text: Text to analyze

        Returns:
            List of detected requirements
        """
        requirements = []

        # Split into sentences
        sentences = self._split_sentences(text)

        for i, sentence in enumerate(sentences):
            # Check if sentence contains requirements
            req = self._analyze_sentence(sentence, position=i)
            if req:
                requirements.append(req)

        return requirements

    def analyze_paragraphs(
        self,
        paragraphs: List[str]
    ) -> List[Requirement]:
        """
        Analyze list of paragraphs to find requirements

        Args:
            paragraphs: List of paragraph texts

        Returns:
            List of detected requirements with paragraph indices
        """
        requirements = []

        for para_idx, paragraph in enumerate(paragraphs):
            # Split paragraph into sentences
            sentences = self._split_sentences(paragraph)

            for sent_idx, sentence in enumerate(sentences):
                req = self._analyze_sentence(
                    sentence,
                    position=sent_idx,
                    paragraph_index=para_idx
                )
                if req:
                    requirements.append(req)

        return requirements

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting (can be improved with nltk)
        # Split on . ! ? followed by space and capital letter
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
        return [s.strip() for s in sentences if s.strip()]

    def _analyze_sentence(
        self,
        sentence: str,
        position: int = 0,
        paragraph_index: int = 0
    ) -> Optional[Requirement]:
        """
        Analyze a single sentence for requirements

        Args:
            sentence: Sentence text
            position: Position in document
            paragraph_index: Index of containing paragraph

        Returns:
            Requirement object or None
        """
        sentence_lower = sentence.lower()

        # Check for prohibition first (must not, shall not)
        is_prohibition, prohibition_keywords = self._check_prohibition(sentence_lower)

        # Check requirement level
        level, level_keywords = self._detect_level(sentence_lower, is_prohibition)

        if level is None:
            return None  # Not a requirement

        # Classify requirement type
        req_type = self._classify_type(sentence_lower)

        # Calculate confidence
        confidence = self._calculate_confidence(
            sentence_lower,
            level_keywords,
            req_type
        )

        if confidence < self.min_confidence:
            return None

        # Create requirement
        req = Requirement(
            text=sentence,
            level=level,
            type=req_type,
            keywords=level_keywords + prohibition_keywords,
            position=position,
            paragraph_index=paragraph_index,
            is_prohibition=is_prohibition,
            confidence=confidence
        )

        return req

    def _check_prohibition(self, text: str) -> Tuple[bool, List[str]]:
        """Check if text contains prohibition keywords"""
        found_keywords = []

        for keyword in self.PROHIBITION_KEYWORDS:
            if keyword in text:
                found_keywords.append(keyword)

        return len(found_keywords) > 0, found_keywords

    def _detect_level(
        self,
        text: str,
        is_prohibition: bool
    ) -> Tuple[Optional[RequirementLevel], List[str]]:
        """
        Detect requirement level from text

        Returns:
            (RequirementLevel, list of keywords found)
        """
        found_keywords = []

        # Check for prohibition levels
        if is_prohibition:
            if any(kw in text for kw in ['must not', 'shall not']):
                return RequirementLevel.MUST_NOT, ['must not']
            return RequirementLevel.SHALL_NOT, ['shall not']

        # Check MUST level (highest priority)
        for keyword in self.MUST_KEYWORDS:
            if keyword in text:
                found_keywords.append(keyword)

        if found_keywords:
            if 'shall' in found_keywords:
                return RequirementLevel.SHALL, found_keywords
            return RequirementLevel.MUST, found_keywords

        # Check German MUST keywords
        if self.detect_german:
            for keyword in self.GERMAN_MUST_KEYWORDS:
                if keyword in text:
                    found_keywords.append(keyword)
            if found_keywords:
                return RequirementLevel.MUST, found_keywords

        # Check SHOULD level
        for keyword in self.SHOULD_KEYWORDS:
            if keyword in text:
                found_keywords.append(keyword)

        if found_keywords:
            return RequirementLevel.SHOULD, found_keywords

        # Check German SHOULD keywords
        if self.detect_german:
            for keyword in self.GERMAN_SHOULD_KEYWORDS:
                if keyword in text:
                    found_keywords.append(keyword)
            if found_keywords:
                return RequirementLevel.SHOULD, found_keywords

        # Check MAY level (lowest priority)
        for keyword in self.MAY_KEYWORDS:
            if keyword in text:
                found_keywords.append(keyword)

        if found_keywords:
            return RequirementLevel.MAY, found_keywords

        # Check German MAY keywords
        if self.detect_german:
            for keyword in self.GERMAN_MAY_KEYWORDS:
                if keyword in text:
                    found_keywords.append(keyword)
            if found_keywords:
                return RequirementLevel.MAY, found_keywords

        return None, []

    def _classify_type(self, text: str) -> RequirementType:
        """Classify requirement type based on keywords"""
        # Count keywords for each type
        scores = {}

        # Functional
        functional_count = sum(1 for kw in self.FUNCTIONAL_KEYWORDS if kw in text)
        scores[RequirementType.FUNCTIONAL] = functional_count

        # Non-functional
        nonfunc_count = sum(1 for kw in self.NON_FUNCTIONAL_KEYWORDS if kw in text)
        scores[RequirementType.NON_FUNCTIONAL] = nonfunc_count

        # Constraint
        constraint_count = sum(1 for kw in self.CONSTRAINT_KEYWORDS if kw in text)
        scores[RequirementType.CONSTRAINT] = constraint_count

        # Legal
        legal_count = sum(1 for kw in self.LEGAL_KEYWORDS if kw in text)
        scores[RequirementType.LEGAL] = legal_count

        # Interface
        interface_count = sum(1 for kw in self.INTERFACE_KEYWORDS if kw in text)
        scores[RequirementType.INTERFACE] = interface_count

        # Data
        data_count = sum(1 for kw in self.DATA_KEYWORDS if kw in text)
        scores[RequirementType.DATA] = data_count

        # Return type with highest score
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)

        return RequirementType.UNKNOWN

    def _calculate_confidence(
        self,
        text: str,
        keywords: List[str],
        req_type: RequirementType
    ) -> float:
        """
        Calculate confidence that this is a requirement

        Factors:
        - Number of requirement keywords
        - Sentence structure
        - Presence of verbs
        - Type classification success
        """
        confidence = 0.5  # Base confidence

        # Boost for multiple keywords
        confidence += min(len(keywords) * 0.1, 0.2)

        # Boost for successful type classification
        if req_type != RequirementType.UNKNOWN:
            confidence += 0.2

        # Boost for sentence length (requirements tend to be substantial)
        word_count = len(text.split())
        if 5 <= word_count <= 50:
            confidence += 0.1

        # Ensure between 0 and 1
        return min(max(confidence, 0.0), 1.0)

    def compare_requirements(
        self,
        old_requirements: List[Requirement],
        new_requirements: List[Requirement],
        similarity_threshold: float = 0.7
    ) -> List[RequirementChange]:
        """
        Compare requirements between two documents

        Args:
            old_requirements: Requirements from old document
            new_requirements: Requirements from new document
            similarity_threshold: Minimum similarity to consider same requirement

        Returns:
            List of requirement changes
        """
        changes = []
        matched_new = set()

        # Find matching and modified requirements
        for old_req in old_requirements:
            best_match = None
            best_similarity = 0.0

            for i, new_req in enumerate(new_requirements):
                if i in matched_new:
                    continue

                similarity = self._requirement_similarity(old_req, new_req)

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = (i, new_req)

            if best_match and best_similarity >= similarity_threshold:
                matched_new.add(best_match[0])
                new_req = best_match[1]

                # Check if requirement changed
                if old_req.level != new_req.level:
                    change = RequirementChange(
                        old_requirement=old_req,
                        new_requirement=new_req,
                        change_type='level_changed',
                        severity='critical',
                        explanation=f"Requirement level changed from {old_req.level.value} to {new_req.level.value}"
                    )
                    changes.append(change)
                elif old_req.text != new_req.text:
                    change = RequirementChange(
                        old_requirement=old_req,
                        new_requirement=new_req,
                        change_type='modified',
                        severity='major',
                        explanation=f"Requirement text modified (similarity: {best_similarity:.0%})"
                    )
                    changes.append(change)
                else:
                    change = RequirementChange(
                        old_requirement=old_req,
                        new_requirement=new_req,
                        change_type='unchanged',
                        severity='minor',
                        explanation="No changes"
                    )
                    changes.append(change)
            else:
                # Requirement removed
                change = RequirementChange(
                    old_requirement=old_req,
                    new_requirement=None,
                    change_type='removed',
                    severity='critical',
                    explanation=f"{old_req.level.value.upper()} requirement removed"
                )
                changes.append(change)

        # Find added requirements
        for i, new_req in enumerate(new_requirements):
            if i not in matched_new:
                change = RequirementChange(
                    old_requirement=None,
                    new_requirement=new_req,
                    change_type='added',
                    severity='major' if new_req.level in [RequirementLevel.MUST, RequirementLevel.SHALL] else 'minor',
                    explanation=f"New {new_req.level.value.upper()} requirement added"
                )
                changes.append(change)

        return changes

    def _requirement_similarity(
        self,
        req1: Requirement,
        req2: Requirement
    ) -> float:
        """
        Calculate similarity between two requirements

        Uses simple word overlap (can be enhanced with semantic embeddings)
        """
        words1 = set(req1.text.lower().split())
        words2 = set(req2.text.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        return intersection / union if union > 0 else 0.0

    def get_statistics(self, requirements: List[Requirement]) -> Dict:
        """Get statistics about requirements"""
        if not requirements:
            return {
                'total': 0,
                'by_level': {},
                'by_type': {},
                'prohibitions': 0,
                'average_confidence': 0.0
            }

        # Count by level
        by_level = {}
        for req in requirements:
            level = req.level.value
            by_level[level] = by_level.get(level, 0) + 1

        # Count by type
        by_type = {}
        for req in requirements:
            req_type = req.type.value
            by_type[req_type] = by_type.get(req_type, 0) + 1

        # Count prohibitions
        prohibitions = sum(1 for req in requirements if req.is_prohibition)

        # Average confidence
        avg_confidence = sum(req.confidence for req in requirements) / len(requirements)

        return {
            'total': len(requirements),
            'by_level': by_level,
            'by_type': by_type,
            'prohibitions': prohibitions,
            'average_confidence': round(avg_confidence, 2)
        }


def main():
    """Example usage and testing"""
    print("=" * 60)
    print("REQUIREMENT ANALYZER TEST")
    print("=" * 60)

    # Initialize analyzer
    analyzer = RequirementAnalyzer(language='en', detect_german=True)

    # Test document
    test_text = """
    The system must authenticate all users before granting access.
    User passwords shall be encrypted using AES-256 standard.
    The application should provide a user-friendly interface.
    Response time may not exceed 2 seconds for normal operations.
    The system must not store passwords in plain text.
    Data shall be backed up daily to prevent loss.
    The interface should be intuitive and easy to navigate.
    Performance requirements: throughput must be at least 1000 requests per second.
    """

    print("\n[TEST] Analyzing requirements...")
    requirements = analyzer.analyze_text(test_text)

    print(f"\n[+] Found {len(requirements)} requirements:\n")

    for i, req in enumerate(requirements, 1):
        print(f"{i}. [{req.level.value.upper()}] {req.text[:70]}...")
        print(f"   Type: {req.type.value}")
        print(f"   Confidence: {req.confidence:.2f}")
        print(f"   Keywords: {', '.join(req.keywords)}")
        if req.is_prohibition:
            print(f"   [!] PROHIBITION")
        print()

    # Get statistics
    stats = analyzer.get_statistics(requirements)
    print("[STATISTICS]")
    print(f"Total requirements: {stats['total']}")
    print(f"By level: {stats['by_level']}")
    print(f"By type: {stats['by_type']}")
    print(f"Prohibitions: {stats['prohibitions']}")
    print(f"Average confidence: {stats['average_confidence']}")

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
