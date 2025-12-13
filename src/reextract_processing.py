"""
Re-extract Processing Details from existing OCR output.
This script uses the existing ocr_full_output.json to re-extract
the boe_extracted_data.json with Processing Details included.
"""

import json
from pathlib import Path

# Import the extraction functions from ocr_full_document
from ocr_full_document import extract_boe_fields

OUTPUT_DIR = Path(__file__).parent.parent / "output"


def main():
    print("=" * 60)
    print("Re-extracting Processing Details from OCR Output")
    print("=" * 60)

    # Load existing OCR full output
    ocr_path = OUTPUT_DIR / "ocr_full_output.json"
    print(f"\nLoading OCR data from: {ocr_path}")

    with open(ocr_path) as f:
        merged_data = json.load(f)

    print(f"  Pages: {len(merged_data.get('pages', []))}")
    print(f"  Tables: {len(merged_data.get('tables', []))}")

    # Re-extract BOE fields with Processing Details
    print("\nExtracting BOE fields with Processing Details...")
    boe_data = extract_boe_fields(merged_data)

    # Show processing details found
    print(f"\nProcessing Details found: {len(boe_data['part1_processing'])}")
    for proc in boe_data['part1_processing']:
        print(f"  - {proc['event']}: {proc['event_date']} {proc['event_time']} | {proc['exchange_rate']}")

    # Save updated extracted data
    boe_output_path = OUTPUT_DIR / "boe_extracted_data.json"
    with open(boe_output_path, "w") as f:
        json.dump(boe_data, f, indent=2, default=str)
    print(f"\nSaved updated BOE data to: {boe_output_path}")

    return boe_data


if __name__ == "__main__":
    main()
