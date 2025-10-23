"""
Smart Diff Algorithm for PDF Content Comparison
Handles partial matches, insertions at any position, and word-level diffs
"""

import difflib
from typing import List, Tuple
import re


class SmartDiff:
    """Intelligent diff that handles various cases"""

    @staticmethod
    def compare_texts(text1: str, text2: str) -> List[Tuple[str, str, str]]:
        """
        Compare two texts and return structured diff
        Returns list of (change_type, original_line, modified_line)
        change_type: 'unchanged', 'added', 'removed', 'modified'
        """
        if not text1 and not text2:
            return []

        if not text1:
            # Everything is added
            return [('added', '', line) for line in text2.split('\n') if line.strip()]

        if not text2:
            # Everything is removed
            return [('removed', line, '') for line in text1.split('\n') if line.strip()]

        # Split into sentences/paragraphs for better matching
        lines1 = [line.strip() for line in text1.split('\n') if line.strip()]
        lines2 = [line.strip() for line in text2.split('\n') if line.strip()]

        # Use SequenceMatcher for intelligent matching
        matcher = difflib.SequenceMatcher(None, lines1, lines2)

        result = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # Lines are the same
                for i in range(i1, i2):
                    result.append(('unchanged', lines1[i], lines1[i]))

            elif tag == 'replace':
                # Lines were modified
                # Check if it's a word-level change or complete replacement
                orig_lines = lines1[i1:i2]
                mod_lines = lines2[j1:j2]

                # If counts match, try word-level diff
                if len(orig_lines) == len(mod_lines):
                    for orig, mod in zip(orig_lines, mod_lines):
                        result.append(('modified', orig, mod))
                else:
                    # Different counts - show as remove + add
                    for line in orig_lines:
                        result.append(('removed', line, ''))
                    for line in mod_lines:
                        result.append(('added', '', line))

            elif tag == 'delete':
                # Lines were removed
                for i in range(i1, i2):
                    result.append(('removed', lines1[i], ''))

            elif tag == 'insert':
                # Lines were added
                for j in range(j1, j2):
                    result.append(('added', '', lines2[j]))

        return result

    @staticmethod
    def get_word_level_diff(text1: str, text2: str) -> Tuple[str, str]:
        """
        Get word-level diff highlighting
        Returns HTML with highlighted changes
        """
        words1 = text1.split()
        words2 = text2.split()

        matcher = difflib.SequenceMatcher(None, words1, words2)

        html1_parts = []
        html2_parts = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # Same words
                html1_parts.append(' '.join(words1[i1:i2]))
                html2_parts.append(' '.join(words2[j1:j2]))

            elif tag == 'replace':
                # Words changed
                html1_parts.append(f'<span class="word-removed">{" ".join(words1[i1:i2])}</span>')
                html2_parts.append(f'<span class="word-added">{" ".join(words2[j1:j2])}</span>')

            elif tag == 'delete':
                # Words removed
                html1_parts.append(f'<span class="word-removed">{" ".join(words1[i1:i2])}</span>')

            elif tag == 'insert':
                # Words added
                html2_parts.append(f'<span class="word-added">{" ".join(words2[j1:j2])}</span>')

        return ' '.join(html1_parts), ' '.join(html2_parts)

    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """Calculate similarity percentage"""
        if not text1 and not text2:
            return 100.0

        if not text1 or not text2:
            return 0.0

        return difflib.SequenceMatcher(None, text1, text2).ratio() * 100

    @staticmethod
    def find_moved_content(text1: str, text2: str) -> List[Tuple[str, int, int]]:
        """
        Find content that was moved (not added/removed)
        Returns list of (content, position_in_text1, position_in_text2)
        """
        lines1 = [line.strip() for line in text1.split('\n') if line.strip()]
        lines2 = [line.strip() for line in text2.split('\n') if line.strip()]

        moved = []

        # Find lines in text1 that appear in text2 but in different position
        for i, line1 in enumerate(lines1):
            if len(line1) < 20:  # Skip short lines
                continue

            for j, line2 in enumerate(lines2):
                if line1 == line2 and abs(i - j) > 2:  # Same content, different position
                    # Check if it's not already marked as unchanged nearby
                    similarity = difflib.SequenceMatcher(None, line1, line2).ratio()
                    if similarity > 0.9:
                        moved.append((line1, i, j))
                        break

        return moved


class ContentAnalyzer:
    """Analyze content differences"""

    @staticmethod
    def get_statistics(diff_result: List[Tuple[str, str, str]]) -> dict:
        """Get statistics from diff result"""
        stats = {
            'unchanged': 0,
            'added': 0,
            'removed': 0,
            'modified': 0,
            'total_lines': len(diff_result)
        }

        for change_type, _, _ in diff_result:
            stats[change_type] += 1

        return stats

    @staticmethod
    def extract_key_changes(diff_result: List[Tuple[str, str, str]],
                           keywords: List[str] = None) -> List[Tuple[str, str, str]]:
        """Extract only changes containing keywords"""
        if not keywords:
            return [d for d in diff_result if d[0] != 'unchanged']

        key_changes = []

        for change_type, orig, mod in diff_result:
            if change_type == 'unchanged':
                continue

            text = (orig + ' ' + mod).lower()

            if any(keyword.lower() in text for keyword in keywords):
                key_changes.append((change_type, orig, mod))

        return key_changes

    @staticmethod
    def group_consecutive_changes(diff_result: List[Tuple[str, str, str]]) -> List[List[Tuple[str, str, str]]]:
        """Group consecutive changes together"""
        if not diff_result:
            return []

        groups = []
        current_group = []

        for item in diff_result:
            change_type = item[0]

            if change_type == 'unchanged':
                if current_group:
                    groups.append(current_group)
                    current_group = []
            else:
                current_group.append(item)

        if current_group:
            groups.append(current_group)

        return groups


def format_diff_for_display(diff_result: List[Tuple[str, str, str]],
                            max_lines: int = 100,
                            show_unchanged: bool = False,
                            show_word_diff: bool = True) -> str:
    """
    Format diff result for HTML display
    """
    html_parts = []

    line_count = 0

    for change_type, orig, mod in diff_result:
        if line_count >= max_lines:
            remaining = len(diff_result) - line_count
            html_parts.append(f'<div class="diff-line" style="color: #858585; font-style: italic;">... and {remaining} more lines</div>')
            break

        if change_type == 'unchanged' and not show_unchanged:
            continue

        if change_type == 'unchanged':
            html_parts.append(f'<div class="diff-line diff-unchanged">{_escape_html(orig)}</div>')

        elif change_type == 'added':
            html_parts.append(f'<div class="diff-line diff-added"><strong>+</strong> {_escape_html(mod)}</div>')

        elif change_type == 'removed':
            html_parts.append(f'<div class="diff-line diff-removed"><strong>-</strong> {_escape_html(orig)}</div>')

        elif change_type == 'modified':
            if show_word_diff and len(orig) < 500 and len(mod) < 500:
                # Show word-level diff
                diff = SmartDiff()
                orig_html, mod_html = diff.get_word_level_diff(orig, mod)
                html_parts.append(f'<div class="diff-line diff-modified"><strong>-</strong> {orig_html}</div>')
                html_parts.append(f'<div class="diff-line diff-modified"><strong>+</strong> {mod_html}</div>')
            else:
                # Show line-level diff
                html_parts.append(f'<div class="diff-line diff-removed"><strong>-</strong> {_escape_html(orig)}</div>')
                html_parts.append(f'<div class="diff-line diff-added"><strong>+</strong> {_escape_html(mod)}</div>')

        line_count += 1

    return '\n'.join(html_parts)


def _escape_html(text: str) -> str:
    """Escape HTML characters"""
    import html
    return html.escape(text)
