"""
Optimized PDF Comparison UI - Fast and User-Friendly
Uses dropdown navigation with on-demand content loading
"""

import streamlit as st
import streamlit.components.v1 as components
from pdf_compare_optimized import OptimizedPDFExtractor, PDFComparator, HeadingInfo, SectionContent
import html
from datetime import datetime
import difflib
from typing import Optional, Tuple

def create_optimized_pdf_ui():
    """Main UI for optimized PDF comparison"""

    st.markdown("""
    <style>
        /* Dropdown and navigation styles */
        .section-selector {
            background: #2d2d30;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }

        /* Side-by-side comparison */
        .comparison-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 20px;
        }

        .comparison-panel {
            background: #1e1e1e;
            border: 1px solid #464647;
            border-radius: 6px;
            padding: 15px;
            min-height: 400px;
            max-height: 600px;
            overflow-y: auto;
        }

        .panel-header {
            background: #007ACC;
            color: white;
            padding: 10px;
            margin: -15px -15px 15px -15px;
            border-radius: 6px 6px 0 0;
            font-weight: bold;
        }

        .panel-header.removed {
            background: #e5534b;
        }

        .panel-header.added {
            background: #57ab5a;
        }

        .content-text {
            color: #d4d4d4;
            line-height: 1.8;
            font-family: 'Segoe UI', sans-serif;
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        /* Diff highlighting */
        .diff-line {
            margin: 2px 0;
            padding: 4px 8px;
            border-radius: 3px;
        }

        .diff-added {
            background: rgba(87, 171, 90, 0.2);
            border-left: 3px solid #57ab5a;
        }

        .diff-removed {
            background: rgba(229, 83, 75, 0.2);
            border-left: 3px solid #e5534b;
        }

        .diff-modified {
            background: rgba(210, 153, 34, 0.15);
            border-left: 3px solid #d29922;
        }

        .diff-unchanged {
            opacity: 0.7;
        }

        /* Status badges */
        .status-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            margin-left: 10px;
        }

        .badge-matched {
            background: #007ACC;
            color: white;
        }

        .badge-modified {
            background: #d29922;
            color: white;
        }

        .badge-added {
            background: #57ab5a;
            color: white;
        }

        .badge-removed {
            background: #e5534b;
            color: white;
        }

        /* Loading indicator */
        .loading-section {
            text-align: center;
            padding: 40px;
            color: #007ACC;
            font-size: 16px;
        }

        /* Empty state */
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #858585;
            font-style: italic;
        }

        /* Stats */
        .stats-row {
            display: flex;
            gap: 15px;
            margin: 15px 0;
            flex-wrap: wrap;
        }

        .stat-box {
            background: #2d2d30;
            padding: 15px 20px;
            border-radius: 6px;
            border-left: 4px solid #007ACC;
        }

        .stat-number {
            font-size: 28px;
            font-weight: bold;
            color: #007ACC;
        }

        .stat-label {
            font-size: 13px;
            color: #cccccc;
            margin-top: 5px;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("📄 PDF Structure Comparison (Optimized)")
    st.markdown("**Fast navigation** - Load sections on-demand as you select them")

    # Sidebar
    with st.sidebar:
        st.header("📁 Upload Documents")

        original_pdf = st.file_uploader(
            "Original Template",
            type=['pdf'],
            key="pdf_opt_original"
        )

        modified_pdf = st.file_uploader(
            "Modified Version",
            type=['pdf'],
            key="pdf_opt_modified"
        )

        st.divider()

        if st.button("🔍 Extract Structure", type="primary",
                    disabled=not (original_pdf and modified_pdf)):
            if original_pdf and modified_pdf:
                with st.spinner("Extracting headings (fast scan)..."):
                    extract_structure(original_pdf, modified_pdf)

    # Main content
    if 'pdf_opt_comparator' in st.session_state:
        display_comparison_interface()
    else:
        show_welcome()


def extract_structure(original_pdf, modified_pdf):
    """Extract document structure (headings only - fast!)"""
    try:
        import tempfile
        import os

        # Save uploaded files temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_orig:
            tmp_orig.write(original_pdf.read())
            orig_path = tmp_orig.name

        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_mod:
            tmp_mod.write(modified_pdf.read())
            mod_path = tmp_mod.name

        # Create comparator
        comparator = PDFComparator(orig_path, mod_path)

        # Extract headings only (fast!)
        orig_headings, mod_headings = comparator.extract_headings()

        if not orig_headings and not mod_headings:
            st.error("❌ No headings found in documents. Please ensure PDFs have clear section headings.")
            os.unlink(orig_path)
            os.unlink(mod_path)
            return

        # Match headings
        matches = comparator.match_headings()

        # Store in session state
        st.session_state['pdf_opt_comparator'] = comparator
        st.session_state['pdf_opt_matches'] = matches
        st.session_state['pdf_opt_orig_path'] = orig_path
        st.session_state['pdf_opt_mod_path'] = mod_path

        st.success(f"✅ Structure extracted! Found {len(orig_headings)} sections in original, {len(mod_headings)} in modified.")
        st.rerun()

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())


def display_comparison_interface():
    """Display the main comparison interface with dropdown"""

    comparator = st.session_state['pdf_opt_comparator']
    matches = st.session_state['pdf_opt_matches']

    # Statistics
    st.markdown("### 📊 Document Structure Overview")

    matched = sum(1 for m in matches.values() if m['status'] == 'matched')
    removed = sum(1 for m in matches.values() if m['status'] == 'removed')
    added = sum(1 for m in matches.values() if m['status'] == 'added')

    stats_html = f"""
    <div class="stats-row">
        <div class="stat-box">
            <div class="stat-number">{len(matches)}</div>
            <div class="stat-label">Total Sections</div>
        </div>
        <div class="stat-box" style="border-left-color: #007ACC;">
            <div class="stat-number" style="color: #007ACC;">{matched}</div>
            <div class="stat-label">Matched</div>
        </div>
        <div class="stat-box" style="border-left-color: #e5534b;">
            <div class="stat-number" style="color: #e5534b;">{removed}</div>
            <div class="stat-label">Removed</div>
        </div>
        <div class="stat-box" style="border-left-color: #57ab5a;">
            <div class="stat-number" style="color: #57ab5a;">{added}</div>
            <div class="stat-label">Added</div>
        </div>
    </div>
    """
    st.markdown(stats_html, unsafe_allow_html=True)

    st.markdown("---")

    # Section selector
    st.markdown("### 📑 Select Section to Compare")

    options = comparator.get_dropdown_options()

    if not options:
        st.warning("No sections found to compare")
        return

    # Create dropdown options
    option_labels = [opt[1] for opt in options]
    option_ids = [opt[0] for opt in options]
    option_status = [opt[2] for opt in options]

    selected_idx = st.selectbox(
        "Choose a section:",
        range(len(option_labels)),
        format_func=lambda i: option_labels[i],
        key="section_selector"
    )

    if selected_idx is not None:
        match_id = option_ids[selected_idx]
        status = option_status[selected_idx]

        # Load section content on-demand
        display_section_comparison(comparator, match_id, status)


def display_section_comparison(comparator: PDFComparator, match_id: str, status: str):
    """Display side-by-side comparison for selected section"""

    with st.spinner("Loading section content..."):
        orig_content, mod_content = comparator.get_section_comparison(match_id)

    st.markdown("---")

    # Side-by-side comparison
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📁 Original")
        if orig_content:
            display_content_panel(orig_content, is_original=True, status=status)
        else:
            st.markdown("""
            <div class="empty-state">
                <p>Section not present in original document</p>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("#### 📝 Modified")
        if mod_content:
            display_content_panel(mod_content, is_original=False, status=status)
        else:
            st.markdown("""
            <div class="empty-state">
                <p>Section removed in modified document</p>
            </div>
            """, unsafe_allow_html=True)

    # Diff analysis
    if orig_content and mod_content:
        st.markdown("---")
        st.markdown("### 🔍 Text Diff Analysis")

        with st.expander("View detailed line-by-line differences", expanded=False):
            display_diff_analysis(orig_content.content, mod_content.content)


def display_content_panel(content: SectionContent, is_original: bool, status: str):
    """Display content in a panel"""

    # Heading info
    st.markdown(f"**Section:** {content.heading.title}")
    st.markdown(f"**Page:** {content.heading.page_number}")
    st.markdown(f"**Level:** {content.heading.level}")

    st.markdown("---")

    # Content
    if content.content:
        # Display in scrollable text area
        st.text_area(
            "Content",
            content.content,
            height=400,
            disabled=True,
            key=f"content_{'orig' if is_original else 'mod'}_{content.heading.identifier}"
        )

        # Character count
        st.caption(f"Characters: {len(content.content)} | Lines: {len(content.content.splitlines())}")
    else:
        st.info("No content in this section")


def display_diff_analysis(orig_text: str, mod_text: str):
    """Display line-by-line diff"""

    orig_lines = orig_text.splitlines()
    mod_lines = mod_text.splitlines()

    # Use difflib to compute differences
    differ = difflib.Differ()
    diff = list(differ.compare(orig_lines, mod_lines))

    # Render diff
    diff_html = '<div class="content-text">'

    for line in diff[:100]:  # Limit to first 100 lines for performance
        if line.startswith('+ '):
            diff_html += f'<div class="diff-line diff-added">+ {html.escape(line[2:])}</div>'
        elif line.startswith('- '):
            diff_html += f'<div class="diff-line diff-removed">- {html.escape(line[2:])}</div>'
        elif line.startswith('? '):
            continue  # Skip hint lines
        else:
            diff_html += f'<div class="diff-line diff-unchanged">{html.escape(line[2:])}</div>'

    if len(diff) > 100:
        diff_html += f'<div class="diff-line" style="color: #858585; font-style: italic;">... and {len(diff) - 100} more lines</div>'

    diff_html += '</div>'

    st.markdown(diff_html, unsafe_allow_html=True)


def show_welcome():
    """Show welcome screen"""
    st.markdown("""
    ### Welcome to Optimized PDF Comparison!

    #### 🚀 How It Works:

    **Phase 1: Fast Structure Extraction** (10-30 seconds)
    - Scans PDFs for headings and subheadings
    - Extracts Table of Contents if available
    - Matches sections between documents
    - **No full content loading yet!**

    **Phase 2: On-Demand Section Loading** (1-2 seconds per section)
    - Select any section from dropdown
    - Loads ONLY that section's content
    - Displays side-by-side comparison
    - Like VS Code diff view

    #### ✨ Benefits:

    - ⚡ **Much faster** - No waiting for full document comparison
    - 🎯 **Focused analysis** - Review sections one at a time
    - 📊 **Clear navigation** - Dropdown shows all sections
    - 🔍 **Better UX** - See exactly what changed in each section

    #### 📋 To Get Started:

    1. Upload **Original Template** PDF in sidebar
    2. Upload **Modified Version** PDF
    3. Click **"Extract Structure"**
    4. Select sections from dropdown to compare

    #### 💡 Tips:

    - PDFs should have clear section headings
    - Numbered sections work best (1.2.3 format)
    - Table of Contents helps (first 5 pages scanned)
    - Blue highlights/annotations are OK (handled gracefully)

    **Ready to compare? Upload your PDFs in the sidebar!** →
    """)


if __name__ == "__main__":
    st.set_page_config(
        page_title="PDF Comparison (Optimized)",
        page_icon="📄",
        layout="wide"
    )

    create_optimized_pdf_ui()
