import streamlit as st
import pandas as pd
import openpyxl
from openpyxl.styles import PatternFill, Font, Border, Side
from openpyxl.utils import get_column_letter
import numpy as np
from datetime import datetime
import json
import io
import base64
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Excel Change Visualizer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .change-added {
        background-color: #d4edda !important;
        color: #155724;
        padding: 5px;
        border-radius: 3px;
        margin: 2px;
    }
    .change-removed {
        background-color: #f8d7da !important;
        color: #721c24;
        padding: 5px;
        border-radius: 3px;
        margin: 2px;
    }
    .change-modified {
        background-color: #fff3cd !important;
        color: #856404;
        padding: 5px;
        border-radius: 3px;
        margin: 2px;
    }
    .summary-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #007bff;
        margin-bottom: 20px;
    }
    .sheet-tab {
        padding: 10px 20px;
        margin: 5px;
        border-radius: 5px;
        background-color: #e9ecef;
        cursor: pointer;
    }
    .sheet-tab-active {
        background-color: #007bff;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

class ExcelComparator:
    def __init__(self, original_file, modified_file):
        self.original_wb = openpyxl.load_workbook(original_file, data_only=True)
        self.modified_wb = openpyxl.load_workbook(modified_file, data_only=True)
        self.changes = {}
        self.summary = {
            'total_changes': 0,
            'sheets_modified': [],
            'cells_added': 0,
            'cells_removed': 0,
            'cells_modified': 0,
            'rows_added': [],
            'rows_removed': [],
            'columns_added': [],
            'columns_removed': []
        }
    
    def compare_sheets(self):
        """Compare all sheets in the workbooks"""
        all_sheets = set(self.original_wb.sheetnames) | set(self.modified_wb.sheetnames)
        
        for sheet_name in all_sheets:
            sheet_changes = {
                'added_cells': [],
                'removed_cells': [],
                'modified_cells': [],
                'added_rows': set(),
                'removed_rows': set(),
                'added_cols': set(),
                'removed_cols': set(),
                'sheet_added': False,
                'sheet_removed': False
            }
            
            # Check if sheet exists in both workbooks
            if sheet_name not in self.original_wb.sheetnames:
                sheet_changes['sheet_added'] = True
                self.summary['sheets_modified'].append(f"{sheet_name} (Added)")
            elif sheet_name not in self.modified_wb.sheetnames:
                sheet_changes['sheet_removed'] = True
                self.summary['sheets_modified'].append(f"{sheet_name} (Removed)")
            else:
                # Compare cells in the sheet
                original_sheet = self.original_wb[sheet_name]
                modified_sheet = self.modified_wb[sheet_name]
                
                # Get all cells with values
                original_cells = self._get_sheet_data(original_sheet)
                modified_cells = self._get_sheet_data(modified_sheet)
                
                # Find changes
                all_coords = set(original_cells.keys()) | set(modified_cells.keys())
                
                for coord in all_coords:
                    orig_val = original_cells.get(coord, None)
                    mod_val = modified_cells.get(coord, None)
                    
                    if orig_val is None and mod_val is not None:
                        # Cell added
                        sheet_changes['added_cells'].append({
                            'cell': coord,
                            'value': mod_val,
                            'row': coord[0],
                            'col': coord[1]
                        })
                        sheet_changes['added_rows'].add(coord[0])
                        sheet_changes['added_cols'].add(coord[1])
                        self.summary['cells_added'] += 1
                        
                    elif orig_val is not None and mod_val is None:
                        # Cell removed
                        sheet_changes['removed_cells'].append({
                            'cell': coord,
                            'value': orig_val,
                            'row': coord[0],
                            'col': coord[1]
                        })
                        sheet_changes['removed_rows'].add(coord[0])
                        sheet_changes['removed_cols'].add(coord[1])
                        self.summary['cells_removed'] += 1
                        
                    elif orig_val != mod_val:
                        # Cell modified
                        sheet_changes['modified_cells'].append({
                            'cell': coord,
                            'old_value': orig_val,
                            'new_value': mod_val,
                            'row': coord[0],
                            'col': coord[1]
                        })
                        self.summary['cells_modified'] += 1
                
                if any([sheet_changes['added_cells'], sheet_changes['removed_cells'], 
                       sheet_changes['modified_cells']]):
                    self.summary['sheets_modified'].append(sheet_name)
            
            self.changes[sheet_name] = sheet_changes
        
        self.summary['total_changes'] = (self.summary['cells_added'] + 
                                        self.summary['cells_removed'] + 
                                        self.summary['cells_modified'])
        return self.changes
    
    def _get_sheet_data(self, sheet):
        """Extract all non-empty cells from a sheet"""
        data = {}
        for row in sheet.iter_rows():
            for cell in row:
                if cell.value is not None:
                    data[(cell.row, cell.column)] = cell.value
        return data
    
    def create_diff_excel(self):
        """Create an Excel file with changes highlighted"""
        diff_wb = openpyxl.Workbook()
        diff_wb.remove(diff_wb.active)  # Remove default sheet
        
        # Define fill colors
        green_fill = PatternFill(start_color="90EE90", end_color="90EE90", fill_type="solid")
        red_fill = PatternFill(start_color="FFB6C1", end_color="FFB6C1", fill_type="solid")
        yellow_fill = PatternFill(start_color="FFFF99", end_color="FFFF99", fill_type="solid")
        
        for sheet_name, sheet_changes in self.changes.items():
            if sheet_changes['sheet_removed']:
                continue
                
            # Create sheet in diff workbook
            diff_sheet = diff_wb.create_sheet(sheet_name)
            
            # Copy modified sheet as base
            if sheet_name in self.modified_wb.sheetnames:
                source_sheet = self.modified_wb[sheet_name]
                
                # Copy all cells
                for row in source_sheet.iter_rows():
                    for cell in row:
                        new_cell = diff_sheet.cell(row=cell.row, column=cell.column, value=cell.value)
                        
                        # Check if this cell has changes
                        coord = (cell.row, cell.column)
                        
                        # Apply highlighting based on change type
                        for added in sheet_changes['added_cells']:
                            if added['cell'] == coord:
                                new_cell.fill = green_fill
                                new_cell.comment = openpyxl.comments.Comment(
                                    f"Added: {added['value']}", "Change Tracker"
                                )
                        
                        for modified in sheet_changes['modified_cells']:
                            if modified['cell'] == coord:
                                new_cell.fill = yellow_fill
                                new_cell.comment = openpyxl.comments.Comment(
                                    f"Changed from: {modified['old_value']}", "Change Tracker"
                                )
                
                # Mark removed cells
                if sheet_name in self.original_wb.sheetnames:
                    for removed in sheet_changes['removed_cells']:
                        cell = diff_sheet.cell(row=removed['row'], column=removed['col'])
                        cell.fill = red_fill
                        cell.value = f"[REMOVED: {removed['value']}]"
                        cell.comment = openpyxl.comments.Comment(
                            f"Removed: {removed['value']}", "Change Tracker"
                        )
        
        # Add summary sheet
        summary_sheet = diff_wb.create_sheet("CHANGE_SUMMARY", 0)
        summary_data = [
            ["Change Summary Report", ""],
            ["Generated on:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["", ""],
            ["Total Changes:", self.summary['total_changes']],
            ["Cells Added:", self.summary['cells_added']],
            ["Cells Removed:", self.summary['cells_removed']],
            ["Cells Modified:", self.summary['cells_modified']],
            ["", ""],
            ["Sheets Modified:", ", ".join(self.summary['sheets_modified']) if self.summary['sheets_modified'] else "None"],
        ]
        
        for row_idx, row_data in enumerate(summary_data, 1):
            for col_idx, value in enumerate(row_data, 1):
                cell = summary_sheet.cell(row=row_idx, column=col_idx, value=value)
                if row_idx == 1:
                    cell.font = Font(bold=True, size=14)
                elif col_idx == 1 and row_idx > 3:
                    cell.font = Font(bold=True)
        
        return diff_wb

def create_change_visualization(changes, sheet_name):
    """Create HTML visualization of changes for a specific sheet"""
    sheet_changes = changes.get(sheet_name, {})
    
    if sheet_changes.get('sheet_added'):
        return "<div class='change-added'>📄 This sheet was added in the modified version</div>"
    elif sheet_changes.get('sheet_removed'):
        return "<div class='change-removed'>📄 This sheet was removed in the modified version</div>"
    
    html = "<div style='padding: 10px;'>"
    
    # Group changes by row for better visualization
    changes_by_row = {}
    
    for change in sheet_changes.get('modified_cells', []):
        row = change['row']
        if row not in changes_by_row:
            changes_by_row[row] = []
        changes_by_row[row].append({
            'type': 'modified',
            'col': change['col'],
            'old': change['old_value'],
            'new': change['new_value']
        })
    
    for change in sheet_changes.get('added_cells', []):
        row = change['row']
        if row not in changes_by_row:
            changes_by_row[row] = []
        changes_by_row[row].append({
            'type': 'added',
            'col': change['col'],
            'value': change['value']
        })
    
    for change in sheet_changes.get('removed_cells', []):
        row = change['row']
        if row not in changes_by_row:
            changes_by_row[row] = []
        changes_by_row[row].append({
            'type': 'removed',
            'col': change['col'],
            'value': change['value']
        })
    
    # Sort and display changes
    for row in sorted(changes_by_row.keys()):
        html += f"<h4>Row {row}:</h4>"
        html += "<div style='margin-left: 20px;'>"
        
        for change in sorted(changes_by_row[row], key=lambda x: x['col']):
            col_letter = get_column_letter(change['col'])
            
            if change['type'] == 'modified':
                html += f"""
                <div class='change-modified'>
                    📝 Cell {col_letter}{row}: 
                    <span style='text-decoration: line-through;'>{change['old']}</span> 
                    → <strong>{change['new']}</strong>
                </div>
                """
            elif change['type'] == 'added':
                html += f"""
                <div class='change-added'>
                    ➕ Cell {col_letter}{row}: <strong>{change['value']}</strong>
                </div>
                """
            elif change['type'] == 'removed':
                html += f"""
                <div class='change-removed'>
                    ➖ Cell {col_letter}{row}: <span style='text-decoration: line-through;'>{change['value']}</span>
                </div>
                """
        
        html += "</div>"
    
    html += "</div>"
    return html

# Main Streamlit App
def main():
    st.title("📊 Excel Change Visualizer")
    st.markdown("Compare Excel files and visualize changes made by clients")
    
    # Sidebar for file upload
    with st.sidebar:
        st.header("📁 Upload Files")
        
        original_file = st.file_uploader(
            "Upload Original Template", 
            type=['xlsx', 'xls'],
            help="Upload the original Excel template you sent to the client"
        )
        
        modified_file = st.file_uploader(
            "Upload Modified Version", 
            type=['xlsx', 'xls'],
            help="Upload the Excel file returned by the client with changes"
        )
        
        if st.button("🔍 Compare Files", type="primary", disabled=not (original_file and modified_file)):
            if original_file and modified_file:
                with st.spinner("Analyzing changes..."):
                    # Store files in session state
                    st.session_state['original_file'] = original_file
                    st.session_state['modified_file'] = modified_file
                    
                    # Perform comparison
                    comparator = ExcelComparator(original_file, modified_file)
                    changes = comparator.compare_sheets()
                    
                    st.session_state['changes'] = changes
                    st.session_state['comparator'] = comparator
                    st.session_state['comparison_done'] = True
    
    # Main content area
    if 'comparison_done' in st.session_state and st.session_state['comparison_done']:
        comparator = st.session_state['comparator']
        changes = st.session_state['changes']
        
        # Summary Dashboard
        st.header("📈 Change Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Changes", comparator.summary['total_changes'])
        with col2:
            st.metric("Cells Added", comparator.summary['cells_added'], delta="+", delta_color="normal")
        with col3:
            st.metric("Cells Removed", comparator.summary['cells_removed'], delta="-", delta_color="inverse")
        with col4:
            st.metric("Cells Modified", comparator.summary['cells_modified'], delta="~")
        
        # Sheet-wise changes
        st.header("📋 Sheet-wise Changes")
        
        if comparator.summary['sheets_modified']:
            # Create tabs for each modified sheet
            sheet_tabs = st.tabs(comparator.summary['sheets_modified'])
            
            for idx, sheet_name in enumerate(comparator.summary['sheets_modified']):
                with sheet_tabs[idx]:
                    # Clean sheet name (remove status indicators)
                    clean_name = sheet_name.replace(" (Added)", "").replace(" (Removed)", "")
                    
                    # Statistics for this sheet
                    sheet_changes = changes.get(clean_name, {})
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.info(f"✅ Added: {len(sheet_changes.get('added_cells', []))}")
                    with col2:
                        st.warning(f"📝 Modified: {len(sheet_changes.get('modified_cells', []))}")
                    with col3:
                        st.error(f"❌ Removed: {len(sheet_changes.get('removed_cells', []))}")
                    
                    # Display changes
                    st.subheader("Detailed Changes")
                    
                    # Use expandable sections for different change types
                    if sheet_changes.get('modified_cells'):
                        with st.expander(f"📝 Modified Cells ({len(sheet_changes['modified_cells'])})", expanded=True):
                            for change in sheet_changes['modified_cells']:
                                col_letter = get_column_letter(change['col'])
                                st.markdown(f"""
                                <div class='change-modified'>
                                    Cell **{col_letter}{change['row']}**: 
                                    ~{change['old_value']}~ → **{change['new_value']}**
                                </div>
                                """, unsafe_allow_html=True)
                    
                    if sheet_changes.get('added_cells'):
                        with st.expander(f"➕ Added Cells ({len(sheet_changes['added_cells'])})"):
                            for change in sheet_changes['added_cells']:
                                col_letter = get_column_letter(change['col'])
                                st.markdown(f"""
                                <div class='change-added'>
                                    Cell **{col_letter}{change['row']}**: {change['value']}
                                </div>
                                """, unsafe_allow_html=True)
                    
                    if sheet_changes.get('removed_cells'):
                        with st.expander(f"➖ Removed Cells ({len(sheet_changes['removed_cells'])})"):
                            for change in sheet_changes['removed_cells']:
                                col_letter = get_column_letter(change['col'])
                                st.markdown(f"""
                                <div class='change-removed'>
                                    Cell **{col_letter}{change['row']}**: ~{change['value']}~
                                </div>
                                """, unsafe_allow_html=True)
        else:
            st.info("No changes detected between the files")
        
        # Export options
        st.header("💾 Export Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Generate diff Excel
            if st.button("📊 Generate Diff Excel", type="primary"):
                with st.spinner("Creating diff file..."):
                    diff_wb = comparator.create_diff_excel()
                    
                    # Save to bytes
                    excel_buffer = io.BytesIO()
                    diff_wb.save(excel_buffer)
                    excel_buffer.seek(0)
                    
                    st.download_button(
                        label="⬇️ Download Diff Excel",
                        data=excel_buffer,
                        file_name=f"excel_diff_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        
        with col2:
            # Export change report as JSON
            if st.button("📄 Export Change Report"):
                change_report = {
                    'summary': comparator.summary,
                    'changes': changes,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Convert sets to lists for JSON serialization
                for sheet in change_report['changes']:
                    for key in ['added_rows', 'removed_rows', 'added_cols', 'removed_cols']:
                        if key in change_report['changes'][sheet]:
                            change_report['changes'][sheet][key] = list(change_report['changes'][sheet][key])
                
                json_str = json.dumps(change_report, indent=2, default=str)
                
                st.download_button(
                    label="⬇️ Download JSON Report",
                    data=json_str,
                    file_name=f"change_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with col3:
            # Generate HTML report
            if st.button("🌐 Generate HTML Report"):
                html_report = f"""
                <html>
                <head>
                    <title>Excel Change Report</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        .summary {{ background: #f0f0f0; padding: 15px; border-radius: 5px; }}
                        .change-added {{ background: #d4edda; padding: 5px; margin: 5px; border-radius: 3px; }}
                        .change-removed {{ background: #f8d7da; padding: 5px; margin: 5px; border-radius: 3px; }}
                        .change-modified {{ background: #fff3cd; padding: 5px; margin: 5px; border-radius: 3px; }}
                        h1, h2, h3 {{ color: #333; }}
                    </style>
                </head>
                <body>
                    <h1>Excel Change Report</h1>
                    <div class="summary">
                        <h2>Summary</h2>
                        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                        <p>Total Changes: {comparator.summary['total_changes']}</p>
                        <p>Cells Added: {comparator.summary['cells_added']}</p>
                        <p>Cells Removed: {comparator.summary['cells_removed']}</p>
                        <p>Cells Modified: {comparator.summary['cells_modified']}</p>
                    </div>
                """
                
                for sheet_name in comparator.summary['sheets_modified']:
                    clean_name = sheet_name.replace(" (Added)", "").replace(" (Removed)", "")
                    html_report += f"<h2>Sheet: {sheet_name}</h2>"
                    html_report += create_change_visualization(changes, clean_name)
                
                html_report += "</body></html>"
                
                st.download_button(
                    label="⬇️ Download HTML Report",
                    data=html_report,
                    file_name=f"change_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html"
                )
    
    else:
        # Instructions when no comparison has been done
        st.info("👈 Please upload both Excel files in the sidebar and click 'Compare Files' to start")
        
        with st.expander("📖 How to use this tool"):
            st.markdown("""
            1. **Upload Original Template**: Upload the Excel file you sent to your client
            2. **Upload Modified Version**: Upload the Excel file returned by your client
            3. **Click Compare Files**: The tool will analyze all changes
            4. **Review Changes**: View changes organized by sheet and type
            5. **Export Results**: Download the comparison as:
               - **Diff Excel**: Excel file with changes highlighted in colors
               - **JSON Report**: Machine-readable change report
               - **HTML Report**: Shareable web-based report
            
            **Color Coding:**
            - 🟢 **Green**: Added content
            - 🟡 **Yellow**: Modified content
            - 🔴 **Red**: Removed content
            """)

if __name__ == "__main__":
    main()
