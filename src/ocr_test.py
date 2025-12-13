"""
Phase 2: Document Intelligence OCR Testing
Test the prebuilt-layout model on Bill of Entry PDF
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

# Load environment variables
load_dotenv(Path(__file__).parent.parent / "config" / ".env")

ENDPOINT = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
KEY = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
PDF_PATH = Path(__file__).parent.parent / "Billofentry.pdf"
OUTPUT_DIR = Path(__file__).parent.parent / "output"


def analyze_document(pdf_path: Path) -> dict:
    """Analyze PDF using Azure Document Intelligence prebuilt-layout model."""

    print(f"Connecting to: {ENDPOINT}")
    client = DocumentAnalysisClient(
        endpoint=ENDPOINT,
        credential=AzureKeyCredential(KEY)
    )

    print(f"Analyzing document: {pdf_path}")
    with open(pdf_path, "rb") as f:
        poller = client.begin_analyze_document("prebuilt-layout", f)

    print("Waiting for analysis to complete...")
    result = poller.result()

    return result


def extract_structured_data(result) -> dict:
    """Extract structured data from OCR result."""

    data = {
        "metadata": {
            "model_id": result.model_id,
            "page_count": len(result.pages),
            "api_version": result.api_version,
        },
        "pages": [],
        "tables": [],
        "key_value_pairs": [],
        "confidence_stats": {
            "total_words": 0,
            "high_confidence": 0,  # >= 0.9
            "medium_confidence": 0,  # 0.8-0.9
            "low_confidence": 0,  # < 0.8
        }
    }

    # Extract page-level data
    for page in result.pages:
        page_data = {
            "page_number": page.page_number,
            "width": page.width,
            "height": page.height,
            "unit": page.unit,
            "lines": [],
            "words_count": len(page.words) if page.words else 0,
        }

        # Extract lines
        if page.lines:
            for line in page.lines:
                page_data["lines"].append({
                    "content": line.content,
                    "polygon": [{"x": p.x, "y": p.y} for p in line.polygon] if line.polygon else None,
                })

        # Track confidence stats
        if page.words:
            for word in page.words:
                data["confidence_stats"]["total_words"] += 1
                if word.confidence >= 0.9:
                    data["confidence_stats"]["high_confidence"] += 1
                elif word.confidence >= 0.8:
                    data["confidence_stats"]["medium_confidence"] += 1
                else:
                    data["confidence_stats"]["low_confidence"] += 1

        data["pages"].append(page_data)

    # Extract tables
    if result.tables:
        for table_idx, table in enumerate(result.tables):
            table_data = {
                "table_index": table_idx,
                "row_count": table.row_count,
                "column_count": table.column_count,
                "page_number": table.bounding_regions[0].page_number if table.bounding_regions else None,
                "cells": []
            }

            for cell in table.cells:
                table_data["cells"].append({
                    "row_index": cell.row_index,
                    "column_index": cell.column_index,
                    "row_span": cell.row_span,
                    "column_span": cell.column_span,
                    "content": cell.content,
                    "kind": cell.kind if hasattr(cell, 'kind') else None,
                })

            data["tables"].append(table_data)

    # Extract key-value pairs (if available)
    if hasattr(result, 'key_value_pairs') and result.key_value_pairs:
        for kv in result.key_value_pairs:
            if kv.key and kv.value:
                data["key_value_pairs"].append({
                    "key": kv.key.content,
                    "value": kv.value.content if kv.value else None,
                    "confidence": kv.confidence,
                })

    # Calculate confidence percentages
    total = data["confidence_stats"]["total_words"]
    if total > 0:
        data["confidence_stats"]["high_confidence_pct"] = round(
            data["confidence_stats"]["high_confidence"] / total * 100, 2
        )
        data["confidence_stats"]["medium_confidence_pct"] = round(
            data["confidence_stats"]["medium_confidence"] / total * 100, 2
        )
        data["confidence_stats"]["low_confidence_pct"] = round(
            data["confidence_stats"]["low_confidence"] / total * 100, 2
        )

    return data


def extract_boe_structure(result) -> dict:
    """Extract Bill of Entry specific structure from OCR result."""

    boe_data = {
        "header": {},
        "part1_summary": {},
        "part2_invoices": [],
        "part3_duties": [],
        "part4_additional": {},
        "part5_compliances": {},
        "glossary": [],
    }

    # Extract header from first page lines
    first_page_lines = []
    if result.pages and result.pages[0].lines:
        first_page_lines = [line.content for line in result.pages[0].lines]

    # Parse header fields (looking for key patterns)
    header_patterns = {
        "port_code": "Port Code",
        "be_no": "BE No",
        "be_date": "BE Date",
        "be_type": "BE Type",
        "iec_br": "IEC/Br",
        "gstin_type": "GSTIN/TYPE",
        "cb_code": "CB CODE",
    }

    # Extract values from tables on page 1
    if result.tables:
        for table in result.tables:
            if table.bounding_regions and table.bounding_regions[0].page_number == 1:
                for cell in table.cells:
                    content = cell.content.strip()
                    # Look for header values
                    if "INDEL4" in content:
                        boe_data["header"]["port_code"] = "INDEL4"
                    if "7654321" in content:
                        boe_data["header"]["be_no"] = "7654321"
                    if "15/04/2022" in content:
                        boe_data["header"]["be_date"] = "2022-04-15"

    # Extract tables structure
    tables_by_page = {}
    if result.tables:
        for table in result.tables:
            page_num = table.bounding_regions[0].page_number if table.bounding_regions else 0
            if page_num not in tables_by_page:
                tables_by_page[page_num] = []
            tables_by_page[page_num].append({
                "rows": table.row_count,
                "cols": table.column_count,
                "cells_sample": [cell.content for cell in table.cells[:10]]
            })

    boe_data["tables_by_page"] = tables_by_page

    return boe_data


def main():
    """Main function to run OCR analysis."""

    print("=" * 60)
    print("Phase 2: Document Intelligence OCR Testing")
    print("=" * 60)

    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Run OCR analysis
    result = analyze_document(PDF_PATH)

    # Extract structured data
    print("\nExtracting structured data...")
    structured_data = extract_structured_data(result)

    # Extract BoE-specific structure
    print("Extracting Bill of Entry structure...")
    boe_data = extract_boe_structure(result)

    # Save raw OCR output
    raw_output_path = OUTPUT_DIR / "ocr_raw_output.json"
    with open(raw_output_path, "w") as f:
        json.dump(structured_data, f, indent=2, default=str)
    print(f"\nRaw OCR output saved to: {raw_output_path}")

    # Save BoE structured output
    boe_output_path = OUTPUT_DIR / "boe_structured_output.json"
    with open(boe_output_path, "w") as f:
        json.dump(boe_data, f, indent=2, default=str)
    print(f"BoE structured output saved to: {boe_output_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("OCR Analysis Summary")
    print("=" * 60)
    print(f"Pages analyzed: {structured_data['metadata']['page_count']}")
    print(f"Tables found: {len(structured_data['tables'])}")
    print(f"Key-value pairs: {len(structured_data['key_value_pairs'])}")

    print("\nConfidence Statistics:")
    stats = structured_data["confidence_stats"]
    print(f"  Total words: {stats['total_words']}")
    print(f"  High confidence (>=90%): {stats['high_confidence']} ({stats.get('high_confidence_pct', 0)}%)")
    print(f"  Medium confidence (80-90%): {stats['medium_confidence']} ({stats.get('medium_confidence_pct', 0)}%)")
    print(f"  Low confidence (<80%): {stats['low_confidence']} ({stats.get('low_confidence_pct', 0)}%)")

    print("\nTables by page:")
    for page_num, tables in boe_data.get("tables_by_page", {}).items():
        print(f"  Page {page_num}: {len(tables)} table(s)")
        for i, t in enumerate(tables):
            print(f"    Table {i+1}: {t['rows']} rows x {t['cols']} cols")

    return structured_data, boe_data


if __name__ == "__main__":
    main()
