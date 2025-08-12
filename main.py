<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Excel Diff - All Changes as Modifications</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1e1e1e;
            color: #d4d4d4;
            margin: 0;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        h1 {
            color: #007ACC;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #858585;
            margin-bottom: 30px;
        }
        
        /* Stats Cards */
        .stats-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 30px 0;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        
        .stat-card.from-empty {
            background: linear-gradient(135deg, #57ab5a 0%, #40916c 100%);
        }
        
        .stat-card.to-empty {
            background: linear-gradient(135deg, #e5534b 0%, #c73e36 100%);
        }
        
        .stat-card.value-change {
            background: linear-gradient(135deg, #d29922 0%, #b87c1b 100%);
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
        
        /* Diff Container with horizontal scrolling */
        .diff-container {
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 13px;
            background: #1e1e1e;
            border: 1px solid #464647;
            border-radius: 6px;
            margin: 20px 0;
            overflow: hidden;
        }
        
        .diff-header {
            background: #2d2d30;
            color: #cccccc;
            padding: 10px 15px;
            font-weight: bold;
            border-bottom: 1px solid #464647;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .sync-indicator {
            background: #007ACC;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
        }
        
        .diff-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            background: #464647;
            gap: 1px;
        }
        
        .diff-side {
            background: #1e1e1e;
            overflow: hidden;
        }
        
        .diff-side-header {
            background: #2d2d30;
            color: #969696;
            padding: 8px 15px;
            font-size: 12px;
            border-bottom: 1px solid #464647;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        
        .diff-content {
            overflow: auto;
            max-height: 400px;
            position: relative;
        }
        
        .diff-table {
            display: table;
            width: max-content;
            min-width: 100%;
            border-collapse: collapse;
        }
        
        .diff-line {
            display: table-row;
            min-height: 24px;
            white-space: nowrap;
        }
        
        .diff-line:hover {
            background: rgba(255, 255, 255, 0.05);
        }
        
        .line-number {
            display: table-cell;
            background: #2d2d30;
            color: #858585;
            padding: 2px 8px;
            min-width: 40px;
            text-align: right;
            border-right: 1px solid #464647;
            user-select: none;
            position: sticky;
            left: 0;
            z-index: 5;
        }
        
        .line-content {
            display: table-cell;
            padding: 2px 0;
            white-space: nowrap;
        }
        
        .cell-data {
            display: inline-block;
            padding: 2px 12px;
            min-width: 120px;
            border-right: 1px solid #3a3a3a;
            white-space: nowrap;
        }
        
        /* Header row styling */
        .header-row {
            background: #2d2d30 !important;
            font-weight: bold;
            position: sticky;
            top: 0;
            z-index: 6;
        }
        
        .header-row .cell-data {
            background: #2d2d30;
            color: #007ACC;
            font-weight: bold;
            border-right: 1px solid #464647;
        }
        
        /* All changes are modifications */
        .diff-modified {
            background: rgba(210, 153, 34, 0.15) !important;
        }
        
        .diff-modified .line-number {
            background: #3d3319 !important;
            color: #d29922;
        }
        
        /* Cell value highlighting */
        .cell-empty {
            color: #6a6a6a;
            font-style: italic;
            opacity: 0.6;
        }
        
        .cell-value-old {
            background: rgba(229, 83, 75, 0.2);
            color: #f85149;
            padding: 1px 4px;
            border-radius: 2px;
            text-decoration: line-through;
        }
        
        .cell-value-new {
            background: rgba(87, 171, 90, 0.2);
            color: #57ab5a;
            padding: 1px 4px;
            border-radius: 2px;
            font-weight: bold;
        }
        
        .demo-note {
            background: #2d2d30;
            border: 1px solid #007ACC;
            border-radius: 6px;
            padding: 15px;
            margin: 20px 0;
            color: #cccccc;
        }
        
        .demo-note h3 {
            color: #007ACC;
            margin-top: 0;
        }
        
        /* Change list */
        .change-list {
            background: #2d2d30;
            border-radius: 6px;
            padding: 15px;
            margin-top: 20px;
        }
        
        .change-item {
            background: #1e1e1e;
            border: 1px solid #464647;
            border-radius: 4px;
            padding: 10px;
            margin: 8px 0;
            font-family: monospace;
            font-size: 13px;
        }
        
        .change-location {
            color: #007ACC;
            font-weight: bold;
        }
        
        .change-arrow {
            color: #d29922;
            margin: 0 8px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Excel Diff Visualizer - Everything as Modifications</h1>
        <div class="subtitle">All changes shown as modifications from original state to new state</div>
        
        <div class="demo-note">
            <h3>📌 New Approach: Everything is a Modification</h3>
            <p>This visualizer treats all changes as modifications:</p>
            <ul>
                <li>📝 <strong>[empty] → Value</strong> = Cell modified from empty to having content</li>
                <li>📝 <strong>Value → [empty]</strong> = Cell modified from having content to empty</li>
                <li>📝 <strong>Value → Value</strong> = Cell content modified</li>
            </ul>
            <p>This is more accurate since Excel cells always exist - they're just empty or filled.</p>
        </div>
        
        <!-- Statistics Cards -->
        <div class="stats-container">
            <div class="stat-card">
                <div class="stat-number">47</div>
                <div class="stat-label">Total Modifications</div>
            </div>
            <div class="stat-card from-empty">
                <div class="stat-number">15</div>
                <div class="stat-label">[empty] → Value</div>
            </div>
            <div class="stat-card to-empty">
                <div class="stat-number">8</div>
                <div class="stat-label">Value → [empty]</div>
            </div>
            <div class="stat-card value-change">
                <div class="stat-number">24</div>
                <div class="stat-label">Value → Value</div>
            </div>
        </div>
        
        <!-- VS Code Style Diff View with Horizontal Scrolling -->
        <div class="diff-container">
            <div class="diff-header">
                📊 Sheet: Financial_Summary
                <span class="sync-indicator">⟷ Synchronized Scrolling (Horizontal & Vertical)</span>
            </div>
            <div class="diff-grid">
                <!-- Original Side -->
                <div class="diff-side">
                    <div class="diff-side-header">📁 Original Template</div>
                    <div class="diff-content">
                        <div class="diff-table">
                            <!-- Header Row -->
                            <div class="diff-line header-row">
                                <span class="line-number">⬜</span>
                                <span class="line-content">
                                    <span class="cell-data">Product</span>
                                    <span class="cell-data">Q1 2024</span>
                                    <span class="cell-data">Q2 2024</span>
                                    <span class="cell-data">Q3 2024</span>
                                    <span class="cell-data">Q4 2024</span>
                                    <span class="cell-data">Total</span>
                                    <span class="cell-data">YoY Growth</span>
                                    <span class="cell-data">Comments</span>
                                </span>
                            </div>
                            
                            <div class="diff-line">
                                <span class="line-number">1</span>
                                <span class="line-content">
                                    <span class="cell-data">Product</span>
                                    <span class="cell-data">Q1 2024</span>
                                    <span class="cell-data">Q2 2024</span>
                                    <span class="cell-data">Q3 2024</span>
                                    <span class="cell-data">Q4 2024</span>
                                    <span class="cell-data">Total</span>
                                    <span class="cell-data">YoY Growth</span>
                                    <span class="cell-data">Comments</span>
                                </span>
                            </div>
                            
                            <div class="diff-line diff-modified">
                                <span class="line-number">2</span>
                                <span class="line-content">
                                    <span class="cell-data">Product A</span>
                                    <span class="cell-data"><span class="cell-value-old">$10,000</span></span>
                                    <span class="cell-data">$12,000</span>
                                    <span class="cell-data">$14,000</span>
                                    <span class="cell-data"><span class="cell-value-old">$15,000</span></span>
                                    <span class="cell-data"><span class="cell-value-old">$51,000</span></span>
                                    <span class="cell-data">15%</span>
                                    <span class="cell-data">Good performance</span>
                                </span>
                            </div>
                            
                            <div class="diff-line">
                                <span class="line-number">3</span>
                                <span class="line-content">
                                    <span class="cell-data">Product B</span>
                                    <span class="cell-data">$8,000</span>
                                    <span class="cell-data">$9,500</span>
                                    <span class="cell-data">$11,000</span>
                                    <span class="cell-data">$12,500</span>
                                    <span class="cell-data">$41,000</span>
                                    <span class="cell-data">12%</span>
                                    <span class="cell-data">Stable growth</span>
                                </span>
                            </div>
                            
                            <div class="diff-line diff-modified">
                                <span class="line-number">4</span>
                                <span class="line-content">
                                    <span class="cell-data">Product C</span>
                                    <span class="cell-data"><span class="cell-value-old">$5,000</span></span>
                                    <span class="cell-data"><span class="cell-value-old">$5,500</span></span>
                                    <span class="cell-data"><span class="cell-value-old">$6,000</span></span>
                                    <span class="cell-data"><span class="cell-value-old">$6,500</span></span>
                                    <span class="cell-data"><span class="cell-value-old">$23,000</span></span>
                                    <span class="cell-data"><span class="cell-value-old">8%</span></span>
                                    <span class="cell-data"><span class="cell-value-old">Discontinued</span></span>
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Modified Side -->
                <div class="diff-side">
                    <div class="diff-side-header">📝 Client's Modified Version</div>
                    <div class="diff-content">
                        <div class="diff-table">
                            <!-- Header Row -->
                            <div class="diff-line header-row">
                                <span class="line-number">⬜</span>
                                <span class="line-content">
                                    <span class="cell-data">Product</span>
                                    <span class="cell-data">Q1 2024</span>
                                    <span class="cell-data">Q2 2024</span>
                                    <span class="cell-data">Q3 2024</span>
                                    <span class="cell-data">Q4 2024</span>
                                    <span class="cell-data">Total</span>
                                    <span class="cell-data">YoY Growth</span>
                                    <span class="cell-data">Comments</span>
                                </span>
                            </div>
                            
                            <div class="diff-line">
                                <span class="line-number">1</span>
                                <span class="line-content">
                                    <span class="cell-data">Product</span>
                                    <span class="cell-data">Q1 2024</span>
                                    <span class="cell-data">Q2 2024</span>
                                    <span class="cell-data">Q3 2024</span>
                                    <span class="cell-data">Q4 2024</span>
                                    <span class="cell-data">Total</span>
                                    <span class="cell-data">YoY Growth</span>
                                    <span class="cell-data">Comments</span>
                                </span>
                            </div>
                            
                            <div class="diff-line diff-modified">
                                <span class="line-number">2</span>
                                <span class="line-content">
                                    <span class="cell-data">Product A</span>
                                    <span class="cell-data"><span class="cell-value-new">$11,500</span></span>
                                    <span class="cell-data">$12,000</span>
                                    <span class="cell-data">$14,000</span>
                                    <span class="cell-data"><span class="cell-value-new">$16,500</span></span>
                                    <span class="cell-data"><span class="cell-value-new">$54,000</span></span>
                                    <span class="cell-data">15%</span>
                                    <span class="cell-data">Good performance</span>
                                </span>
                            </div>
                            
                            <div class="diff-line">
                                <span class="line-number">3</span>
                                <span class="line-content">
                                    <span class="cell-data">Product B</span>
                                    <span class="cell-data">$8,000</span>
                                    <span class="cell-data">$9,500</span>
                                    <span class="cell-data">$11,000</span>
                                    <span class="cell-data">$12,500</span>
                                    <span class="cell-data">$41,000</span>
                                    <span class="cell-data">12%</span>
                                    <span class="cell-data">Stable growth</span>
                                </span>
                            </div>
                            
                            <div class="diff-line diff-modified">
                                <span class="line-number">4</span>
                                <span class="line-content">
                                    <span class="cell-data">Product C</span>
                                    <span class="cell-data"><span class="cell-empty">[empty]</span></span>
                                    <span class="cell-data"><span class="cell-empty">[empty]</span></span>
                                    <span class="cell-data"><span class="cell-empty">[empty]</span></span>
                                    <span class="cell-data"><span class="cell-empty">[empty]</span></span>
                                    <span class="cell-data"><span class="cell-empty">[empty]</span></span>
                                    <span class="cell-data"><span class="cell-empty">[empty]</span></span>
                                    <span class="cell-data"><span class="cell-empty">[empty]</span></span>
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Change List View with Column Names -->
        <div class="change-list">
            <h3 style="color: #007ACC; margin-top: 0;">📝 Modification List (Using Column Headers)</h3>
            
            <div class="change-item">
                <span class="change-location">Q1 2024, Row 2</span>
                <span class="change-arrow">→</span>
                Modified from <span class="cell-value-old">$10,000</span> to <span class="cell-value-new">$11,500</span>
            </div>
            
            <div class="change-item">
                <span class="change-location">Q4 2024, Row 2</span>
                <span class="change-arrow">→</span>
                Modified from <span class="cell-value-old">$15,000</span> to <span class="cell-value-new">$16,500</span>
            </div>
            
            <div class="change-item">
                <span class="change-location">Total, Row 2</span>
                <span class="change-arrow">→</span>
                Modified from <span class="cell-value-old">$51,000</span> to <span class="cell-value-new">$54,000</span>
            </div>
            
            <div class="change-item">
                <span class="change-location">Q1 2024, Row 4</span>
                <span class="change-arrow">→</span>
                Modified from <span class="cell-value-old">$5,000</span> to <span class="cell-empty">[empty]</span>
            </div>
            
            <div class="change-item">
                <span class="change-location">Q2 2024, Row 4</span>
                <span class="change-arrow">→</span>
                Modified from <span class="cell-value-old">$5,500</span> to <span class="cell-empty">[empty]</span>
            </div>
            
            <div class="change-item">
                <span class="change-location">Comments, Row 4</span>
                <span class="change-arrow">→</span>
                Modified from <span class="cell-value-old">Discontinued</span> to <span class="cell-empty">[empty]</span>
            </div>
        </div>
        
        <div class="demo-note">
            <h3>✨ Enhanced Features</h3>
            <ul>
                <li><strong>Horizontal Scrolling:</strong> Wide spreadsheets display cleanly with no line wrapping</li>
                <li><strong>Column Header Names:</strong> Changes show "Q1 2024, Row 2" instead of "Cell B2"</li>
                <li><strong>Sticky Headers:</strong> Column headers stay visible while scrolling</li>
                <li><strong>Synchronized Scrolling:</strong> Both horizontal and vertical scrolling synced between panels</li>
                <li><strong>Clean Table Layout:</strong> Each cell has its own column, making it easy to scan changes</li>
            </ul>
            <p style="margin-top: 15px;">
                <strong>💡 Try it:</strong> In the actual application, you can scroll horizontally through 
                hundreds of columns while keeping everything aligned and readable. The column headers from 
                your Excel file are automatically detected and used throughout the interface.
            </p>
        </div>
    </div>
</body>
</html>
