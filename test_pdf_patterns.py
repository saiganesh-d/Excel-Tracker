"""
Test script for PDFs with pattern fills and complex graphics
This verifies the fix for pdfplumber pattern errors
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pdf_compare import PDFStructureExtractor

def test_pdf_extraction(pdf_path):
    """Test PDF extraction with pattern fill handling"""
    print("=" * 60)
    print("Testing PDF Extraction with Pattern Fill Handling")
    print("=" * 60)
    print()

    if not os.path.exists(pdf_path):
        print(f"ERROR: File not found: {pdf_path}")
        print()
        print("Please provide a valid PDF file path.")
        return False

    print(f"PDF File: {pdf_path}")
    print()

    try:
        print("Extracting structure...")
        extractor = PDFStructureExtractor()
        sections = extractor.extract_from_pdf(pdf_path)

        print(f"✓ Extraction successful!")
        print()
        print(f"Results:")
        print(f"  - Total sections found: {len(sections)}")
        print()

        if sections:
            print("First 5 sections:")
            print("-" * 60)
            for i, section in enumerate(sections[:5], 1):
                print(f"{i}. Level {section.level}: {section.title}")
                print(f"   Page {section.page_number}")
                content_preview = section.content[:100] if section.content else "[empty]"
                print(f"   Content: {content_preview}...")
                print()

            if len(sections) > 5:
                print(f"... and {len(sections) - 5} more sections")
        else:
            print("No sections found. This might be:")
            print("  - A PDF without clear headings")
            print("  - A scanned/image-based PDF")
            print("  - A PDF with unusual formatting")

        print()
        print("=" * 60)
        print("✓ TEST PASSED - No pattern errors!")
        print("=" * 60)
        return True

    except Exception as e:
        print()
        print("=" * 60)
        print("✗ TEST FAILED")
        print("=" * 60)
        print(f"Error: {str(e)}")
        print()
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print()

    if len(sys.argv) > 1:
        # PDF path provided as command line argument
        pdf_path = sys.argv[1]
        test_pdf_extraction(pdf_path)
    else:
        # Interactive mode
        print("PDF Pattern Fill Test")
        print()
        print("This tests PDF extraction with documents that have:")
        print("  - Pattern fills (highlighted text)")
        print("  - Complex backgrounds")
        print("  - Graphics overlays")
        print()

        pdf_path = input("Enter PDF file path (or drag and drop): ").strip('"').strip("'")

        if pdf_path:
            print()
            test_pdf_extraction(pdf_path)
        else:
            print("No file provided. Exiting.")

    print()
    input("Press Enter to exit...")
