# CustomsLens

**Structured data extraction from Indian Customs Bills of Entry using Azure Document Intelligence.**

A Bill of Entry (BoE) is the declaration an importer files with Indian Customs. It is a dense, multi-page form with header fields, duty summaries, invoices, line items, per-item duty breakdowns and licence debits. Importers and customs brokers typically re-key this information into their own systems by hand. CustomsLens converts the PDF into a validated relational record and gives a reviewer an interface to confirm or correct it.

---

## Pipeline

```
BoE PDF
  │  ocr_full_document.py   split into 2-page chunks → Azure Document Intelligence (prebuilt-layout)
  ▼
OCR JSON: text lines, tables, confidence scores
  │  boe_parser.py          section-aware parsing into typed records (Parts I–VI)
  ▼
Structured BoE JSON
  │  pipeline/              normalise dates, amounts, GSTIN and IEC → SQLAlchemy
  ▼
SQLite (local) / Azure SQL (hosted)
  │  app/streamlit_app.py   section-by-section review
  ▼
Reviewed record
```

| Stage | Detail |
|---|---|
| OCR | Azure Document Intelligence `prebuilt-layout` model. The free tier processes two pages per request, so the PDF is split with PyMuPDF and the per-chunk results are merged with corrected page numbers. |
| Parsing | About 35 typed record classes that mirror the form's sections (header, status, declarant, duty summary, manifest, invoices, items, item duties, licences, compliance, declarations). Tables are located by header keywords; free-text fields are recovered from line sequences. |
| Normalisation | Handles the date formats seen on the form (`15/04/2022`, `30-MAR-22`, ISO), Indian number formatting, and GSTIN / IEC format validation. |
| Storage | 12-table relational schema keyed on the document. The same SQLAlchemy models target SQLite for local work and Azure SQL for hosted use. |
| Review | Streamlit interface that shows each extracted section (header, duties, items, manifest, licences, raw JSON) for a reviewer to check against the source document. |

## Results on the sample document

The pipeline was developed against a single 17-page Bill of Entry.

| Measure | Value |
|---|---:|
| Pages processed | 17 |
| Tables detected | 81 |
| Words analysed | 9,447 |
| Words with OCR confidence above 0.90 | 95.2% |
| Line items / licence records parsed | 30 / 30 |

Field-level extraction accuracy has not yet been measured (see limitations).

## Getting started

Requirements: Python 3.10+, an Azure subscription (the free tiers are sufficient).

```bash
git clone https://github.com/shubhstiws-new/customs-lens.git
cd customs-lens
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

pytest                                   # 59 unit tests; no Azure access needed
```

To run OCR, create `config/.env`:

```
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://<resource>.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=<key>
```

`scripts/02_setup_azure_resources.sh` provisions the resource with the Azure CLI and writes this file.

```bash
python src/ocr_full_document.py path/to/bill_of_entry.pdf   # OCR + parse → output/
streamlit run src/app/streamlit_app.py                      # review interface
```

## Repository layout

```
src/ocr_full_document.py     PDF chunking and Azure OCR
src/boe_parser.py            Section-aware parser and record types
src/pipeline/                Normalisation, database operations, end-to-end pipeline
src/database/                SQLAlchemy models (SQLite, Azure SQL) and DDL
src/app/streamlit_app.py     Review interface
scripts/                     Azure provisioning and environment checks
tests/                       Unit tests for normalisation and database operations
```

## Current status and limitations

| Item | Status |
|---|---|
| OCR, parsing, storage, review interface | Implemented end to end on one document |
| Corrections in the review interface | Read-only for now. A database update function exists (`update_document_field`) but is not yet connected to the interface. |
| Unit tests | 59 tests covering normalisation functions and database operations |
| Extraction accuracy | **Not yet measured.** The next step is a hand-verified ground-truth set of 5–10 documents and field-level precision/recall per section. |
| Generalisation | Parsing rules were written against one document. Layout variation across ports, BoE types and form revisions has not been tested. |
| Sample data | No sample PDF or OCR output is included, because real Bills of Entry contain importer identifiers. Test fixtures use synthetic values. |
| Rule-based parsing | Parsing relies on keyword and table-header heuristics. A Document Intelligence custom extraction model or an LLM-based extractor evaluated on the same ground truth would be a natural comparison. |

## Capabilities developed

Built over December 12–13, 2025 as a first document-AI project.

- Provisioning and operating Azure AI services through the CLI within free-tier limits
- Working around service constraints (page limits) without losing document structure
- Modelling a complex government form as a normalised relational schema
- Designing a human-in-the-loop review step for extraction output
- Handling documents that contain personal and commercial identifiers
