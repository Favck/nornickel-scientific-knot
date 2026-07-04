import fitz  # PyMuPDF
import sys

def test_fitz(file_path):
    print(f"Testing {file_path}")
    try:
        doc = fitz.open(file_path)
    except Exception as e:
        print("Error opening:", e)
        return

    # test page 1 (or another page)
    if len(doc) > 0:
        page = doc[0]
        # Test table extraction
        tables = page.find_tables()
        print(f"Found {len(tables.tables)} tables.")
        
        # Test text extraction with layout
        text = page.get_text("text", sort=True)
        print("Length of text:", len(text))
        print("FFFD count in text:", text.count('\ufffd'))
        print("Sample text (first 200 chars):", repr(text[:200]))

import glob
if __name__ == "__main__":
    pdf_files = glob.glob("Information_sources/**/*.pdf", recursive=True)
    target = next((f for f in pdf_files if "1609-9192-2024-1-60-64" in f), pdf_files[0])
    test_fitz(target)
