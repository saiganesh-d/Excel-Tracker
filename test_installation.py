"""
Installation verification script
Tests that all dependencies are properly installed
"""

import sys

def test_imports():
    """Test that all required packages can be imported"""
    print("=" * 60)
    print("Testing Document Comparison Suite Installation")
    print("=" * 60)
    print()

    required_packages = [
        ('streamlit', 'Streamlit web framework'),
        ('pandas', 'Data manipulation library'),
        ('openpyxl', 'Excel file handling'),
        ('numpy', 'Numerical operations'),
        ('pdfplumber', 'PDF text extraction'),
    ]

    all_success = True

    for package, description in required_packages:
        try:
            __import__(package)
            print(f"✓ {package:20s} - {description}")
        except ImportError as e:
            print(f"✗ {package:20s} - FAILED: {str(e)}")
            all_success = False

    print()
    print("=" * 60)

    if all_success:
        print("✓ ALL PACKAGES INSTALLED SUCCESSFULLY!")
        print()
        print("You can now run the application:")
        print("  streamlit run app.py")
        print()
        return True
    else:
        print("✗ SOME PACKAGES ARE MISSING")
        print()
        print("Please run:")
        print("  pip install -r requirements.txt")
        print()
        return False


def test_modules():
    """Test that custom modules can be imported"""
    print("Testing custom modules...")
    print()

    try:
        from pdf_compare import PDFStructureExtractor, PDFStructureComparator
        print("✓ pdf_compare module loaded successfully")
    except Exception as e:
        print(f"✗ pdf_compare module failed: {str(e)}")
        return False

    try:
        import pdf_compare_ui
        print("✓ pdf_compare_ui module loaded successfully")
    except Exception as e:
        print(f"✗ pdf_compare_ui module failed: {str(e)}")
        return False

    try:
        import main
        print("✓ main (Excel comparison) module loaded successfully")
    except Exception as e:
        print(f"✗ main module failed: {str(e)}")
        return False

    try:
        import app
        print("✓ app (unified launcher) module loaded successfully")
    except Exception as e:
        print(f"✗ app module failed: {str(e)}")
        return False

    print()
    return True


def test_versions():
    """Display versions of key packages"""
    print("=" * 60)
    print("Package Versions")
    print("=" * 60)
    print()

    try:
        import streamlit
        print(f"Streamlit: {streamlit.__version__}")
    except:
        print("Streamlit: NOT INSTALLED")

    try:
        import pandas
        print(f"Pandas: {pandas.__version__}")
    except:
        print("Pandas: NOT INSTALLED")

    try:
        import openpyxl
        print(f"Openpyxl: {openpyxl.__version__}")
    except:
        print("Openpyxl: NOT INSTALLED")

    try:
        import numpy
        print(f"NumPy: {numpy.__version__}")
    except:
        print("NumPy: NOT INSTALLED")

    try:
        import pdfplumber
        print(f"PDFPlumber: {pdfplumber.__version__}")
    except:
        print("PDFPlumber: NOT INSTALLED")

    print()
    print(f"Python: {sys.version}")
    print()


def main():
    """Run all tests"""
    print()

    # Test package imports
    packages_ok = test_imports()

    if not packages_ok:
        return

    # Test versions
    test_versions()

    # Test custom modules
    print("=" * 60)
    modules_ok = test_modules()
    print("=" * 60)
    print()

    if modules_ok:
        print("🎉 INSTALLATION VERIFIED SUCCESSFULLY! 🎉")
        print()
        print("Next steps:")
        print("  1. Run: streamlit run app.py")
        print("  2. Open browser to: http://localhost:8501")
        print("  3. Choose Excel or PDF comparison tool")
        print("  4. Upload your documents and start comparing!")
        print()
    else:
        print("⚠️  Some modules failed to load.")
        print("Please check the error messages above.")
        print()


if __name__ == "__main__":
    main()
