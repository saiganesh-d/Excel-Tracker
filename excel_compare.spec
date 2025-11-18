# PyInstaller spec file for Excel Comparison EXE
# This creates a standalone executable with all dependencies

# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import copy_metadata

block_cipher = None

a = Analysis(
    ['excel_launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include main.py as a data file
        ('main.py', '.'),
        # Include Streamlit's static files and metadata
        ('venv/Lib/site-packages/streamlit/static', 'streamlit/static'),
        ('venv/Lib/site-packages/streamlit/runtime', 'streamlit/runtime'),
    ] + copy_metadata('streamlit') + copy_metadata('altair') + copy_metadata('pandas'),
    hiddenimports=[
        'streamlit',
        'streamlit.web.cli',
        'streamlit.runtime.scriptrunner.magic_funcs',
        'pandas',
        'openpyxl',
        'numpy',
        'altair',
        'pyarrow',
        'click',
        'toml',
        'validators',
        'watchdog',
        'tornado',
        'PIL',
        'packaging',
        'packaging.version',
        'packaging.specifiers',
        'packaging.requirements',
        'importlib_metadata',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude PDF/ML libraries to keep size small
        'torch',
        'torchvision',
        'transformers',
        'sentence_transformers',
        'scipy',
        'scikit-learn',
        'pdfplumber',
        'pypdf2',
        'llama_cpp',
        'langdetect',
        # Exclude PDF comparison modules
        'pdf_compare_ui',
        'pdf_compare_ui_optimized',
        'pdf_compare_ui_advanced',
        'advanced_pdf_comparator',
        'paragraph_extractor',
        'language_detector',
        'translation_service',
        'semantic_embedder',
        'semantic_comparator',
        'requirement_analyzer',
        'local_llm',
        'model_manager',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ExcelCompare',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress with UPX
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Keep console for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path if you have one
)
