"""
Advanced PDF Comparison UI - Streamlit Interface

Modern, user-friendly web interface for PDF document comparison with
semantic understanding, requirement tracking, and optional AI explanations.

Author: Advanced PDF Comparison System
Date: 2025-10-30
"""

import streamlit as st
import json
import tempfile
from pathlib import Path
from datetime import datetime

try:
    from advanced_pdf_comparator import AdvancedPDFComparator, ComparisonConfig
    COMPARATOR_AVAILABLE = True
except ImportError:
    COMPARATOR_AVAILABLE = False
    st.error("⚠️ Advanced PDF Comparator not available. Please check installation.")


# Page configuration
st.set_page_config(
    page_title="Advanced PDF Comparator",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_session_state():
    """Initialize session state variables"""
    if 'comparison_done' not in st.session_state:
        st.session_state.comparison_done = False
    if 'report' not in st.session_state:
        st.session_state.report = None
    if 'config' not in st.session_state:
        st.session_state.config = None


def render_header():
    """Render page header"""
    st.title("📄 Advanced PDF Document Comparator")
    st.markdown("""
    Compare PDF documents with **semantic understanding**, **requirement tracking**,
    and optional **AI explanations**. Perfect for technical specifications,
    contracts, and legal documents.
    """)

    st.markdown("---")


def render_sidebar():
    """Render sidebar with configuration options"""
    st.sidebar.header("⚙️ Configuration")

    st.sidebar.subheader("Features")
    enable_translation = st.sidebar.checkbox(
        "🌍 Auto-translate documents",
        value=True,
        help="Automatically translate non-English documents to English"
    )

    enable_requirements = st.sidebar.checkbox(
        "📋 Analyze requirements",
        value=True,
        help="Detect and track MUST/SHALL/SHOULD requirements"
    )

    enable_llm = st.sidebar.checkbox(
        "🤖 Generate AI explanations",
        value=False,
        help="Use local LLM to explain changes (requires model)"
    )

    st.sidebar.subheader("Parameters")
    similarity_threshold = st.sidebar.slider(
        "Similarity Threshold",
        min_value=0.5,
        max_value=0.95,
        value=0.75,
        step=0.05,
        help="Minimum similarity to consider paragraphs as matching"
    )

    use_gpu = st.sidebar.checkbox(
        "⚡ Use GPU acceleration",
        value=True,
        help="Enable GPU for faster processing"
    )

    llm_model_path = None
    max_llm_explanations = 10

    if enable_llm:
        st.sidebar.subheader("LLM Settings")
        llm_model_path = st.sidebar.text_input(
            "LLM Model Path",
            placeholder="path/to/model.gguf",
            help="Path to GGUF format LLM model"
        )
        max_llm_explanations = st.sidebar.number_input(
            "Max Explanations",
            min_value=1,
            max_value=50,
            value=10,
            help="Maximum number of AI explanations to generate"
        )

    # Create config
    config = ComparisonConfig(
        enable_translation=enable_translation,
        enable_requirements=enable_requirements,
        enable_llm=enable_llm,
        similarity_threshold=similarity_threshold,
        use_gpu=use_gpu,
        llm_model_path=llm_model_path if llm_model_path else None,
        max_llm_explanations=max_llm_explanations
    )

    st.sidebar.markdown("---")
    st.sidebar.info("""
    **💡 Tips:**
    - Translation adds 5-10s per document
    - LLM explanations add 1-2s each
    - GPU acceleration speeds up 2-3x
    - Large documents may take 1-2 minutes
    """)

    return config


def render_file_upload():
    """Render file upload section"""
    st.header("1️⃣ Upload Documents")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📄 Original Document")
        old_file = st.file_uploader(
            "Upload original/old PDF",
            type=['pdf'],
            key='old_file',
            help="The original or previous version of the document"
        )

        if old_file:
            st.success(f"✅ {old_file.name}")

    with col2:
        st.subheader("📄 Modified Document")
        new_file = st.file_uploader(
            "Upload modified/new PDF",
            type=['pdf'],
            key='new_file',
            help="The modified or new version of the document"
        )

        if new_file:
            st.success(f"✅ {new_file.name}")

    return old_file, new_file


def render_text_input():
    """Render text input section as alternative"""
    with st.expander("💬 Or compare text directly (no PDF upload)"):
        col1, col2 = st.columns(2)

        with col1:
            old_text = st.text_area(
                "Original Text",
                height=200,
                placeholder="Enter original text here..."
            )

        with col2:
            new_text = st.text_area(
                "Modified Text",
                height=200,
                placeholder="Enter modified text here..."
            )

        return old_text, new_text

    return None, None


def run_comparison(old_file, new_file, old_text, new_text, config):
    """Run document comparison"""
    try:
        # Initialize comparator
        with st.spinner("🔧 Initializing comparison engine..."):
            comparator = AdvancedPDFComparator(config)

        # Determine comparison mode
        if old_file and new_file:
            # PDF comparison mode
            with st.spinner("📄 Comparing PDF documents..."):
                # Save uploaded files to temp directory
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_old:
                    tmp_old.write(old_file.read())
                    old_path = tmp_old.name

                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_new:
                    tmp_new.write(new_file.read())
                    new_path = tmp_new.name

                # Run comparison
                report = comparator.compare_documents(old_path, new_path)

                # Clean up temp files
                Path(old_path).unlink()
                Path(new_path).unlink()

        elif old_text and new_text:
            # Text comparison mode
            with st.spinner("💬 Comparing text..."):
                report = comparator.compare_texts(old_text, new_text)

        else:
            st.error("❌ Please provide documents or text to compare")
            return None

        return report

    except Exception as e:
        st.error(f"❌ Comparison failed: {str(e)}")
        st.exception(e)
        return None


def render_summary(report):
    """Render comparison summary"""
    st.header("📊 Comparison Summary")

    summary = report.comparison_result['summary']

    # Metrics row
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Unchanged", summary['unchanged'], help="Paragraphs with no changes")

    with col2:
        st.metric("Modified", summary['modified'], help="Paragraphs with modifications")

    with col3:
        st.metric("Added", summary['added'], help="New paragraphs in modified document")

    with col4:
        st.metric("Deleted", summary['deleted'], help="Paragraphs removed from original")

    with col5:
        similarity_pct = summary['average_similarity'] * 100
        st.metric("Similarity", f"{similarity_pct:.1f}%", help="Average semantic similarity")

    # Additional info
    col1, col2, col3 = st.columns(3)

    with col1:
        st.info(f"**Processing Time:** {report.processing_time:.2f}s")

    with col2:
        st.info(f"**Old Doc:** {report.old_doc_info.paragraph_count} paragraphs")

    with col3:
        st.info(f"**New Doc:** {report.new_doc_info.paragraph_count} paragraphs")


def render_detailed_changes(report):
    """Render detailed changes"""
    st.header("📝 Detailed Changes")

    matches = report.comparison_result['matches']

    # Filter options
    col1, col2 = st.columns([3, 1])

    with col1:
        filter_type = st.multiselect(
            "Filter by change type:",
            ['unchanged', 'modified', 'added', 'deleted', 'moved'],
            default=['modified', 'added', 'deleted']
        )

    with col2:
        show_all = st.checkbox("Show all", value=False)

    # Filter matches
    if show_all:
        filtered_matches = matches
    else:
        filtered_matches = [m for m in matches if m['change_type'] in filter_type]

    # Display matches
    if not filtered_matches:
        st.info("No changes to display with current filters.")
        return

    st.write(f"Showing {len(filtered_matches)} of {len(matches)} total changes")

    for i, match in enumerate(filtered_matches[:50]):  # Limit to 50 for performance
        change_type = match['change_type']

        # Determine color based on change type
        if change_type == 'unchanged':
            color = 'gray'
        elif change_type == 'modified':
            color = 'blue'
        elif change_type == 'added':
            color = 'green'
        elif change_type == 'deleted':
            color = 'red'
        else:
            color = 'orange'

        with st.expander(f"**{i+1}. [{change_type.upper()}]** - {match.get('explanation', 'No explanation')[:80]}..."):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Original:**")
                if match['old_text']:
                    st.text_area("", match['old_text'], height=100, key=f"old_{i}", disabled=True)
                else:
                    st.info("(No original text)")

            with col2:
                st.markdown("**Modified:**")
                if match['new_text']:
                    st.text_area("", match['new_text'], height=100, key=f"new_{i}", disabled=True)
                else:
                    st.info("(No modified text)")

            # Additional info
            st.caption(f"Similarity: {match['similarity']:.2%} | Severity: {match['severity']}")


def render_requirement_changes(report):
    """Render requirement changes"""
    if not report.requirement_changes:
        return

    st.header("📋 Requirement Changes")

    req_changes = report.requirement_changes

    # Count by type
    added = sum(1 for r in req_changes if r['change_type'] == 'added')
    removed = sum(1 for r in req_changes if r['change_type'] == 'removed')
    modified = sum(1 for r in req_changes if r['change_type'] == 'modified')
    level_changed = sum(1 for r in req_changes if r['change_type'] == 'level_changed')
    critical = sum(1 for r in req_changes if r.get('severity') == 'critical')

    # Metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Added", added)

    with col2:
        st.metric("Removed", removed)

    with col3:
        st.metric("Modified", modified)

    with col4:
        st.metric("⚠️ Critical", critical)

    # Display changes
    st.subheader("Requirement Details")

    for i, change in enumerate(req_changes[:20]):  # Limit to 20
        severity = change.get('severity', 'minor')
        change_type = change['change_type']

        # Icon based on severity
        if severity == 'critical':
            icon = "🔴"
        elif severity == 'major':
            icon = "🟡"
        else:
            icon = "🟢"

        with st.expander(f"{icon} **{i+1}. {change_type.upper()}** - {change.get('explanation', '')[:80]}"):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Old Requirement:**")
                if change['old_requirement']:
                    req = change['old_requirement']
                    st.info(f"**Level:** {req['level']}")
                    st.text_area("", req['text'], height=80, key=f"old_req_{i}", disabled=True)
                else:
                    st.info("(New requirement)")

            with col2:
                st.markdown("**New Requirement:**")
                if change['new_requirement']:
                    req = change['new_requirement']
                    st.info(f"**Level:** {req['level']}")
                    st.text_area("", req['text'], height=80, key=f"new_req_{i}", disabled=True)
                else:
                    st.info("(Removed)")


def render_export(report):
    """Render export options"""
    st.header("💾 Export Results")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Export JSON
        report_json = json.dumps(report.to_dict(), indent=2, ensure_ascii=False)
        st.download_button(
            label="📄 Download JSON Report",
            data=report_json,
            file_name=f"comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

    with col2:
        # Export summary text
        summary = report.comparison_result['summary']
        summary_text = f"""
PDF COMPARISON REPORT
Generated: {report.timestamp}

SUMMARY:
- Old Document: {report.old_doc_info.paragraph_count} paragraphs
- New Document: {report.new_doc_info.paragraph_count} paragraphs
- Unchanged: {summary['unchanged']}
- Modified: {summary['modified']}
- Added: {summary['added']}
- Deleted: {summary['deleted']}
- Average Similarity: {summary['average_similarity']:.2%}

Processing Time: {report.processing_time:.2f}s
        """

        st.download_button(
            label="📝 Download Summary",
            data=summary_text,
            file_name=f"comparison_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

    with col3:
        st.info("More export formats coming soon!")


def main():
    """Main application"""
    init_session_state()
    render_header()

    # Sidebar configuration
    config = render_sidebar()

    # File upload
    old_file, new_file = render_file_upload()

    # Text input alternative
    old_text, new_text = render_text_input()

    st.markdown("---")

    # Comparison button
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        compare_button = st.button(
            "🚀 Start Comparison",
            type="primary",
            use_container_width=True
        )

    # Run comparison
    if compare_button:
        if not COMPARATOR_AVAILABLE:
            st.error("❌ Comparator not available. Please check installation.")
            return

        report = run_comparison(old_file, new_file, old_text, new_text, config)

        if report:
            st.session_state.report = report
            st.session_state.comparison_done = True
            st.session_state.config = config
            st.success("✅ Comparison completed successfully!")
            st.rerun()

    # Display results if comparison done
    if st.session_state.comparison_done and st.session_state.report:
        st.markdown("---")
        render_summary(st.session_state.report)

        st.markdown("---")
        render_detailed_changes(st.session_state.report)

        st.markdown("---")
        render_requirement_changes(st.session_state.report)

        st.markdown("---")
        render_export(st.session_state.report)

        # Reset button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            if st.button("🔄 Start New Comparison", use_container_width=True):
                st.session_state.comparison_done = False
                st.session_state.report = None
                st.rerun()


if __name__ == "__main__":
    main()
