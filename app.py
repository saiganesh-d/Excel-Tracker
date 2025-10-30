"""
Unified Document Comparison Tool
Supports both Excel and PDF document comparisons
"""

import streamlit as st

# Configure page
st.set_page_config(
    page_title="Document Comparison Suite",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 30px;
    }

    .tool-card {
        background: #2d2d30;
        border: 2px solid #464647;
        border-radius: 10px;
        padding: 30px;
        margin: 20px 0;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .tool-card:hover {
        border-color: #007ACC;
        transform: translateY(-5px);
        box-shadow: 0 5px 20px rgba(0, 122, 204, 0.3);
    }

    .tool-icon {
        font-size: 48px;
        margin-bottom: 15px;
    }

    .tool-title {
        font-size: 24px;
        font-weight: bold;
        color: #007ACC;
        margin-bottom: 10px;
    }

    .tool-description {
        color: #cccccc;
        line-height: 1.6;
    }

    .feature-list {
        list-style: none;
        padding-left: 0;
        margin-top: 15px;
    }

    .feature-list li {
        padding: 5px 0;
        color: #d4d4d4;
    }

    .feature-list li:before {
        content: "✓ ";
        color: #57ab5a;
        font-weight: bold;
        margin-right: 8px;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main application entry point"""

    # Check if a tool is selected
    if 'selected_tool' not in st.session_state:
        st.session_state['selected_tool'] = None

    # Tool selection or show selected tool
    if st.session_state['selected_tool'] is None:
        show_tool_selection()
    elif st.session_state['selected_tool'] == 'excel':
        show_excel_comparison()
    elif st.session_state['selected_tool'] == 'pdf':
        show_pdf_comparison()
    elif st.session_state['selected_tool'] == 'pdf_optimized':
        show_pdf_comparison_optimized()
    elif st.session_state['selected_tool'] == 'pdf_advanced':
        show_pdf_comparison_advanced()


def show_tool_selection():
    """Display tool selection screen"""

    st.markdown("""
    <div class="main-header">
        <h1>🔍 Document Comparison Suite</h1>
        <p>Professional tools for analysts to compare Excel spreadsheets and PDF documents</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Choose Your Comparison Tool")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="tool-card">
            <div class="tool-icon">📊</div>
            <div class="tool-title">Excel Diff Visualizer</div>
            <div class="tool-description">
                Compare Excel spreadsheets with VS Code-style synchronized scrolling.
                Perfect for tracking template modifications.

                <ul class="feature-list">
                    <li>Synchronized horizontal & vertical scrolling</li>
                    <li>Cell-by-cell change tracking</li>
                    <li>Column header naming</li>
                    <li>Visual highlighting of modifications</li>
                    <li>Export to Excel, JSON, or Text</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 Launch Excel Comparison", key="launch_excel", type="primary", use_container_width=True):
            st.session_state['selected_tool'] = 'excel'
            st.rerun()

    with col2:
        st.markdown("""
        <div class="tool-card">
            <div class="tool-icon">🤖</div>
            <div class="tool-title">Advanced PDF Comparison (AI-Powered)</div>
            <div class="tool-description">
                Next-generation PDF comparison with semantic understanding,
                requirement tracking, and optional AI explanations.

                <ul class="feature-list">
                    <li>🧠 Semantic understanding (95%+ accuracy)</li>
                    <li>🌍 Multi-language support (50+ languages)</li>
                    <li>📋 Requirement analysis (MUST/SHALL/SHOULD)</li>
                    <li>🤖 Optional AI explanations</li>
                    <li>🔒 100% local processing (privacy-first)</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 Launch Advanced PDF", key="launch_pdf_adv", type="primary", use_container_width=True):
            st.session_state['selected_tool'] = 'pdf_advanced'
            st.rerun()

    # Show older PDF tools in expander
    with st.expander("📄 Other PDF Comparison Tools (Legacy)"):
        col3, col4 = st.columns(2)

        with col3:
            st.markdown("**PDF Structure Comparison**")
            st.markdown("Hierarchical section matching, handles reordering")
            if st.button("Launch PDF Structure", key="launch_pdf", use_container_width=True):
                st.session_state['selected_tool'] = 'pdf'
                st.rerun()

        with col4:
            st.markdown("**PDF Comparison (Fast)**")
            st.markdown("Optimized for large documents, dropdown navigation")
            if st.button("Launch Fast PDF", key="launch_pdf_opt", use_container_width=True):
                st.session_state['selected_tool'] = 'pdf_optimized'
                st.rerun()

    # Information section
    st.markdown("---")
    st.markdown("""
    ### 📖 About This Tool Suite

    This suite provides professional-grade document comparison tools designed for analysts who need to:

    - **Track supplier modifications** to templates and requirement documents
    - **Identify structural changes** that may affect compliance
    - **Quickly spot critical changes** without manual review
    - **Generate reports** for stakeholders and audit trails

    #### Use Cases:

    - **Excel Comparison**: Template modifications, data validation, financial reports, inventory tracking
    - **PDF Comparison**: Requirement documents, security guidelines, contract modifications, policy updates

    #### Getting Started:

    1. Select the tool type above (Excel or PDF)
    2. Upload your original template/document
    3. Upload the modified version
    4. Click "Compare" to see intelligent analysis
    5. Export results in your preferred format
    """)


def show_excel_comparison():
    """Show Excel comparison tool"""

    # Add back button in sidebar
    with st.sidebar:
        if st.button("⬅️ Back to Tool Selection", key="back_from_excel"):
            st.session_state['selected_tool'] = None
            # Clear Excel-related session state
            for key in list(st.session_state.keys()):
                if key.startswith('original_file') or key.startswith('modified_file') or key.startswith('comparison'):
                    del st.session_state[key]
            st.rerun()

        st.divider()

    # Import and run Excel comparison
    from main import main as excel_main
    excel_main()


def show_pdf_comparison():
    """Show PDF comparison tool"""

    # Add back button in sidebar
    with st.sidebar:
        if st.button("⬅️ Back to Tool Selection", key="back_from_pdf"):
            st.session_state['selected_tool'] = None
            # Clear PDF-related session state
            for key in list(st.session_state.keys()):
                if key.startswith('pdf_'):
                    del st.session_state[key]
            st.rerun()

        st.divider()

    # Import and run PDF comparison
    from pdf_compare_ui import create_pdf_comparison_ui
    create_pdf_comparison_ui()


def show_pdf_comparison_optimized():
    """Show optimized PDF comparison tool"""

    # Add back button in sidebar
    with st.sidebar:
        if st.button("⬅️ Back to Tool Selection", key="back_from_pdf_opt"):
            st.session_state['selected_tool'] = None
            # Clear PDF-related session state
            for key in list(st.session_state.keys()):
                if key.startswith('pdf_opt_'):
                    del st.session_state[key]
            st.rerun()

        st.divider()

    # Import and run optimized PDF comparison
    from pdf_compare_ui_optimized import create_optimized_pdf_ui
    create_optimized_pdf_ui()


def show_pdf_comparison_advanced():
    """Show advanced AI-powered PDF comparison tool"""

    # Add back button in sidebar
    with st.sidebar:
        if st.button("⬅️ Back to Tool Selection", key="back_from_pdf_adv"):
            st.session_state['selected_tool'] = None
            # Clear PDF-related session state
            for key in list(st.session_state.keys()):
                if key.startswith('pdf_adv_') or key in ['comparison_done', 'report', 'config']:
                    del st.session_state[key]
            st.rerun()

        st.divider()

    # Import and run advanced PDF comparison
    from pdf_compare_ui_advanced import main as advanced_pdf_main
    advanced_pdf_main()


if __name__ == "__main__":
    main()
