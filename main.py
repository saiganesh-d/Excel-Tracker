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
import difflib
import html
import streamlit.components.v1 as components

# Page configuration
st.set_page_config(
    page_title="Excel Diff Visualizer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for VS Code-style diff visualization
st.markdown("""
<style>
    .diff-container {
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        font-size: 13px;
        background: #1e1e1e;
        border-radius: 6px;
        padding: 10px;
        margin: 10px 0;
        overflow: hidden;
    }
    
    .diff-header {
        background: #2d2d30;
        color: #cccccc;
        padding: 8px 12px;
        border-radius: 4px 4px 0 0;
        font-weight: bold;
        border-bottom: 1px solid #464647;
    }
    
    .diff-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2px;
        background: #2d2d30;
        padding: 1px;
    }
    
    .diff-side {
        background: #1e1e1e;
        overflow: auto;
        max-height: 500px;
        max-width: 100%;
    }
    
    .diff-side-header {
        background: #2d2d30;
        color: #969696;
        padding: 6px 12px;
        font-size: 12px;
        border-bottom: 1px solid #464647;
        position: sticky;
        top: 0;
        z-index: 10;
    }
    
    .diff-content {
        overflow-x: auto;
        overflow-y: auto;
        max-height: 450px;
        width: 100%;
    }
    
    .diff-table {
        display: table;
        width: max-content;
        min-width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        table-layout: fixed;
    }
    
    .diff-line {
        display: table-row;
        min-height: 22px;
        white-space: nowrap;
    }
    
    .line-number {
        display: table-cell;
        background: #2d2d30;
        color: #858585;
        padding: 4px 8px;
        width: 50px;
        min-width: 50px;
        max-width: 50px;
        text-align: right;
        border-right: 1px solid #464647;
        user-select: none;
        position: sticky;
        left: 0;
        z-index: 5;
        vertical-align: middle;
    }
    
    .line-content {
        display: table-cell;
        padding: 0;
        white-space: nowrap;
        vertical-align: middle;
    }
    
    .cell-data {
        display: inline-block;
        padding: 4px 12px;
        width: 120px;
        min-width: 120px;
        border-right: 1px solid #3a3a3a;
        border-bottom: 1px solid #3a3a3a;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        vertical-align: middle;
        box-sizing: border-box;
    }
    
    .cell-data:hover {
        overflow: visible;
        background: rgba(255, 255, 255, 0.05);
        position: relative;
        z-index: 2;
        max-width: none;
        width: auto;
    }
    
    /* Diff highlighting colors - VS Code style */
    .diff-modified {
        background: rgba(210, 153, 34, 0.15) !important;
    }
    
    .diff-modified .line-number {
        background: #3d3319 !important;
        color: #d29922;
    }
    
    .diff-unchanged {
        background: #1e1e1e;
        color: #d4d4d4;
    }
    
    /* Cell highlighting for modifications */
    .cell-empty {
        color: #6a6a6a;
        font-style: italic;
        opacity: 0.6;
    }
    
    .cell-value-old {
        background: rgba(229, 83, 75, 0.2) !important;
        color: #f85149 !important;
        padding: 2px 6px;
        border-radius: 2px;
        text-decoration: line-through;
    }
    
    .cell-value-new {
        background: rgba(87, 171, 90, 0.2) !important;
        color: #57ab5a !important;
        padding: 2px 6px;
        border-radius: 2px;
        font-weight: bold;
    }
    
    /* Column headers */
    .header-row {
        background: #2d2d30 !important;
        font-weight: bold;
        position: sticky;
        top: 0;
        z-index: 6;
        border-bottom: 2px solid #464647;
    }
    
    .header-row .cell-data {
        background: #2d2d30;
        color: #007ACC;
        font-weight: bold;
        border-right: 1px solid #464647;
        border-bottom: 2px solid #464647;
    }
    
    .header-row .line-number {
        background: #2d2d30;
        border-bottom: 2px solid #464647;
    }
    
    /* Stats cards */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin: 20px 0;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .stat-card.modified {
        background: linear-gradient(135deg, #d29922 0%, #b87c1b 100%);
    }
    
    .stat-card.to-empty {
        background: linear-gradient(135deg, #e5534b 0%, #c73e36 100%);
    }
    
    .stat-card.from-empty {
        background: linear-gradient(135deg, #57ab5a 0%, #40916c 100%);
    }
    
    .stat-number {
        font-size: 32px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    
    .stat-label {
        font-size: 14px;
        opacity: 0.9;
    }
    
    /* Sync scroll indicator */
    .sync-indicator {
        background: #007ACC;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 11px;
        margin-left: 10px;
    }
    
    /* Change list styling */
    .change-item {
        background: #2d2d30;
        border: 1px solid #464647;
        border-radius: 4px;
        padding: 10px;
        margin: 5px 0;
        font-family: monospace;
    }
    
    .change-location {
        color: #007ACC;
        font-weight: bold;
    }
    
    .change-arrow {
        color: #d29922;
        margin: 0 8px;
    }
    
    .value-empty {
        color: #6a6a6a;
        font-style: italic;
    }
    
    .value-old {
        color: #f85149;
        text-decoration: line-through;
    }
    
    .value-new {
        color: #57ab5a;
        font-weight: bold;
    }
    
    /* Scrollbar styling */
    .diff-content::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    .diff-content::-webkit-scrollbar-track {
        background: #2d2d30;
    }
    
    .diff-content::-webkit-scrollbar-thumb {
        background: #464647;
        border-radius: 5px;
    }
    
    .diff-content::-webkit-scrollbar-thumb:hover {
        background: #565658;
    }
    
    .diff-content::-webkit-scrollbar-corner {
        background: #2d2d30;
    }
</style>
""", unsafe_allow_html=True)

class ExcelDiffVisualizer:
    def __init__(self, original_file, modified_file):
        self.original_wb = openpyxl.load_workbook(original_file, data_only=True)
        self.modified_wb = openpyxl.load_workbook(modified_file, data_only=True)
        self.changes = {}
        self.summary = {
            'total_modifications': 0,
            'sheets_modified': [],
            'blank_to_value': 0,  # Previously "added"
            'value_to_blank': 0,  # Previously "removed"
            'value_to_value': 0,  # Previously "modified"
        }
    
    def get_sheet_as_dataframe(self, sheet):
        """Convert sheet to DataFrame for easier comparison"""
        data = []
        max_row = sheet.max_row
        max_col = sheet.max_column
        
        # Store headers separately (assuming first row contains headers)
        headers = {}
        if max_row >= 1:
            for col in range(1, max_col + 1):
                cell = sheet.cell(row=1, column=col)
                if cell.value:
                    headers[col] = str(cell.value)
                else:
                    headers[col] = get_column_letter(col)
        
        for row in range(1, max_row + 1):
            row_data = []
            for col in range(1, max_col + 1):
                cell = sheet.cell(row=row, column=col)
                # Store None for empty cells to distinguish from empty string
                row_data.append(cell.value if cell.value is not None else None)
            data.append(row_data)
        
        # Create column headers
        columns = [get_column_letter(i) for i in range(1, max_col + 1)]
        
        if data:
            df = pd.DataFrame(data, columns=columns[:len(data[0])])
        else:
            df = pd.DataFrame()
        
        # Store headers for later use
        self.column_headers = headers
        
        return df
    
    def compare_sheets(self):
        """Compare all sheets in the workbooks"""
        all_sheets = set(self.original_wb.sheetnames) | set(self.modified_wb.sheetnames)
        
        for sheet_name in all_sheets:
            sheet_changes = {
                'modifications': [],  # All changes are now modifications
                'sheet_added': False,
                'sheet_removed': False,
                'original_df': None,
                'modified_df': None,
                'column_headers': {}
            }
            
            # Check if sheet exists in both workbooks
            if sheet_name not in self.original_wb.sheetnames:
                sheet_changes['sheet_added'] = True
                sheet_changes['modified_df'] = self.get_sheet_as_dataframe(self.modified_wb[sheet_name])
                sheet_changes['column_headers'] = getattr(self, 'column_headers', {})
                self.summary['sheets_modified'].append(f"{sheet_name} (New Sheet)")
            elif sheet_name not in self.modified_wb.sheetnames:
                sheet_changes['sheet_removed'] = True
                sheet_changes['original_df'] = self.get_sheet_as_dataframe(self.original_wb[sheet_name])
                sheet_changes['column_headers'] = getattr(self, 'column_headers', {})
                self.summary['sheets_modified'].append(f"{sheet_name} (Sheet Removed)")
            else:
                # Get both sheets as DataFrames
                original_sheet = self.original_wb[sheet_name]
                modified_sheet = self.modified_wb[sheet_name]
                
                sheet_changes['original_df'] = self.get_sheet_as_dataframe(original_sheet)
                original_headers = dict(getattr(self, 'column_headers', {}))
                
                sheet_changes['modified_df'] = self.get_sheet_as_dataframe(modified_sheet)
                modified_headers = dict(getattr(self, 'column_headers', {}))
                
                # Use modified headers as primary, fall back to original if needed
                sheet_changes['column_headers'] = modified_headers or original_headers
                
                # Get max dimensions for both sheets
                max_row = max(original_sheet.max_row, modified_sheet.max_row, 10)  # At least 10 rows
                max_col = max(original_sheet.max_column, modified_sheet.max_column, 5)  # At least 5 columns
                
                # Compare all cells in the grid
                has_changes = False
                for row in range(1, max_row + 1):
                    for col in range(1, max_col + 1):
                        orig_cell = original_sheet.cell(row=row, column=col)
                        mod_cell = modified_sheet.cell(row=row, column=col)
                        
                        orig_val = orig_cell.value
                        mod_val = mod_cell.value
                        
                        # Only track if there's an actual change
                        if orig_val != mod_val:
                            change_type = self._categorize_change(orig_val, mod_val)
                            
                            # Get column header name for better description
                            col_header = sheet_changes['column_headers'].get(col, get_column_letter(col))
                            
                            sheet_changes['modifications'].append({
                                'cell': (row, col),
                                'cell_ref': f"{get_column_letter(col)}{row}",
                                'column_name': col_header,
                                'row_number': row,
                                'old_value': orig_val,
                                'new_value': mod_val,
                                'row': row,
                                'col': col,
                                'change_type': change_type
                            })
                            
                            # Update summary
                            if change_type == 'blank_to_value':
                                self.summary['blank_to_value'] += 1
                            elif change_type == 'value_to_blank':
                                self.summary['value_to_blank'] += 1
                            else:
                                self.summary['value_to_value'] += 1
                            
                            has_changes = True
                            self.summary['total_modifications'] += 1
                
                if has_changes:
                    self.summary['sheets_modified'].append(sheet_name)
            
            self.changes[sheet_name] = sheet_changes
        
        return self.changes
    
    def _categorize_change(self, old_value, new_value):
        """Categorize the type of modification"""
        if old_value is None and new_value is not None:
            return 'blank_to_value'
        elif old_value is not None and new_value is None:
            return 'value_to_blank'
        else:
            return 'value_to_value'
    
    def _format_value(self, value):
        """Format value for display"""
        if value is None:
            return "[empty]"
        elif isinstance(value, (int, float)):
            return str(value)
        else:
            return str(value)
    
    def create_synchronized_diff_component(self, sheet_name):
        """Create synchronized diff view using Streamlit components for true scrolling sync"""
        sheet_changes = self.changes.get(sheet_name, {})
        
        if sheet_changes.get('sheet_added') or sheet_changes.get('sheet_removed'):
            # For added/removed sheets, use the regular view
            return self.create_vs_code_diff_html(sheet_name)
        
        original_df = sheet_changes.get('original_df', pd.DataFrame())
        modified_df = sheet_changes.get('modified_df', pd.DataFrame())
        column_headers = sheet_changes.get('column_headers', {})
        
        # Get max dimensions
        max_rows = max(len(original_df) if not original_df.empty else 10,
                      len(modified_df) if not modified_df.empty else 10, 10)
        max_cols = max(len(original_df.columns) if not original_df.empty else 5,
                      len(modified_df.columns) if not modified_df.empty else 5, 5)
        
        # Build change map
        change_map = {}
        for mod in sheet_changes.get('modifications', []):
            change_map[(mod['row']-1, mod['col']-1)] = mod
        
        # Clean sheet name for IDs
        sheet_id = sheet_name.replace(' ', '_').replace('(', '').replace(')', '')
        
        # Generate HTML for original side
        original_html = self._generate_table_html(
            original_df, column_headers, change_map, max_rows, max_cols, is_original=True
        )
        
        # Generate HTML for modified side
        modified_html = self._generate_table_html(
            modified_df, column_headers, change_map, max_rows, max_cols, is_original=False
        )
        
        # Create full HTML with embedded JavaScript for synchronized scrolling
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                    background: #1e1e1e;
                    color: #d4d4d4;
                }}
                
                .diff-container {{
                    background: #1e1e1e;
                    border-radius: 6px;
                    overflow: hidden;
                    height: 100vh;
                    display: flex;
                    flex-direction: column;
                }}
                
                .diff-header {{
                    background: #2d2d30;
                    color: #cccccc;
                    padding: 10px 15px;
                    font-weight: bold;
                    border-bottom: 1px solid #464647;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    flex-shrink: 0;
                }}
                
                .sync-badge {{
                    background: #28a745;
                    color: white;
                    padding: 4px 10px;
                    border-radius: 4px;
                    font-size: 11px;
                    animation: pulse 2s infinite;
                }}
                
                @keyframes pulse {{
                    0% {{ opacity: 1; }}
                    50% {{ opacity: 0.7; }}
                    100% {{ opacity: 1; }}
                }}
                
                .diff-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 2px;
                    background: #2d2d30;
                    padding: 1px;
                    flex: 1;
                    overflow: hidden;
                }}
                
                .diff-side {{
                    background: #1e1e1e;
                    display: flex;
                    flex-direction: column;
                    overflow: hidden;
                }}
                
                .diff-side-header {{
                    background: #2d2d30;
                    color: #969696;
                    padding: 8px 15px;
                    font-size: 12px;
                    border-bottom: 1px solid #464647;
                    flex-shrink: 0;
                }}
                
                .diff-content {{
                    overflow: auto;
                    flex: 1;
                }}
                
                .diff-table {{
                    display: table;
                    width: max-content;
                    min-width: 100%;
                    border-collapse: separate;
                    border-spacing: 0;
                }}
                
                .diff-line {{
                    display: table-row;
                    height: 28px;
                }}
                
                .diff-line:hover {{
                    background: rgba(255, 255, 255, 0.05) !important;
                }}
                
                .line-number {{
                    display: table-cell;
                    background: #2d2d30;
                    color: #858585;
                    padding: 4px 8px;
                    width: 50px;
                    min-width: 50px;
                    max-width: 50px;
                    text-align: right;
                    border-right: 1px solid #464647;
                    position: sticky;
                    left: 0;
                    z-index: 5;
                    user-select: none;
                    vertical-align: middle;
                    box-sizing: border-box;
                }}
                
                .line-content {{
                    display: table-cell;
                    padding: 0;
                    vertical-align: middle;
                }}
                
                .cell-data {{
                    display: inline-block;
                    padding: 4px 12px;
                    width: 120px;
                    min-width: 120px;
                    border-right: 1px solid #3a3a3a;
                    border-bottom: 1px solid #3a3a3a;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    vertical-align: middle;
                    box-sizing: border-box;
                    height: 28px;
                    line-height: 20px;
                }}
                
                .cell-data:hover {{
                    overflow: visible;
                    background: rgba(255, 255, 255, 0.05);
                    position: relative;
                    z-index: 2;
                    max-width: none;
                }}
                
                .header-row {{
                    background: #2d2d30 !important;
                    font-weight: bold;
                    position: sticky;
                    top: 0;
                    z-index: 6;
                    height: 32px;
                }}
                
                .header-row .cell-data {{
                    background: #2d2d30;
                    color: #007ACC;
                    font-weight: bold;
                    border-right: 1px solid #464647;
                    border-bottom: 2px solid #464647;
                    height: 32px;
                    line-height: 24px;
                }}
                
                .header-row .line-number {{
                    background: #2d2d30;
                    border-bottom: 2px solid #464647;
                    height: 32px;
                }}
                
                .diff-modified {{
                    background: rgba(210, 153, 34, 0.15) !important;
                }}
                
                .diff-modified .line-number {{
                    background: #3d3319 !important;
                    color: #d29922;
                }}
                
                .cell-empty {{
                    color: #6a6a6a;
                    font-style: italic;
                    opacity: 0.6;
                }}
                
                .cell-value-old {{
                    background: rgba(229, 83, 75, 0.2);
                    color: #f85149;
                    padding: 2px 6px;
                    border-radius: 2px;
                    text-decoration: line-through;
                }}
                
                .cell-value-new {{
                    background: rgba(87, 171, 90, 0.2);
                    color: #57ab5a;
                    padding: 2px 6px;
                    border-radius: 2px;
                    font-weight: bold;
                }}
                
                /* Scrollbar styling */
                ::-webkit-scrollbar {{
                    width: 10px;
                    height: 10px;
                }}
                
                ::-webkit-scrollbar-track {{
                    background: #2d2d30;
                }}
                
                ::-webkit-scrollbar-thumb {{
                    background: #464647;
                    border-radius: 5px;
                }}
                
                ::-webkit-scrollbar-thumb:hover {{
                    background: #565658;
                }}
                
                ::-webkit-scrollbar-corner {{
                    background: #2d2d30;
                }}
            </style>
        </head>
        <body>
            <div class="diff-container">
                <div class="diff-header">
                    📊 Sheet: {sheet_name}
                    <span class="sync-badge">⟷ SYNCHRONIZED SCROLLING ACTIVE</span>
                </div>
                <div class="diff-grid">
                    <div class="diff-side">
                        <div class="diff-side-header">📁 Original</div>
                        <div class="diff-content" id="original-{sheet_id}">
                            {original_html}
                        </div>
                    </div>
                    <div class="diff-side">
                        <div class="diff-side-header">📝 Modified</div>
                        <div class="diff-content" id="modified-{sheet_id}">
                            {modified_html}
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                // Synchronized scrolling implementation
                (function() {{
                    const original = document.getElementById('original-{sheet_id}');
                    const modified = document.getElementById('modified-{sheet_id}');
                    
                    if (original && modified) {{
                        let isSyncing = false;
                        
                        // Function to sync scroll positions
                        function syncScroll(source, target) {{
                            if (!isSyncing) {{
                                isSyncing = true;
                                target.scrollTop = source.scrollTop;
                                target.scrollLeft = source.scrollLeft;
                                
                                // Reset flag after a small delay
                                requestAnimationFrame(() => {{
                                    isSyncing = false;
                                }});
                            }}
                        }}
                        
                        // Add scroll listeners
                        original.addEventListener('scroll', function() {{
                            syncScroll(original, modified);
                        }});
                        
                        modified.addEventListener('scroll', function() {{
                            syncScroll(modified, original);
                        }});
                        
                        // Log that synchronization is active
                        console.log('✅ Synchronized scrolling activated for sheet: {sheet_name}');
                    }} else {{
                        console.error('❌ Could not find elements for synchronization');
                    }}
                }})();
            </script>
        </body>
        </html>
        """
        
        return full_html
    
    def _generate_table_html(self, df, column_headers, change_map, max_rows, max_cols, is_original=True):
        """Generate HTML table for one side of the diff"""
        html_output = '<div class="diff-table">'
        
        # Add column headers
        html_output += '<div class="diff-line header-row"><div class="line-number">⬜</div><div class="line-content">'
        for col_idx in range(max_cols):
            col_num = col_idx + 1
            if col_num in column_headers:
                header = column_headers[col_num]
            elif col_idx < len(df.columns) if not df.empty else 0:
                header = df.columns[col_idx]
            else:
                header = get_column_letter(col_num)
            html_output += f'<div class="cell-data">{html.escape(str(header))}</div>'
        html_output += '</div></div>'
        
        # Add data rows
        for row_idx in range(max_rows):
            row_has_changes = any((row_idx, col) in change_map for col in range(max_cols))
            
            html_output += f'<div class="diff-line'
            if row_has_changes:
                html_output += ' diff-modified'
            html_output += f'"><div class="line-number">{row_idx + 1}</div><div class="line-content">'
            
            for col_idx in range(max_cols):
                cell_html = '<div class="cell-data">'
                
                if not df.empty and row_idx < len(df) and col_idx < len(df.columns):
                    value = df.iloc[row_idx, col_idx]
                    
                    if (row_idx, col_idx) in change_map:
                        if value is None:
                            cell_html += '<span class="cell-empty">[empty]</span>'
                        else:
                            if is_original:
                                cell_html += f'<span class="cell-value-old">{html.escape(str(value))}</span>'
                            else:
                                cell_html += f'<span class="cell-value-new">{html.escape(str(value))}</span>'
                    else:
                        if value is None:
                            cell_html += '<span class="cell-empty">·</span>'
                        else:
                            cell_html += html.escape(str(value))
                else:
                    cell_html += '<span class="cell-empty">·</span>'
                
                cell_html += '</div>'
                html_output += cell_html
            
            html_output += '</div></div>'
        
        html_output += '</div>'
        return html_output
    
    def create_vs_code_diff_html(self, sheet_name):
        """Create VS Code style diff visualization for a sheet"""
        sheet_changes = self.changes.get(sheet_name, {})
        
        if sheet_changes.get('sheet_added'):
            return self._create_added_sheet_view(sheet_changes['modified_df'], sheet_name)
        elif sheet_changes.get('sheet_removed'):
            return self._create_removed_sheet_view(sheet_changes['original_df'], sheet
