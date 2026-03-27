"""
Master Report Generator
Processes raw data and generates reports in the selected format(s).

Usage:
    python generate_report.py              → prompts for format
    python generate_report.py docx         → Word only
    python generate_report.py pptx         → PowerPoint only
    python generate_report.py pdf          → PDF only
    python generate_report.py all          → all formats
    python generate_report.py docx pdf     → multiple formats
"""

import sys
from pathlib import Path

# Ensure src/ is in path for imports
SRC_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC_DIR))

from ProcessData import main as process_data
from generateDocx import generate_report as generate_docx
from generatePPTx import generate_presentation as generate_pptx
from generatePDF import generate_report as generate_pdf

VALID_FORMATS = {"docx", "pptx", "pdf", "all"}

GENERATORS = {
    "docx": ("Word (.docx)", generate_docx),
    "pptx": ("PowerPoint (.pptx)", generate_pptx),
    "pdf":  ("PDF (.pdf)", generate_pdf),
}


def prompt_format():
    """Ask the user which format(s) to generate."""
    print("\nAvailable formats:")
    print("  1. docx  — Word document")
    print("  2. pptx  — PowerPoint presentation")
    print("  3. pdf   — PDF report")
    print("  4. all   — Generate all formats")
    print()

    choice = input("Select format(s) (e.g. 'docx', 'pdf', 'all', or 'docx pdf'): ").strip().lower()

    if not choice:
        print("No format selected. Exiting.")
        sys.exit(0)

    return choice.split()


def run(formats):
    """Process data and generate selected formats."""

    # Validate
    for fmt in formats:
        if fmt not in VALID_FORMATS:
            print(f"Error: '{fmt}' is not a valid format. Use: {', '.join(sorted(VALID_FORMATS))}")
            sys.exit(1)

    # Expand 'all'
    if "all" in formats:
        formats = ["docx", "pptx", "pdf"]

    # Remove duplicates, preserve order
    seen = set()
    formats = [f for f in formats if f not in seen and not seen.add(f)]

    # Step 1: Process data
    print("=" * 50)
    print("STEP 1: Processing raw data")
    print("=" * 50)
    process_data()

    # Step 2: Generate reports
    for fmt in formats:
        label, generator = GENERATORS[fmt]
        print()
        print("=" * 50)
        print(f"STEP 2: Generating {label}")
        print("=" * 50)
        generator()

    # Summary
    print()
    print("=" * 50)
    print("DONE")
    print("=" * 50)
    print(f"Generated: {', '.join(formats)}")
    print(f"Output directory: outputs/")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        formats = [arg.lower() for arg in sys.argv[1:]]
    else:
        formats = prompt_format()

    run(formats)