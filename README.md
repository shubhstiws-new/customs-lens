# Bill of Entry OCR Data Extraction System

An end-to-end system for extracting structured data from Indian Customs Bill of Entry (BoE) PDF documents using Azure Document Intelligence OCR and storing in a database.

## Features

- **OCR Processing**: Uses Azure Document Intelligence (Form Recognizer) to extract text and tables from PDF documents
- **Structured Data Extraction**: Parses OCR output into structured BoE data format
- **Database Storage**: SQLite for local testing, Azure SQL for production
- **Data Validation**: Comprehensive transformers for dates, numbers, and field validation
- **Human Review Interface**: Streamlit app for reviewing and correcting extracted data
- **Full Test Suite**: 59 unit tests covering transformers and database operations

## Project Structure

```
boe/
├── config/
│   └── .env                    # Azure credentials (not in git)
├── src/
│   ├── ocr_full_document.py    # Full document OCR with page chunking
│   ├── boe_parser.py           # Structured data parser
│   ├── database/
│   │   ├── models.py           # SQLAlchemy models (Azure SQL)
│   │   ├── models_sqlite.py    # SQLAlchemy models (SQLite)
│   │   ├── connection.py       # Database connection management
│   │   └── schema.sql          # Full SQL DDL schema
│   ├── pipeline/
│   │   ├── transformers.py     # Data transformation functions
│   │   ├── db_operations.py    # Database CRUD operations
│   │   └── pipeline.py         # End-to-end processing pipeline
│   └── app/
│       └── streamlit_app.py    # Human review interface
├── tests/
│   ├── test_transformers.py    # Transformer unit tests
│   └── test_database.py        # Database operation tests
├── output/
│   ├── boe_local.db            # Local SQLite database
│   ├── boe_parsed_final.json   # Sample parsed output
│   └── ocr_full_output.json    # Sample OCR output
└── IMPLEMENTATION_PLAN.md      # Detailed implementation plan
```

## Quick Start

### Prerequisites

- Python 3.10+
- Azure Account (free tier works)
- uv package manager

### Installation

```bash
# Clone and navigate to project
cd /Users/shubh/boe

# Create virtual environment
uv venv venv
source venv/bin/activate

# Install dependencies
uv pip install azure-ai-formrecognizer azure-identity sqlalchemy pymupdf streamlit pytest
```

### Configuration

Create `config/.env` with Azure credentials:
```
AZURE_DOC_INTEL_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_DOC_INTEL_KEY=your-key-here
```

### Usage

#### 1. Process a PDF through OCR
```bash
python src/ocr_full_document.py path/to/document.pdf
```

#### 2. Import parsed JSON to database
```bash
python -c "from src.pipeline import run_json_import; run_json_import('output/boe_parsed_final.json')"
```

#### 3. Run the validation interface
```bash
streamlit run src/app/streamlit_app.py
```

#### 4. Run tests
```bash
python -m pytest tests/ -v
```

## Database Schema

12 tables across document sections:

| Table | Description |
|-------|-------------|
| `documents` | Main BoE header (BE No, Date, Port, IEC, GSTIN) |
| `part1_status` | Status flags, country info |
| `part1_declarant` | Importer/CB details |
| `part1_duty_summary` | Duty totals (BCD, IGST, etc.) |
| `part1_manifest` | IGM, MAWB, HAWB details |
| `part1_payment` | Payment challans |
| `part1_processing` | Processing events |
| `part2_invoice` | Invoice details |
| `part2_item` | Line items |
| `part3_item_duty` | Per-item duty breakdown |
| `part4_licence` | Licence debit details |
| `part5_compliance` | Examination/OOC details |

## Azure Resources Used

| Resource | SKU | Monthly Cost |
|----------|-----|--------------|
| Document Intelligence | F0 (Free) | $0 (500 pages/month) |
| SQL Database | Serverless Free | $0 (100K vCore seconds) |

## Sample Data

The system was tested on a 17-page Bill of Entry document containing:
- 30 line items
- 30 licence records
- IGST: Rs. 113,241
- Total Duty: Rs. 118,381

OCR Results:
- 95.2% high confidence (>90%)
- 81 tables extracted
- 9,447 words analyzed

## License

Private/Internal Use
