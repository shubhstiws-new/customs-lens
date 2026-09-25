"""
Phase 2: Full Document OCR Analysis
Processes all 17 pages of the Bill of Entry PDF
Handles F0 tier 2-page limit by splitting PDF
"""

import os
import sys
import json
import fitz  # PyMuPDF
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

# Load environment variables
load_dotenv(Path(__file__).parent.parent / "config" / ".env")

ENDPOINT = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
KEY = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
PDF_PATH = Path(__file__).parent.parent / "Billofentry.pdf"
OUTPUT_DIR = Path(__file__).parent.parent / "output"
TEMP_DIR = OUTPUT_DIR / "temp_pages"


def split_pdf_into_chunks(pdf_path: Path, pages_per_chunk: int = 2) -> list[Path]:
    """Split PDF into chunks of N pages each."""

    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    print(f"Total pages in PDF: {total_pages}")

    chunk_paths = []
    for start in range(0, total_pages, pages_per_chunk):
        end = min(start + pages_per_chunk, total_pages)
        chunk_doc = fitz.open()

        for page_num in range(start, end):
            chunk_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

        chunk_path = TEMP_DIR / f"chunk_{start+1:02d}_to_{end:02d}.pdf"
        chunk_doc.save(chunk_path)
        chunk_doc.close()
        chunk_paths.append((chunk_path, start + 1, end))
        print(f"  Created chunk: pages {start+1}-{end}")

    doc.close()
    return chunk_paths


def analyze_chunk(client: DocumentAnalysisClient, pdf_path: Path, start_page: int) -> dict:
    """Analyze a PDF chunk and return structured results."""

    with open(pdf_path, "rb") as f:
        poller = client.begin_analyze_document("prebuilt-layout", f)

    result = poller.result()

    chunk_data = {
        "pages": [],
        "tables": [],
        "confidence_stats": {
            "total_words": 0,
            "high_confidence": 0,
            "medium_confidence": 0,
            "low_confidence": 0,
        }
    }

    # Extract page data
    for page in result.pages:
        # Adjust page number to original document
        original_page_num = start_page + page.page_number - 1

        page_data = {
            "page_number": original_page_num,
            "width": page.width,
            "height": page.height,
            "unit": page.unit,
            "lines": [],
        }

        if page.lines:
            for line in page.lines:
                page_data["lines"].append({
                    "content": line.content,
                    "polygon": [{"x": p.x, "y": p.y} for p in line.polygon] if line.polygon else None,
                })

        # Track confidence
        if page.words:
            for word in page.words:
                chunk_data["confidence_stats"]["total_words"] += 1
                if word.confidence >= 0.9:
                    chunk_data["confidence_stats"]["high_confidence"] += 1
                elif word.confidence >= 0.8:
                    chunk_data["confidence_stats"]["medium_confidence"] += 1
                else:
                    chunk_data["confidence_stats"]["low_confidence"] += 1

        chunk_data["pages"].append(page_data)

    # Extract tables
    if result.tables:
        for table in result.tables:
            original_page = start_page + (table.bounding_regions[0].page_number - 1) if table.bounding_regions else start_page

            table_data = {
                "page_number": original_page,
                "row_count": table.row_count,
                "column_count": table.column_count,
                "cells": []
            }

            for cell in table.cells:
                table_data["cells"].append({
                    "row_index": cell.row_index,
                    "column_index": cell.column_index,
                    "row_span": cell.row_span,
                    "column_span": cell.column_span,
                    "content": cell.content,
                })

            chunk_data["tables"].append(table_data)

    return chunk_data


def merge_chunk_results(all_chunks: list[dict]) -> dict:
    """Merge results from all chunks into a single document."""

    merged = {
        "metadata": {
            "model_id": "prebuilt-layout",
            "total_pages": 0,
            "total_tables": 0,
        },
        "pages": [],
        "tables": [],
        "confidence_stats": {
            "total_words": 0,
            "high_confidence": 0,
            "medium_confidence": 0,
            "low_confidence": 0,
        }
    }

    for chunk in all_chunks:
        merged["pages"].extend(chunk["pages"])
        merged["tables"].extend(chunk["tables"])

        for key in merged["confidence_stats"]:
            merged["confidence_stats"][key] += chunk["confidence_stats"][key]

    merged["metadata"]["total_pages"] = len(merged["pages"])
    merged["metadata"]["total_tables"] = len(merged["tables"])

    # Calculate percentages
    total = merged["confidence_stats"]["total_words"]
    if total > 0:
        merged["confidence_stats"]["high_confidence_pct"] = round(
            merged["confidence_stats"]["high_confidence"] / total * 100, 2
        )
        merged["confidence_stats"]["medium_confidence_pct"] = round(
            merged["confidence_stats"]["medium_confidence"] / total * 100, 2
        )
        merged["confidence_stats"]["low_confidence_pct"] = round(
            merged["confidence_stats"]["low_confidence"] / total * 100, 2
        )

    return merged


def extract_processing_details_from_lines(page_lines: list) -> list:
    """Extract H. PROCESSING DETAILS section from page 1 lines using y-coordinates.

    This section contains events like Submission, Assessment, OOC with
    their dates, times, and exchange rates. Items on the same visual row
    have similar y-coordinates.
    """
    import re

    processing_events = []

    # Date pattern: DD-MMM-YY or DD-MM-YYYY
    date_pattern = re.compile(r'\d{2}-[A-Z]{3}-\d{2}|\d{2}-\d{2}-\d{4}')
    # Time pattern: HH:MM
    time_pattern = re.compile(r'^\d{2}:\d{2}$')
    # Exchange rate pattern: X CUR=Y.ZINR or similar
    exchange_pattern = re.compile(r'\d+\s*[A-Z]{3}\s*=\s*[\d.]+\s*INR|INR\s*=\s*INR')

    # Event names to look for
    event_names = ["Submission", "Assessment", "OOC"]

    # Get y-coordinate from polygon (use first point's y)
    def get_y_coord(line_data):
        if isinstance(line_data, dict):
            polygon = line_data.get("polygon", [])
            if polygon and len(polygon) > 0:
                return polygon[0].get("y", 0)
        return 0

    # Find events and their y-coordinates (exact match, case-insensitive)
    event_positions = {}
    for line in page_lines:
        if isinstance(line, dict):
            content = line.get("content", "").strip()
            content_lower = content.lower()
            y_coord = get_y_coord(line)

            for event_name in event_names:
                # Match exact event name (not part of larger text like "OOC COPY")
                if content_lower == event_name.lower() and event_name not in event_positions:
                    event_positions[event_name] = y_coord

    # For each event, find related data on the same row (similar y-coordinate)
    y_tolerance = 0.12  # Tighter tolerance - rows are about 0.13 apart

    for event_name, event_y in event_positions.items():
        event_data = {
            "event": event_name,
            "event_date": "",
            "event_time": "",
            "exchange_rate": "",
        }

        # Find all items on the same row (similar y-coordinate)
        for line in page_lines:
            if isinstance(line, dict):
                content = line.get("content", "")
                line_y = get_y_coord(line)

                # Check if on the same row
                if abs(line_y - event_y) <= y_tolerance:
                    # Look for date
                    date_match = date_pattern.search(content)
                    if date_match and not event_data["event_date"]:
                        event_data["event_date"] = date_match.group()

                    # Look for time (exact match to avoid matching other numbers)
                    time_match = time_pattern.match(content.strip())
                    if time_match and not event_data["event_time"]:
                        event_data["event_time"] = time_match.group()

                    # Look for exchange rate
                    exchange_match = exchange_pattern.search(content)
                    if exchange_match and not event_data["exchange_rate"]:
                        event_data["exchange_rate"] = exchange_match.group()

        if event_data["event_date"] or event_data["event_time"]:
            processing_events.append(event_data)

    return processing_events


def extract_boe_fields(merged_data: dict) -> dict:
    """Extract Bill of Entry specific fields from OCR data."""

    boe = {
        "document_id": None,
        "header": {
            "port_code": None,
            "port_name": None,
            "be_no": None,
            "be_date": None,
            "be_type": None,
            "iec_br": None,
            "gstin_type": None,
            "cb_code": None,
            "inv_count": None,
            "item_count": None,
            "cont_count": None,
            "pkg_count": None,
            "gross_weight_kgs": None,
        },
        "part1_status": {},
        "part1_declarant": {},
        "part1_duty_summary": {},
        "part1_manifest": {},
        "part1_bond": {},
        "part1_payment": {},
        "part1_processing": [],
        "part2_invoices": [],
        "part2_items": [],
        "part3_item_duties": [],
        "part4_licence_details": [],
        "part4_sw_declarations": [],
        "part5_compliances": {},
        "tables_raw": [],
    }

    # Extract header from first page
    if merged_data["pages"]:
        first_page_lines = [l["content"] for l in merged_data["pages"][0].get("lines", [])]
        all_text = " ".join(first_page_lines)

        # Parse known values from the document
        import re

        # Port Code
        if "INDEL4" in all_text:
            boe["header"]["port_code"] = "INDEL4"

        # BE No - look for 7-digit number near "BE No"
        be_match = re.search(r'(\d{7})', all_text)
        if be_match:
            boe["header"]["be_no"] = be_match.group(1)

        # BE Date
        date_match = re.search(r'(\d{2}/\d{2}/\d{4})', all_text)
        if date_match:
            boe["header"]["be_date"] = date_match.group(1)

        # IEC/Br
        iec_match = re.search(r'(\d{10}/\d+)', all_text)
        if iec_match:
            boe["header"]["iec_br"] = iec_match.group(1)

        # GSTIN
        gstin_match = re.search(r'(\d{2}[A-Z]{5}\d{4}[A-Z]\d[A-Z\d]{2})', all_text)
        if gstin_match:
            boe["header"]["gstin_type"] = gstin_match.group(1)

        # Port Name
        port_match = re.search(r'PORT\s*:\s*(.+?)(?:BILL|$)', all_text)
        if port_match:
            boe["header"]["port_name"] = port_match.group(1).strip()

        # Extract Processing Details (Section H) from first page lines
        # Pass full line data with polygon coordinates for y-coordinate matching
        first_page_lines = merged_data["pages"][0].get("lines", [])
        boe["part1_processing"] = extract_processing_details_from_lines(first_page_lines)

    # Process tables by page to extract structured data
    for table in merged_data["tables"]:
        page_num = table.get("page_number", 0)

        # Convert table to 2D array
        rows = table["row_count"]
        cols = table["column_count"]
        grid = [[None for _ in range(cols)] for _ in range(rows)]

        for cell in table["cells"]:
            r, c = cell["row_index"], cell["column_index"]
            if r < rows and c < cols:
                grid[r][c] = cell["content"]

        table_info = {
            "page": page_num,
            "rows": rows,
            "cols": cols,
            "data": grid,
            "headers": grid[0] if grid else [],
        }
        boe["tables_raw"].append(table_info)

        # Parse specific sections based on page number and table structure
        if page_num == 1:
            # Look for duty summary (has BCD, ACD, SWS columns)
            headers_text = " ".join([str(h) for h in grid[0] if h])
            if "BCD" in headers_text or "IGST" in headers_text:
                boe["part1_duty_summary"]["raw_table"] = grid

            # Look for manifest details (IGM NO, MAWB NO)
            if "IGM" in headers_text or "MAWB" in headers_text:
                boe["part1_manifest"]["raw_table"] = grid

        # Part II - Invoice items (pages 2-3, has CTH column)
        if page_num in [2, 3]:
            if any("CTH" in str(h) for h in grid[0] if h):
                for row in grid[1:]:  # Skip header
                    if row[0] and str(row[0]).isdigit():
                        boe["part2_items"].append({
                            "sno": row[0],
                            "cth": row[1] if len(row) > 1 else None,
                            "description": row[2] if len(row) > 2 else None,
                            "unit_price": row[3] if len(row) > 3 else None,
                            "quantity": row[4] if len(row) > 4 else None,
                            "uqc": row[5] if len(row) > 5 else None,
                            "amount": row[6] if len(row) > 6 else None,
                        })

        # Part III - Duties (pages 4-13)
        if 4 <= page_num <= 13:
            # These pages have item duty details
            if rows > 2 and cols > 5:
                for row in grid[1:]:
                    if row[0] and row[1]:
                        boe["part3_item_duties"].append({
                            "page": page_num,
                            "inv_sno": row[0],
                            "item_sno": row[1] if len(row) > 1 else None,
                            "raw_row": row,
                        })

    # Generate document ID from BE number
    if boe["header"]["be_no"]:
        boe["document_id"] = f"BE{boe['header']['be_no']}"

    return boe


def main(pdf_path: Path = PDF_PATH):
    """Main function to process full document."""

    print("=" * 60)
    print("Phase 2: Full Document OCR Analysis")
    print("=" * 60)

    OUTPUT_DIR.mkdir(exist_ok=True)

    # Split PDF into chunks (2 pages each for F0 tier)
    print("\nStep 1: Splitting PDF into 2-page chunks...")
    chunks = split_pdf_into_chunks(pdf_path, pages_per_chunk=2)

    # Initialize client
    print("\nStep 2: Connecting to Azure Document Intelligence...")
    client = DocumentAnalysisClient(
        endpoint=ENDPOINT,
        credential=AzureKeyCredential(KEY)
    )

    # Process each chunk
    print("\nStep 3: Processing chunks...")
    all_results = []
    for chunk_path, start_page, end_page in chunks:
        print(f"  Analyzing pages {start_page}-{end_page}...")
        try:
            chunk_result = analyze_chunk(client, chunk_path, start_page)
            all_results.append(chunk_result)
        except Exception as e:
            print(f"    Error: {e}")

    # Merge results
    print("\nStep 4: Merging results...")
    merged = merge_chunk_results(all_results)

    # Extract BoE fields
    print("Step 5: Extracting Bill of Entry fields...")
    boe_data = extract_boe_fields(merged)

    # Save outputs
    print("\nStep 6: Saving outputs...")

    # Save full OCR output
    ocr_output_path = OUTPUT_DIR / "ocr_full_output.json"
    with open(ocr_output_path, "w") as f:
        json.dump(merged, f, indent=2, default=str)
    print(f"  Full OCR output: {ocr_output_path}")

    # Save BoE structured output
    boe_output_path = OUTPUT_DIR / "boe_extracted_data.json"
    with open(boe_output_path, "w") as f:
        json.dump(boe_data, f, indent=2, default=str)
    print(f"  BoE extracted data: {boe_output_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("OCR Analysis Complete")
    print("=" * 60)
    print(f"Pages processed: {merged['metadata']['total_pages']}")
    print(f"Tables extracted: {merged['metadata']['total_tables']}")

    stats = merged["confidence_stats"]
    print(f"\nConfidence Statistics:")
    print(f"  Total words: {stats['total_words']}")
    print(f"  High confidence (>=90%): {stats['high_confidence']} ({stats.get('high_confidence_pct', 0)}%)")
    print(f"  Medium confidence (80-90%): {stats['medium_confidence']} ({stats.get('medium_confidence_pct', 0)}%)")
    print(f"  Low confidence (<80%): {stats['low_confidence']} ({stats.get('low_confidence_pct', 0)}%)")

    print(f"\nExtracted BoE Header:")
    for key, value in boe_data["header"].items():
        if value:
            print(f"  {key}: {value}")

    print(f"\nPart II Items extracted: {len(boe_data['part2_items'])}")
    print(f"Part III Duties extracted: {len(boe_data['part3_item_duties'])}")
    print(f"Raw tables preserved: {len(boe_data['tables_raw'])}")

    # Cleanup temp files
    import shutil
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)
        print(f"\nTemp files cleaned up.")

    return merged, boe_data


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else PDF_PATH)
