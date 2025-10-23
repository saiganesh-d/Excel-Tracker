"""
PDF Document Structure Comparison Tool
Intelligently compares PDF documents by extracting and matching
hierarchical structures (chapters, sections, subsections)
"""

import pdfplumber
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from difflib import SequenceMatcher
import numpy as np
from collections import defaultdict


@dataclass
class Section:
    """Represents a section in the document with hierarchical structure"""
    level: int  # 1=Chapter, 2=Section, 3=Subsection, etc.
    title: str
    content: str
    page_number: int
    parent_id: Optional[str] = None
    section_id: str = ""
    children: List['Section'] = field(default_factory=list)

    def __post_init__(self):
        if not self.section_id:
            # Generate unique ID based on level and title
            self.section_id = f"{self.level}_{self.title[:50].replace(' ', '_')}"

    def get_full_path(self) -> str:
        """Get full hierarchical path (e.g., '1.2.3 Section Name')"""
        return self.title

    def to_dict(self) -> Dict:
        """Convert to dictionary for export"""
        return {
            'level': self.level,
            'title': self.title,
            'content': self.content[:200] + '...' if len(self.content) > 200 else self.content,
            'page': self.page_number,
            'section_id': self.section_id,
            'children_count': len(self.children)
        }


@dataclass
class SectionMatch:
    """Represents a matched pair of sections"""
    original_section: Optional[Section]
    modified_section: Optional[Section]
    match_score: float  # 0-100
    change_type: str  # 'unchanged', 'modified', 'added', 'removed', 'reordered'
    content_changes: List[Tuple[str, str, str]] = field(default_factory=list)  # (change_type, old, new)

    def has_content_changes(self) -> bool:
        return len(self.content_changes) > 0


class PDFStructureExtractor:
    """Extract hierarchical structure from PDF documents"""

    def __init__(self):
        # Patterns to identify headings (customizable for different document formats)
        self.heading_patterns = [
            # Chapter patterns: "1. Introduction", "Chapter 1:", "CHAPTER 1"
            (r'^(?:CHAPTER\s+)?(\d+)[\.\:\s]+(.+)$', 1),
            (r'^([A-Z][A-Z\s]{2,})\s*$', 1),  # ALL CAPS headings

            # Section patterns: "1.1 Overview", "1.1. Overview"
            (r'^(\d+\.\d+)[\.\s]+(.+)$', 2),

            # Subsection patterns: "1.1.1 Details"
            (r'^(\d+\.\d+\.\d+)[\.\s]+(.+)$', 3),

            # Sub-subsection: "1.1.1.1 Item"
            (r'^(\d+\.\d+\.\d+\.\d+)[\.\s]+(.+)$', 4),

            # Letter-based sections: "A. Section", "a) Subsection"
            (r'^([A-Z])[\.\)]\s+(.+)$', 2),
            (r'^([a-z])[\.\)]\s+(.+)$', 3),

            # Roman numerals: "I. Section", "ii. Subsection"
            (r'^([IVX]+)[\.\)]\s+(.+)$', 2),
            (r'^([ivx]+)[\.\)]\s+(.+)$', 3),
        ]

        self.sections: List[Section] = []

    def extract_from_pdf(self, pdf_path) -> List[Section]:
        """Extract structured sections from PDF"""
        sections = []
        current_section = None
        content_buffer = []

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if not text:
                    continue

                lines = text.split('\n')

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    # Check if line is a heading
                    heading_info = self._identify_heading(line)

                    if heading_info:
                        # Save previous section if exists
                        if current_section:
                            current_section.content = '\n'.join(content_buffer).strip()
                            sections.append(current_section)
                            content_buffer = []

                        # Create new section
                        level, title = heading_info
                        current_section = Section(
                            level=level,
                            title=title,
                            content="",
                            page_number=page_num
                        )
                    else:
                        # Add to content buffer
                        if current_section:
                            content_buffer.append(line)

        # Don't forget the last section
        if current_section:
            current_section.content = '\n'.join(content_buffer).strip()
            sections.append(current_section)

        self.sections = sections
        return sections

    def _identify_heading(self, line: str) -> Optional[Tuple[int, str]]:
        """Identify if a line is a heading and return (level, title)"""
        # Check against all patterns
        for pattern, default_level in self.heading_patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                # Extract title (handling different pattern groups)
                if len(match.groups()) >= 2:
                    title = match.group(2).strip()
                else:
                    title = match.group(0).strip()

                # Determine level based on numbering depth
                if '.' in match.group(1) if match.lastindex >= 1 else '':
                    level = match.group(1).count('.') + 1
                else:
                    level = default_level

                return (level, title)

        # Check for bold/large text (requires font analysis)
        # This is a heuristic: short lines with specific characteristics
        if len(line) < 100 and len(line.split()) <= 10:
            # Check if line looks like a heading (title case, short)
            if line.istitle() or line.isupper():
                # Estimate level based on context
                return (self._estimate_level_from_context(line), line)

        return None

    def _estimate_level_from_context(self, line: str) -> int:
        """Estimate heading level from context when no clear numbering exists"""
        if line.isupper() and len(line) < 50:
            return 1  # Chapter level
        elif line.istitle():
            return 2  # Section level
        return 3  # Subsection level

    def build_hierarchy(self) -> List[Section]:
        """Build parent-child relationships between sections"""
        if not self.sections:
            return []

        root_sections = []
        stack = []  # Stack to track parent sections at each level

        for section in self.sections:
            # Pop stack until we find appropriate parent
            while stack and stack[-1].level >= section.level:
                stack.pop()

            # Set parent if stack has items
            if stack:
                section.parent_id = stack[-1].section_id
                stack[-1].children.append(section)
            else:
                root_sections.append(section)

            # Add current section to stack
            stack.append(section)

        return root_sections


class PDFStructureComparator:
    """Compare two PDF documents by their structure and content"""

    def __init__(self, original_pdf_path, modified_pdf_path):
        self.original_path = original_pdf_path
        self.modified_path = modified_pdf_path

        # Extract structures
        self.original_extractor = PDFStructureExtractor()
        self.modified_extractor = PDFStructureExtractor()

        self.original_sections = []
        self.modified_sections = []

        self.matches: List[SectionMatch] = []
        self.summary = {
            'total_sections_original': 0,
            'total_sections_modified': 0,
            'unchanged': 0,
            'modified': 0,
            'added': 0,
            'removed': 0,
            'reordered': 0
        }

    def compare(self) -> List[SectionMatch]:
        """Perform full comparison"""
        # Extract sections from both PDFs
        self.original_sections = self.original_extractor.extract_from_pdf(self.original_path)
        self.modified_sections = self.modified_extractor.extract_from_pdf(self.modified_path)

        self.summary['total_sections_original'] = len(self.original_sections)
        self.summary['total_sections_modified'] = len(self.modified_sections)

        # Match sections using intelligent algorithm
        self.matches = self._match_sections()

        # Analyze content changes for matched sections
        for match in self.matches:
            if match.original_section and match.modified_section:
                match.content_changes = self._compare_content(
                    match.original_section.content,
                    match.modified_section.content
                )

        # Update summary statistics
        self._update_summary()

        return self.matches

    def _match_sections(self) -> List[SectionMatch]:
        """Intelligently match sections between documents"""
        matches = []
        used_modified_indices = set()

        # First pass: exact title matches
        for orig_idx, orig_section in enumerate(self.original_sections):
            best_match_idx = None
            best_score = 0

            for mod_idx, mod_section in enumerate(self.modified_sections):
                if mod_idx in used_modified_indices:
                    continue

                # Calculate similarity score
                score = self._calculate_similarity(orig_section, mod_section)

                if score > best_score and score > 60:  # Threshold for matching
                    best_score = score
                    best_match_idx = mod_idx

            if best_match_idx is not None:
                # Found a match
                mod_section = self.modified_sections[best_match_idx]
                used_modified_indices.add(best_match_idx)

                # Determine change type
                if best_score > 95 and orig_section.content == mod_section.content:
                    change_type = 'unchanged'
                elif abs(orig_idx - best_match_idx) > 2:
                    change_type = 'reordered'
                else:
                    change_type = 'modified'

                matches.append(SectionMatch(
                    original_section=orig_section,
                    modified_section=mod_section,
                    match_score=best_score,
                    change_type=change_type
                ))
            else:
                # No match found - section was removed
                matches.append(SectionMatch(
                    original_section=orig_section,
                    modified_section=None,
                    match_score=0,
                    change_type='removed'
                ))

        # Second pass: find added sections
        for mod_idx, mod_section in enumerate(self.modified_sections):
            if mod_idx not in used_modified_indices:
                matches.append(SectionMatch(
                    original_section=None,
                    modified_section=mod_section,
                    match_score=0,
                    change_type='added'
                ))

        # Sort matches by original position (keeping removed at end)
        matches.sort(key=lambda m: (
            m.original_section.page_number if m.original_section else 999,
            m.modified_section.page_number if m.modified_section else 999
        ))

        return matches

    def _calculate_similarity(self, section1: Section, section2: Section) -> float:
        """Calculate similarity score between two sections (0-100)"""
        # Title similarity (weighted heavily)
        title_similarity = SequenceMatcher(None,
                                          section1.title.lower(),
                                          section2.title.lower()).ratio()

        # Level match bonus
        level_match = 1.0 if section1.level == section2.level else 0.5

        # Content similarity (if titles are similar)
        content_similarity = 0
        if title_similarity > 0.6:
            content_similarity = SequenceMatcher(None,
                                                section1.content[:500].lower(),
                                                section2.content[:500].lower()).ratio()

        # Weighted score
        score = (title_similarity * 0.6 + content_similarity * 0.3 + level_match * 0.1) * 100

        return score

    def _compare_content(self, original_content: str, modified_content: str) -> List[Tuple[str, str, str]]:
        """Compare content and return list of changes"""
        if original_content == modified_content:
            return []

        changes = []

        # Split into sentences/paragraphs for granular comparison
        orig_lines = [line.strip() for line in original_content.split('\n') if line.strip()]
        mod_lines = [line.strip() for line in modified_content.split('\n') if line.strip()]

        # Use SequenceMatcher to find differences
        matcher = SequenceMatcher(None, orig_lines, mod_lines)

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                old_text = '\n'.join(orig_lines[i1:i2])
                new_text = '\n'.join(mod_lines[j1:j2])
                changes.append(('modified', old_text, new_text))
            elif tag == 'delete':
                old_text = '\n'.join(orig_lines[i1:i2])
                changes.append(('deleted', old_text, ''))
            elif tag == 'insert':
                new_text = '\n'.join(mod_lines[j1:j2])
                changes.append(('added', '', new_text))

        return changes

    def _update_summary(self):
        """Update summary statistics based on matches"""
        for match in self.matches:
            if match.change_type == 'unchanged':
                self.summary['unchanged'] += 1
            elif match.change_type == 'modified':
                self.summary['modified'] += 1
            elif match.change_type == 'added':
                self.summary['added'] += 1
            elif match.change_type == 'removed':
                self.summary['removed'] += 1
            elif match.change_type == 'reordered':
                self.summary['reordered'] += 1

    def get_summary(self) -> Dict:
        """Get comparison summary"""
        return self.summary

    def export_to_dict(self) -> Dict:
        """Export comparison results to dictionary"""
        return {
            'summary': self.summary,
            'matches': [
                {
                    'original': match.original_section.to_dict() if match.original_section else None,
                    'modified': match.modified_section.to_dict() if match.modified_section else None,
                    'match_score': match.match_score,
                    'change_type': match.change_type,
                    'content_changes_count': len(match.content_changes)
                }
                for match in self.matches
            ]
        }


class PDFComparisonAnalyzer:
    """Advanced analysis tools for PDF comparison results"""

    @staticmethod
    def find_critical_changes(matches: List[SectionMatch],
                            critical_keywords: List[str]) -> List[SectionMatch]:
        """Find changes in sections containing critical keywords"""
        critical_changes = []

        for match in matches:
            if match.change_type in ['removed', 'modified']:
                # Check if section contains critical keywords
                section = match.original_section or match.modified_section
                if section:
                    content_lower = (section.title + ' ' + section.content).lower()
                    if any(keyword.lower() in content_lower for keyword in critical_keywords):
                        critical_changes.append(match)

        return critical_changes

    @staticmethod
    def detect_structural_changes(original_sections: List[Section],
                                 modified_sections: List[Section]) -> Dict:
        """Detect high-level structural changes"""

        # Count sections by level
        orig_by_level = defaultdict(int)
        mod_by_level = defaultdict(int)

        for section in original_sections:
            orig_by_level[section.level] += 1

        for section in modified_sections:
            mod_by_level[section.level] += 1

        # Detect changes
        structural_changes = {
            'chapter_count_change': mod_by_level[1] - orig_by_level[1],
            'section_count_change': mod_by_level[2] - orig_by_level[2],
            'subsection_count_change': mod_by_level[3] - orig_by_level[3],
            'total_hierarchy_levels_original': max(orig_by_level.keys()) if orig_by_level else 0,
            'total_hierarchy_levels_modified': max(mod_by_level.keys()) if mod_by_level else 0
        }

        return structural_changes

    @staticmethod
    def generate_change_report(comparator: PDFStructureComparator) -> str:
        """Generate a human-readable change report"""
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("PDF STRUCTURE COMPARISON REPORT")
        report_lines.append("=" * 80)
        report_lines.append("")

        # Summary
        summary = comparator.summary
        report_lines.append("SUMMARY")
        report_lines.append("-" * 80)
        report_lines.append(f"Original Sections: {summary['total_sections_original']}")
        report_lines.append(f"Modified Sections: {summary['total_sections_modified']}")
        report_lines.append(f"Unchanged: {summary['unchanged']}")
        report_lines.append(f"Modified: {summary['modified']}")
        report_lines.append(f"Added: {summary['added']}")
        report_lines.append(f"Removed: {summary['removed']}")
        report_lines.append(f"Reordered: {summary['reordered']}")
        report_lines.append("")

        # Detailed changes
        report_lines.append("DETAILED CHANGES")
        report_lines.append("-" * 80)

        for idx, match in enumerate(comparator.matches, 1):
            if match.change_type == 'unchanged':
                continue

            report_lines.append(f"\n{idx}. [{match.change_type.upper()}]")

            if match.original_section:
                report_lines.append(f"   Original: {match.original_section.title} (Page {match.original_section.page_number})")

            if match.modified_section:
                report_lines.append(f"   Modified: {match.modified_section.title} (Page {match.modified_section.page_number})")

            if match.match_score > 0:
                report_lines.append(f"   Match Score: {match.match_score:.1f}%")

            if match.content_changes:
                report_lines.append(f"   Content Changes: {len(match.content_changes)} modifications detected")

        return '\n'.join(report_lines)
