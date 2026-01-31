#!/usr/bin/env python3
"""
Extract complete text from a PDF while preserving structure and reading order.

Two methods available:
1. pymupdf4llm - Fast extraction from existing text layer (native PDFs or pre-OCR'd)
2. ocrmypdf - Re-OCR with Tesseract for better quality on scanned documents

For scanned books, ocrmypdf with language-specific models produces cleaner results.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def check_pymupdf():
    """Check if pymupdf4llm is available."""
    try:
        import pymupdf4llm
        import pymupdf
        return True
    except ImportError:
        return False


def check_ocrmypdf():
    """Check if ocrmypdf is available."""
    try:
        result = subprocess.run(
            ["ocrmypdf", "--version"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def extract_with_pymupdf(pdf_path: Path, output_path: Path, as_markdown: bool = True) -> None:
    """Extract PDF text using pymupdf4llm (uses existing text layer)."""
    import pymupdf4llm
    import pymupdf

    print(f"Extracting with pymupdf4llm: {pdf_path}")
    print(f"Output: {output_path}")

    doc = pymupdf.open(pdf_path)
    total_pages = len(doc)
    doc.close()
    print(f"Total pages: {total_pages}")

    if as_markdown:
        text = pymupdf4llm.to_markdown(
            str(pdf_path),
            write_images=False,
            page_chunks=False,
        )
    else:
        doc = pymupdf.open(pdf_path)
        parts = []
        for page in doc:
            parts.append(page.get_text("text"))
        doc.close()
        text = "\n\n".join(parts)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")
    report_stats(text)


def extract_with_ocrmypdf(
    pdf_path: Path,
    output_path: Path,
    language: str = "eng"
) -> None:
    """
    Re-OCR PDF using ocrmypdf with Tesseract.

    This produces higher quality text for scanned documents by:
    - Using language-specific Tesseract models
    - Deskewing pages
    - Cleaning images before OCR

    Args:
        pdf_path: Input PDF file
        output_path: Output text file path
        language: Tesseract language code (e.g., 'fra' for French, 'eng' for English)
    """
    print(f"Re-OCRing with ocrmypdf ({language}): {pdf_path}")
    print(f"Output: {output_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Create a temporary PDF path (we only want the sidecar text)
    temp_pdf = output_path.with_suffix(".tmp.pdf")

    cmd = [
        "ocrmypdf",
        "--force-ocr",
        "-l", language,
        "--deskew",
        "--clean",
        "--sidecar", str(output_path),
        str(pdf_path),
        str(temp_pdf),
    ]

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)

    # Remove the temporary PDF (we only need the sidecar text)
    if temp_pdf.exists():
        temp_pdf.unlink()

    # Report statistics
    text = output_path.read_text(encoding="utf-8")
    report_stats(text)


def report_stats(text: str) -> None:
    """Report extraction statistics."""
    lines = text.count("\n")
    words = len(text.split())
    chars = len(text)
    print(f"Extraction complete:")
    print(f"  - Lines: {lines:,}")
    print(f"  - Words: {words:,}")
    print(f"  - Characters: {chars:,}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract text from PDF with structure preservation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract using existing OCR layer (fast)
  python extract_text.py input.pdf -o output.md

  # Re-OCR a scanned French book (better quality)
  python extract_text.py input.pdf -o output.txt --method ocrmypdf --language fra

  # Re-OCR with English
  python extract_text.py input.pdf -o output.txt --method ocrmypdf --language eng
"""
    )
    parser.add_argument("pdf", type=Path, help="Input PDF file")
    parser.add_argument("-o", "--output", type=Path, help="Output file path")
    parser.add_argument(
        "--method",
        choices=["pymupdf", "ocrmypdf"],
        default="pymupdf",
        help="Extraction method (default: pymupdf)"
    )
    parser.add_argument(
        "--language",
        default="eng",
        help="Tesseract language code for ocrmypdf (default: eng). Use 'fra' for French."
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "text"],
        default="text",
        help="Output format for pymupdf method (default: text)"
    )

    args = parser.parse_args()

    if not args.pdf.exists():
        print(f"Error: PDF not found: {args.pdf}")
        sys.exit(1)

    # Default output path
    if args.output is None:
        suffix = ".md" if args.format == "markdown" and args.method == "pymupdf" else ".txt"
        args.output = args.pdf.with_suffix(suffix)

    if args.method == "pymupdf":
        if not check_pymupdf():
            print("Error: pymupdf4llm not installed.")
            print("Install with: pip install pymupdf4llm[ocr,layout]")
            sys.exit(1)
        extract_with_pymupdf(args.pdf, args.output, as_markdown=(args.format == "markdown"))
    else:
        if not check_ocrmypdf():
            print("Error: ocrmypdf not installed.")
            print("Install with: pip install ocrmypdf")
            print("Also install tesseract language packs: brew install tesseract-lang")
            sys.exit(1)
        extract_with_ocrmypdf(args.pdf, args.output, language=args.language)


if __name__ == "__main__":
    main()
