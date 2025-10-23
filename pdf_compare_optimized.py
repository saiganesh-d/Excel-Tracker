"""
Optimized PDF Comparison - Fast Table of Contents approach
Extracts only headings first, then loads content on-demand
"""

import pdfplumber
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from difflib import SequenceMatcher
import warnings

# Suppress pattern warnings
warnings.filterwarnings('ignore', message='.*cannot set gray color.*')
warnings.filterwarnings('ignore', message='.*Pattern.*')


@dataclass
class HeadingInfo:
    """Light-weight heading information"""
    level: int
    title: str
    page_number: int
    start_line: int  # Line number where section starts
    identifier: str  # Unique ID for this heading

    def display_title(self) -> str:
        """Display title with indentation based on level"""
        indent = "  " * (self.level - 1)
        return f"{indent}{self.title}"


@dataclass
class SectionContent:
    """Full section content loaded on-demand"""
    heading: HeadingInfo
    content: str
    raw_text: str


class OptimizedPDFExtractor:
    """Fast PDF extraction - headings first, content on-demand"""

    def __init__(self):
        # Patterns for identifying headings
        self.heading_patterns = [
            # Numbered patterns
            (r'^(\d+\.?\d*\.?\d*\.?\d*)\s+([A-Z][^\n]{0,200})$', 'numbered'),

            # ALL CAPS headings (short lines)
            (r'^([A-Z][A-Z\s]{2,50})$', 'caps'),

            # Title Case (at start of line, short)
            (r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,8})$', 'title'),

            # With colons
            (r'^([A-Z][^\n]{5,60}):$', 'colon'),
        ]

        self.toc_patterns = [
            # Table of contents style entries
            r'^(\d+\.?\d*\.?\d*\.?\d*)\s+([^\.\d]+?)\s*\.{2,}\s*\d+$',  # 1.2.3 Title .... 45
            r'^([A-Z][A-Z\s]{2,50})\s*\.{2,}\s*\d+$',  # TITLE .... 45
        ]

        # Cache for footer/header detection
        self.common_lines = {}  # Track lines that appear on multiple pages

    def extract_toc_and_headings(self, pdf_path: str) -> List[HeadingInfo]:
        """
        Fast extraction of just headings and table of contents
        Returns list of all headings found
        """
        headings = []
        seen_titles = set()  # Avoid duplicates

        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)

                # First, check first 5 pages for ToC
                toc_headings = self._extract_from_toc(pdf, max_pages=5)

                # Then scan all pages for headings (fast scan - no content extraction)
                for page_num, page in enumerate(pdf.pages, start=1):
                    # Show progress for long documents
                    if page_num % 20 == 0:
                        print(f"Scanning page {page_num}/{total_pages}...")

                    try:
                        # Quick text extraction
                        text = page.extract_text()
                        if not text:
                            continue

                        lines = text.split('\n')

                        for line_num, line in enumerate(lines):
                            line = line.strip()
                            if not line or len(line) < 3:
                                continue

                            # Check if this is a heading
                            heading_info = self._identify_heading(line, page_num, line_num)

                            if heading_info and heading_info.title not in seen_titles:
                                headings.append(heading_info)
                                seen_titles.add(heading_info.title)

                    except Exception as e:
                        # Skip problematic pages
                        continue

                # Merge ToC with found headings, prioritize ToC
                if toc_headings:
                    # Use ToC as primary structure
                    final_headings = toc_headings

                    # Add any headings not in ToC
                    toc_titles = {h.title for h in toc_headings}
                    for heading in headings:
                        if heading.title not in toc_titles:
                            final_headings.append(heading)
                else:
                    final_headings = headings

                # Sort by page number, then by line number
                final_headings.sort(key=lambda h: (h.page_number, h.start_line))

                # Assign unique identifiers
                for i, heading in enumerate(final_headings):
                    heading.identifier = f"section_{i}_{heading.page_number}"

                return final_headings

        except Exception as e:
            print(f"Error extracting headings: {str(e)}")
            return []

    def _extract_from_toc(self, pdf, max_pages=5) -> List[HeadingInfo]:
        """Extract headings from table of contents if present"""
        toc_headings = []

        for page_num in range(min(max_pages, len(pdf.pages))):
            try:
                page = pdf.pages[page_num]
                text = page.extract_text()
                if not text:
                    continue

                lines = text.split('\n')

                # Look for ToC patterns
                for line_num, line in enumerate(lines):
                    line = line.strip()

                    for pattern in self.toc_patterns:
                        match = re.match(pattern, line)
                        if match:
                            if len(match.groups()) == 2:
                                number, title = match.groups()
                                level = number.count('.') + 1 if '.' in number else 1
                            else:
                                title = match.group(1)
                                level = 1

                            heading = HeadingInfo(
                                level=level,
                                title=title.strip(),
                                page_number=page_num + 1,
                                start_line=line_num,
                                identifier=""
                            )
                            toc_headings.append(heading)
                            break

            except:
                continue

        return toc_headings

    def _identify_heading(self, line: str, page_num: int, line_num: int) -> Optional[HeadingInfo]:
        """Identify if a line is a heading"""

        # Skip very long lines (likely content)
        if len(line) > 150:
            return None

        # Skip lines with too many common words (likely content)
        common_words = ['the', 'and', 'or', 'is', 'are', 'was', 'were', 'in', 'on', 'at']
        word_count = len(line.split())
        common_count = sum(1 for word in line.lower().split() if word in common_words)
        if word_count > 10 and common_count > 3:
            return None

        # Check against patterns
        for pattern, pattern_type in self.heading_patterns:
            match = re.match(pattern, line)
            if match:
                if pattern_type == 'numbered':
                    number = match.group(1)
                    title = match.group(2).strip()
                    level = number.count('.') + 1
                else:
                    title = match.group(1).strip()
                    level = self._estimate_level(line, pattern_type)

                # Additional validation
                if len(title) < 3 or len(title) > 120:
                    continue

                return HeadingInfo(
                    level=level,
                    title=title,
                    page_number=page_num,
                    start_line=line_num,
                    identifier=""
                )

        return None

    def _estimate_level(self, line: str, pattern_type: str) -> int:
        """Estimate heading level based on characteristics"""
        if pattern_type == 'caps':
            return 1 if len(line) < 30 else 2
        elif pattern_type == 'title':
            return 2 if len(line) < 40 else 3
        elif pattern_type == 'colon':
            return 2
        return 3

    def extract_section_content(self, pdf_path: str, heading: HeadingInfo,
                                next_heading: Optional[HeadingInfo] = None,
                                all_headings: List[HeadingInfo] = None) -> SectionContent:
        """
        Extract content for a specific section on-demand
        Handles multi-page sections and removes headers/footers
        """
        all_page_lines = {}  # Store lines by page for footer detection
        content_lines = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Determine page range - handle sections spanning multiple pages
                start_page = heading.page_number - 1  # 0-indexed

                # Find actual end page by looking for next heading OR end of document
                if next_heading:
                    end_page = next_heading.page_number - 1
                else:
                    # No next heading, go to end of document
                    end_page = len(pdf.pages) - 1

                # First pass: collect all lines to detect footers/headers
                for page_num in range(start_page, min(end_page + 1, len(pdf.pages))):
                    try:
                        page = pdf.pages[page_num]
                        text = page.extract_text()
                        if not text:
                            continue

                        lines = text.split('\n')
                        all_page_lines[page_num] = lines

                    except Exception as e:
                        continue

                # Detect common headers/footers (appear on multiple pages)
                headers_footers = self._detect_headers_footers(all_page_lines)

                # Second pass: extract actual content, skip headers/footers
                collecting = False
                for page_num in range(start_page, min(end_page + 1, len(pdf.pages))):
                    if page_num not in all_page_lines:
                        continue

                    lines = all_page_lines[page_num]

                    for line_num, line in enumerate(lines):
                        line_clean = line.strip()

                        # Skip empty lines
                        if not line_clean:
                            continue

                        # On start page, skip until we reach the heading
                        if page_num == start_page:
                            if line_num < heading.start_line:
                                continue
                            elif line_num == heading.start_line:
                                collecting = True
                                continue  # Skip the heading itself

                        # On end page with next heading, stop at next heading
                        if next_heading and page_num == end_page:
                            # Check if this line is the next heading
                            if line_num >= next_heading.start_line:
                                # Check if line matches next heading title
                                if self._is_heading_line(line_clean, next_heading, all_headings):
                                    break

                        # Skip if this is a header/footer
                        if line_clean in headers_footers:
                            continue

                        # Skip page numbers (common footer pattern)
                        if self._is_page_number(line_clean):
                            continue

                        # Skip if this is actually a heading (not content)
                        if collecting and self._looks_like_heading(line_clean, all_headings):
                            # This might be a sub-heading within the section
                            # Only skip if it's a major heading
                            if all_headings:
                                is_major_heading = any(
                                    h.title == line_clean and h.page_number == page_num + 1
                                    for h in all_headings
                                    if h != heading and (not next_heading or h != next_heading)
                                )
                                if is_major_heading:
                                    continue

                        if collecting:
                            content_lines.append(line_clean)

        except Exception as e:
            print(f"Error extracting section content: {str(e)}")

        # Clean up content
        content_text = '\n'.join(content_lines)

        # Remove multiple consecutive newlines
        import re
        content_text = re.sub(r'\n{3,}', '\n\n', content_text)

        return SectionContent(
            heading=heading,
            content=content_text,
            raw_text=content_text
        )

    def _detect_headers_footers(self, all_page_lines: Dict[int, List[str]]) -> set:
        """Detect lines that appear on multiple pages (likely headers/footers)"""
        line_frequency = {}

        for page_num, lines in all_page_lines.items():
            # Check first 3 lines (potential headers)
            for line in lines[:3]:
                line_clean = line.strip()
                if line_clean and len(line_clean) > 3:
                    line_frequency[line_clean] = line_frequency.get(line_clean, 0) + 1

            # Check last 3 lines (potential footers)
            for line in lines[-3:]:
                line_clean = line.strip()
                if line_clean and len(line_clean) > 3:
                    line_frequency[line_clean] = line_frequency.get(line_clean, 0) + 1

        # Lines appearing on 50%+ of pages are likely headers/footers
        num_pages = len(all_page_lines)
        threshold = max(2, num_pages * 0.5)  # At least 2 pages or 50%

        headers_footers = {
            line for line, count in line_frequency.items()
            if count >= threshold
        }

        return headers_footers

    def _is_page_number(self, line: str) -> bool:
        """Check if line is just a page number"""
        # Common page number patterns
        if re.match(r'^\d+$', line):  # Just a number
            return True
        if re.match(r'^Page\s+\d+$', line, re.IGNORECASE):
            return True
        if re.match(r'^\d+\s*/\s*\d+$', line):  # 5 / 250
            return True
        return False

    def _is_heading_line(self, line: str, heading: HeadingInfo, all_headings: List[HeadingInfo]) -> bool:
        """Check if line matches a known heading"""
        if not heading:
            return False

        # Exact match
        if line == heading.title:
            return True

        # Partial match (heading might have line breaks)
        if heading.title in line or line in heading.title:
            return True

        return False

    def _looks_like_heading(self, line: str, all_headings: List[HeadingInfo]) -> bool:
        """Check if line looks like a heading"""
        if not all_headings:
            return False

        # Check against known headings
        for heading in all_headings:
            if line == heading.title or heading.title.startswith(line) or line.startswith(heading.title[:20]):
                return True

        return False


class PDFComparator:
    """Compare two PDFs using heading-based navigation"""

    def __init__(self, original_path: str, modified_path: str):
        self.original_path = original_path
        self.modified_path = modified_path
        self.extractor = OptimizedPDFExtractor()

        self.original_headings: List[HeadingInfo] = []
        self.modified_headings: List[HeadingInfo] = []
        self.heading_matches: Dict[str, Tuple[Optional[HeadingInfo], Optional[HeadingInfo]]] = {}

    def extract_headings(self) -> Tuple[List[HeadingInfo], List[HeadingInfo]]:
        """Fast extraction of headings from both PDFs"""
        print("Extracting headings from original PDF...")
        self.original_headings = self.extractor.extract_toc_and_headings(self.original_path)

        print("Extracting headings from modified PDF...")
        self.modified_headings = self.extractor.extract_toc_and_headings(self.modified_path)

        print(f"Found {len(self.original_headings)} headings in original")
        print(f"Found {len(self.modified_headings)} headings in modified")

        return self.original_headings, self.modified_headings

    def match_headings(self) -> Dict[str, Dict]:
        """
        Match headings between documents
        Returns dict with structure for dropdown
        """
        matches = {}
        used_modified = set()

        # Match original headings to modified
        for orig in self.original_headings:
            best_match = None
            best_score = 0

            for mod_idx, mod in enumerate(self.modified_headings):
                if mod_idx in used_modified:
                    continue

                score = self._similarity_score(orig.title, mod.title)
                if score > best_score and score > 60:
                    best_score = score
                    best_match = mod

            if best_match:
                used_modified.add(self.modified_headings.index(best_match))
                match_id = f"match_{len(matches)}"
                matches[match_id] = {
                    'original': orig,
                    'modified': best_match,
                    'match_score': best_score,
                    'status': 'matched'
                }
            else:
                match_id = f"match_{len(matches)}"
                matches[match_id] = {
                    'original': orig,
                    'modified': None,
                    'match_score': 0,
                    'status': 'removed'
                }

        # Add unmatched modified headings
        for mod_idx, mod in enumerate(self.modified_headings):
            if mod_idx not in used_modified:
                match_id = f"match_{len(matches)}"
                matches[match_id] = {
                    'original': None,
                    'modified': mod,
                    'match_score': 0,
                    'status': 'added'
                }

        self.heading_matches = matches
        return matches

    def _similarity_score(self, text1: str, text2: str) -> float:
        """Calculate similarity between two heading titles"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio() * 100

    def get_section_comparison(self, match_id: str) -> Tuple[Optional[SectionContent], Optional[SectionContent]]:
        """
        Load content for a specific section on-demand
        Only called when user selects from dropdown
        """
        if match_id not in self.heading_matches:
            return None, None

        match = self.heading_matches[match_id]
        orig_heading = match['original']
        mod_heading = match['modified']

        # Find next headings to determine section boundaries
        orig_next = self._get_next_heading(orig_heading, self.original_headings) if orig_heading else None
        mod_next = self._get_next_heading(mod_heading, self.modified_headings) if mod_heading else None

        # Extract content on-demand
        orig_content = None
        mod_content = None

        if orig_heading:
            print(f"Loading original: {orig_heading.title}")
            orig_content = self.extractor.extract_section_content(
                self.original_path, orig_heading, orig_next, self.original_headings
            )

        if mod_heading:
            print(f"Loading modified: {mod_heading.title}")
            mod_content = self.extractor.extract_section_content(
                self.modified_path, mod_heading, mod_next, self.modified_headings
            )

        return orig_content, mod_content

    def _get_next_heading(self, current: HeadingInfo, headings: List[HeadingInfo]) -> Optional[HeadingInfo]:
        """Get the next heading after current"""
        try:
            idx = headings.index(current)
            if idx + 1 < len(headings):
                return headings[idx + 1]
        except ValueError:
            pass
        return None

    def get_dropdown_options(self) -> List[Tuple[str, str, str]]:
        """
        Get options for dropdown
        Returns list of (match_id, display_text, status)
        """
        options = []

        for match_id, match in self.heading_matches.items():
            orig = match['original']
            mod = match['modified']
            status = match['status']

            if status == 'matched':
                display = f"📄 {orig.title}"
            elif status == 'removed':
                display = f"🔴 REMOVED: {orig.title}"
            elif status == 'added':
                display = f"🟢 ADDED: {mod.title}"
            else:
                display = f"📄 {orig.title if orig else mod.title}"

            options.append((match_id, display, status))

        return options
