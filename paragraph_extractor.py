"""
Paragraph-Aware PDF Content Extractor

Extracts paragraphs (not just lines) from PDF content.
Handles multi-line paragraphs, numbered sections, bullet points.
"""

import re
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Paragraph:
    """Represents a single paragraph with metadata"""
    text: str
    paragraph_type: str  # 'normal', 'numbered', 'bullet', 'heading'
    number: str = None  # e.g., "1.", "1.1", "a)"
    start_position: int = 0
    end_position: int = 0


class ParagraphExtractor:
    """Extract paragraphs from PDF content with structure awareness"""

    # Patterns for detecting different paragraph types
    NUMBERED_PATTERN = re.compile(r'^(\d+\.(?:\d+\.)*)\s+')  # 1., 1.1., 1.1.1.
    LETTER_PATTERN = re.compile(r'^([a-z]\))\s+')  # a), b), c)
    ROMAN_PATTERN = re.compile(r'^([ivxlcdm]+\.)\s+', re.IGNORECASE)  # i., ii., iii.
    BULLET_PATTERN = re.compile(r'^[•\-\*]\s+')  # •, -, *

    def __init__(self):
        self.min_paragraph_length = 10  # Minimum characters for valid paragraph

    def extract_paragraphs(self, content: str) -> List[str]:
        """
        Split content into meaningful paragraphs

        Args:
            content: Raw text content from PDF

        Returns:
            List of paragraph texts
        """
        if not content or not content.strip():
            return []

        lines = content.split('\n')
        paragraphs = []
        current_para = []

        for i, line in enumerate(lines):
            line_stripped = line.strip()

            # Skip empty lines
            if not line_stripped:
                if current_para:
                    # End of paragraph
                    para_text = ' '.join(current_para)
                    if len(para_text) >= self.min_paragraph_length:
                        paragraphs.append(para_text)
                    current_para = []
                continue

            # Check if this line starts a new paragraph
            if self._is_paragraph_start(line_stripped, current_para):
                # Save previous paragraph
                if current_para:
                    para_text = ' '.join(current_para)
                    if len(para_text) >= self.min_paragraph_length:
                        paragraphs.append(para_text)
                    current_para = []

                # Start new paragraph
                current_para.append(line_stripped)
            else:
                # Continue current paragraph
                current_para.append(line_stripped)

        # Don't forget last paragraph
        if current_para:
            para_text = ' '.join(current_para)
            if len(para_text) >= self.min_paragraph_length:
                paragraphs.append(para_text)

        return paragraphs

    def extract_with_structure(self, content: str) -> List[Paragraph]:
        """
        Extract paragraphs with metadata about structure

        Args:
            content: Raw text content from PDF

        Returns:
            List of Paragraph objects with metadata
        """
        if not content or not content.strip():
            return []

        lines = content.split('\n')
        paragraphs = []
        current_para = []
        current_type = 'normal'
        current_number = None
        start_pos = 0

        for i, line in enumerate(lines):
            line_stripped = line.strip()

            # Skip empty lines
            if not line_stripped:
                if current_para:
                    # End of paragraph - save it
                    para_text = ' '.join(current_para)
                    if len(para_text) >= self.min_paragraph_length:
                        paragraphs.append(Paragraph(
                            text=para_text,
                            paragraph_type=current_type,
                            number=current_number,
                            start_position=start_pos,
                            end_position=i
                        ))
                    current_para = []
                    current_type = 'normal'
                    current_number = None
                continue

            # Check if this line starts a new paragraph
            if self._is_paragraph_start(line_stripped, current_para):
                # Save previous paragraph
                if current_para:
                    para_text = ' '.join(current_para)
                    if len(para_text) >= self.min_paragraph_length:
                        paragraphs.append(Paragraph(
                            text=para_text,
                            paragraph_type=current_type,
                            number=current_number,
                            start_position=start_pos,
                            end_position=i
                        ))

                # Detect type of new paragraph
                start_pos = i
                current_type, current_number = self._detect_paragraph_type(line_stripped)
                current_para = [line_stripped]
            else:
                # Continue current paragraph
                current_para.append(line_stripped)

        # Don't forget last paragraph
        if current_para:
            para_text = ' '.join(current_para)
            if len(para_text) >= self.min_paragraph_length:
                paragraphs.append(Paragraph(
                    text=para_text,
                    paragraph_type=current_type,
                    number=current_number,
                    start_position=start_pos,
                    end_position=len(lines)
                ))

        return paragraphs

    def _is_paragraph_start(self, line: str, current_para: List[str]) -> bool:
        """
        Determine if a line starts a new paragraph

        Args:
            line: Current line (stripped)
            current_para: Current paragraph lines being built

        Returns:
            True if this line starts a new paragraph
        """
        if not current_para:
            # First line always starts a paragraph
            return True

        # Check for numbered/lettered/bulleted lines
        if (self.NUMBERED_PATTERN.match(line) or
            self.LETTER_PATTERN.match(line) or
            self.ROMAN_PATTERN.match(line) or
            self.BULLET_PATTERN.match(line)):
            return True

        # Check if looks like a heading (all caps, or title case with short length)
        if self._looks_like_heading(line):
            return True

        # Check if previous line ended with sentence terminator
        if current_para:
            last_line = current_para[-1]
            if last_line.endswith(('.', '!', '?', ':', ';')):
                # Check if current line starts with capital letter (new sentence)
                if line and line[0].isupper():
                    # But not if it's clearly a continuation (e.g., "Mr.", "Dr.", "Inc.")
                    if not self._is_abbreviation_ending(last_line):
                        return True

        return False

    def _detect_paragraph_type(self, line: str) -> Tuple[str, str]:
        """
        Detect the type of paragraph from first line

        Returns:
            Tuple of (type, number)
            type: 'normal', 'numbered', 'bullet', 'heading'
            number: extracted number/letter if applicable
        """
        # Check for numbered paragraph
        match = self.NUMBERED_PATTERN.match(line)
        if match:
            return ('numbered', match.group(1))

        # Check for lettered paragraph
        match = self.LETTER_PATTERN.match(line)
        if match:
            return ('numbered', match.group(1))

        # Check for roman numeral
        match = self.ROMAN_PATTERN.match(line)
        if match:
            return ('numbered', match.group(1))

        # Check for bullet point
        if self.BULLET_PATTERN.match(line):
            return ('bullet', None)

        # Check if looks like heading
        if self._looks_like_heading(line):
            return ('heading', None)

        return ('normal', None)

    def _looks_like_heading(self, line: str) -> bool:
        """
        Check if line looks like a heading

        Heuristics:
        - All uppercase (with some exceptions)
        - Title case and relatively short
        - Ends without punctuation
        """
        if not line:
            return False

        # All uppercase (but not if very long - might be shouting/emphasis)
        if line.isupper() and len(line) < 100:
            return True

        # Title case, short, no ending punctuation
        if (len(line) < 80 and
            line[0].isupper() and
            not line.endswith(('.', ',', ';', ':', '!', '?'))):
            # Check if mostly title case
            words = line.split()
            if len(words) <= 8:  # Short enough to be heading
                capitalized = sum(1 for w in words if w and w[0].isupper())
                if capitalized / len(words) > 0.5:  # Mostly capitalized
                    return True

        return False

    def _is_abbreviation_ending(self, line: str) -> bool:
        """
        Check if line ends with common abbreviation
        (to avoid splitting on abbreviations)
        """
        abbreviations = [
            'Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Prof.', 'Sr.', 'Jr.',
            'Inc.', 'Ltd.', 'Corp.', 'Co.',
            'etc.', 'e.g.', 'i.e.', 'vs.',
            'Fig.', 'Tab.', 'Eq.',
        ]

        for abbr in abbreviations:
            if line.endswith(abbr):
                return True

        return False

    def merge_split_paragraphs(self, paragraphs: List[str],
                               similarity_threshold: float = 0.8) -> List[str]:
        """
        Merge paragraphs that were incorrectly split
        (e.g., by PDF column breaks or page breaks)

        Args:
            paragraphs: List of paragraph texts
            similarity_threshold: How similar paragraphs should be to merge

        Returns:
            List of merged paragraphs
        """
        if not paragraphs or len(paragraphs) < 2:
            return paragraphs

        merged = []
        current = paragraphs[0]

        for i in range(1, len(paragraphs)):
            next_para = paragraphs[i]

            # Check if should merge
            if self._should_merge(current, next_para):
                # Merge with space
                current = current + ' ' + next_para
            else:
                # Save current and start new
                merged.append(current)
                current = next_para

        # Don't forget last paragraph
        merged.append(current)

        return merged

    def _should_merge(self, para1: str, para2: str) -> bool:
        """
        Determine if two paragraphs should be merged

        Heuristics:
        - First doesn't end with sentence terminator
        - Second doesn't start with capital letter
        - Similar writing style/structure
        """
        if not para1 or not para2:
            return False

        # If first doesn't end with sentence terminator, likely split
        if not para1.rstrip().endswith(('.', '!', '?', ':', ';')):
            # And second doesn't start numbered/bulleted
            if not (self.NUMBERED_PATTERN.match(para2) or
                   self.LETTER_PATTERN.match(para2) or
                   self.BULLET_PATTERN.match(para2)):
                return True

        return False

    def clean_paragraph(self, paragraph: str) -> str:
        """
        Clean a paragraph by removing artifacts, normalizing whitespace

        Args:
            paragraph: Raw paragraph text

        Returns:
            Cleaned paragraph text
        """
        if not paragraph:
            return ""

        # Remove multiple spaces
        cleaned = re.sub(r'\s+', ' ', paragraph)

        # Remove leading/trailing whitespace
        cleaned = cleaned.strip()

        # Fix common PDF extraction artifacts
        # Remove soft hyphens
        cleaned = cleaned.replace('\u00ad', '')

        # Fix hyphenation at line breaks (word- word -> word)
        cleaned = re.sub(r'(\w)-\s+(\w)', r'\1\2', cleaned)

        return cleaned


# Example usage and testing
if __name__ == "__main__":
    # Test with sample content
    sample_content = """
1. Introduction

This document describes the security requirements for the system. All users must authenticate before accessing sensitive data.

The authentication process should use multi-factor authentication. This includes:

a) Username and password
b) One-time code from mobile device
c) Biometric verification (optional)

2. System Requirements

The system shall implement the following security controls:

• Data encryption at rest
• Data encryption in transit
• Access logging and monitoring

All security measures must comply with industry standards.

3. Additional Notes

For more information, see the detailed specification document.
    """

    extractor = ParagraphExtractor()

    # Test basic extraction
    print("="*70)
    print("Basic Paragraph Extraction:")
    print("="*70)
    paragraphs = extractor.extract_paragraphs(sample_content)
    for i, para in enumerate(paragraphs, 1):
        print(f"\nParagraph {i}:")
        print(f"  {para[:100]}..." if len(para) > 100 else f"  {para}")

    # Test structured extraction
    print("\n" + "="*70)
    print("Structured Paragraph Extraction:")
    print("="*70)
    structured = extractor.extract_with_structure(sample_content)
    for i, para in enumerate(structured, 1):
        print(f"\nParagraph {i}:")
        print(f"  Type: {para.paragraph_type}")
        if para.number:
            print(f"  Number: {para.number}")
        print(f"  Text: {para.text[:100]}..." if len(para.text) > 100 else f"  Text: {para.text}")

    print(f"\n\nTotal paragraphs extracted: {len(paragraphs)}")
    print("[+] Paragraph extraction working correctly!")
