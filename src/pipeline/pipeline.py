"""
End-to-End Pipeline
Processes PDF through OCR and inserts into database
"""

import json
import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BoEPipeline:
    """
    End-to-end pipeline for Bill of Entry processing:
    PDF -> OCR -> Parse -> Transform -> Database
    """

    def __init__(self, db_path: str = "output/boe_local.db"):
        """
        Initialize pipeline

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self._ocr_client = None
        self._db_manager = None

    @property
    def db_manager(self):
        """Lazy load database manager"""
        if self._db_manager is None:
            from .db_operations import BoEDatabaseManager
            self._db_manager = BoEDatabaseManager(self.db_path)
            self._db_manager.create_tables()
        return self._db_manager

    def process_pdf(
        self,
        pdf_path: str,
        output_dir: str = "output",
        save_intermediate: bool = True
    ) -> Dict[str, Any]:
        """
        Process a PDF file through the complete pipeline

        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory for intermediate outputs
            save_intermediate: Whether to save OCR and parsed JSON files

        Returns:
            Dictionary with processing results
        """
        start_time = time.time()
        pdf_path = Path(pdf_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        result = {
            "success": False,
            "pdf_path": str(pdf_path),
            "document_id": None,
            "stages": {},
            "errors": [],
            "processing_time_seconds": 0
        }

        try:
            # Stage 1: OCR
            logger.info(f"Stage 1: Running OCR on {pdf_path.name}")
            stage_start = time.time()

            from src.ocr_full_document import process_full_document
            ocr_result = process_full_document(str(pdf_path))

            result["stages"]["ocr"] = {
                "success": True,
                "time_seconds": time.time() - stage_start,
                "pages_processed": ocr_result.get("total_pages", 0),
                "tables_found": ocr_result.get("total_tables", 0)
            }

            if save_intermediate:
                ocr_output_path = output_dir / f"{pdf_path.stem}_ocr.json"
                with open(ocr_output_path, 'w') as f:
                    json.dump(ocr_result, f, indent=2, default=str)
                logger.info(f"Saved OCR output to {ocr_output_path}")

            # Stage 2: Parse
            logger.info("Stage 2: Parsing OCR output")
            stage_start = time.time()

            from src.boe_parser import parse_boe_document
            parsed_data = parse_boe_document(ocr_result)

            result["stages"]["parse"] = {
                "success": True,
                "time_seconds": time.time() - stage_start
            }
            result["document_id"] = parsed_data.get("header", {}).get("document_id")

            if save_intermediate:
                parsed_output_path = output_dir / f"{pdf_path.stem}_parsed.json"
                with open(parsed_output_path, 'w') as f:
                    json.dump(parsed_data, f, indent=2, default=str)
                logger.info(f"Saved parsed output to {parsed_output_path}")

            # Stage 3: Database Insert
            logger.info("Stage 3: Inserting into database")
            stage_start = time.time()

            success = self.db_manager.insert_full_document(parsed_data)

            result["stages"]["database"] = {
                "success": success,
                "time_seconds": time.time() - stage_start,
                "document_id": result["document_id"]
            }

            result["success"] = success

        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            result["errors"].append(str(e))
            result["success"] = False

        result["processing_time_seconds"] = time.time() - start_time
        logger.info(f"Pipeline completed in {result['processing_time_seconds']:.2f}s")

        return result

    def process_json(
        self,
        json_path: str,
        skip_existing: bool = True
    ) -> Dict[str, Any]:
        """
        Process an already-parsed JSON file directly to database

        Args:
            json_path: Path to the parsed JSON file
            skip_existing: Whether to skip if document exists

        Returns:
            Dictionary with processing results
        """
        start_time = time.time()

        result = {
            "success": False,
            "json_path": str(json_path),
            "document_id": None,
            "errors": [],
            "processing_time_seconds": 0
        }

        try:
            with open(json_path, 'r') as f:
                parsed_data = json.load(f)

            result["document_id"] = parsed_data.get("header", {}).get("document_id")

            success = self.db_manager.insert_full_document(
                parsed_data,
                skip_existing=skip_existing
            )
            result["success"] = success

        except Exception as e:
            logger.error(f"Error processing JSON: {e}")
            result["errors"].append(str(e))

        result["processing_time_seconds"] = time.time() - start_time
        return result

    def get_document_stats(self) -> Dict[str, Any]:
        """Get statistics about documents in the database"""
        from sqlalchemy import func
        from src.database.models_sqlite import Document, Licence, ItemDuty

        session = self.db_manager.get_session()
        try:
            doc_count = session.query(func.count(Document.id)).scalar()
            licence_count = session.query(func.count(Licence.id)).scalar()
            item_duty_count = session.query(func.count(ItemDuty.id)).scalar()

            return {
                "total_documents": doc_count,
                "total_licences": licence_count,
                "total_item_duties": item_duty_count
            }
        finally:
            session.close()


def run_pipeline(
    pdf_path: str,
    db_path: str = "output/boe_local.db",
    output_dir: str = "output"
) -> Dict[str, Any]:
    """
    Convenience function to run the full pipeline

    Args:
        pdf_path: Path to PDF file
        db_path: Path to SQLite database
        output_dir: Directory for outputs

    Returns:
        Processing result dictionary
    """
    pipeline = BoEPipeline(db_path=db_path)
    return pipeline.process_pdf(pdf_path, output_dir=output_dir)


def run_json_import(
    json_path: str,
    db_path: str = "output/boe_local.db"
) -> Dict[str, Any]:
    """
    Import from parsed JSON to database

    Args:
        json_path: Path to parsed JSON file
        db_path: Path to SQLite database

    Returns:
        Processing result dictionary
    """
    pipeline = BoEPipeline(db_path=db_path)
    return pipeline.process_json(json_path)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python pipeline.py <pdf_path|json_path>")
        print("  For PDF: python pipeline.py /path/to/document.pdf")
        print("  For JSON: python pipeline.py /path/to/parsed.json --json")
        sys.exit(1)

    input_path = sys.argv[1]

    if "--json" in sys.argv or input_path.endswith(".json"):
        print(f"Importing from JSON: {input_path}")
        result = run_json_import(input_path)
    else:
        print(f"Processing PDF: {input_path}")
        result = run_pipeline(input_path)

    print("\n" + "=" * 60)
    print("PIPELINE RESULT")
    print("=" * 60)
    print(json.dumps(result, indent=2, default=str))
