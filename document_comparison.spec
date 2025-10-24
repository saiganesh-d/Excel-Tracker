# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller specification file for Document Comparison Suite
This creates a standalone executable for Windows
"""

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all Streamlit files
streamlit_datas = collect_data_files('streamlit')
streamlit_hiddenimports = collect_submodules('streamlit')

# Collect altair (used by Streamlit)
altair_datas = collect_data_files('altair')

# Collect pdfplumber dependencies
pdfplumber_datas = collect_data_files('pdfplumber')

# All data files to include
datas = []
datas += streamlit_datas
datas += altair_datas
datas += pdfplumber_datas

# Add application files
datas += [
    ('app.py', '.'),
    ('main.py', '.'),
    ('pdf_compare.py', '.'),
    ('pdf_compare_ui.py', '.'),
    ('pdf_compare_optimized.py', '.'),
    ('pdf_compare_ui_optimized.py', '.'),
    ('smart_diff.py', '.'),
]

# Hidden imports (modules that PyInstaller might miss)
hiddenimports = []
hiddenimports += streamlit_hiddenimports
hiddenimports += [
    'streamlit.web.cli',
    'streamlit.runtime.scriptrunner.magic_funcs',
    'streamlit.hello',
    'pdfplumber',
    'pdfplumber.utils',
    'PIL._tkinter_finder',
    'pandas',
    'openpyxl',
    'openpyxl.styles',
    'openpyxl.utils',
    'openpyxl.comments',
    'numpy',
    'altair',
    'click',
    'validators',
]

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pytest',
        'IPython',
        'jupyter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DocumentComparison',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Keep console open to see Streamlit output
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add .ico file path here if you have a custom icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DocumentComparison',
)
