"""
Tests for database operations
"""

import pytest
import os
import sys
from pathlib import Path
from datetime import date

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.models_sqlite import (
    Base, Document, Status, Declarant, DutySummary, Manifest,
    Payment, Processing, Invoice, Item, ItemDuty, Licence, Compliance
)
from src.pipeline.db_operations import BoEDatabaseManager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def test_db():
    """Create a temporary test database"""
    db_path = "output/test_boe.db"

    # Remove if exists
    if os.path.exists(db_path):
        os.remove(db_path)

    manager = BoEDatabaseManager(db_path)
    manager.create_tables()

    yield manager

    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def sample_boe_data():
    """Sample BoE data for testing"""
    return {
        "header": {
            "document_id": "BE_TEST_001",
            "port_code": "INDEL4",
            "port_name": "NEW CUSTOM HOUSE, IGI AIRPORT",
            "be_no": "1234567",
            "be_date": "15/04/2022",
            "be_type": "H",
            "iec_br": "0512345678/6",
            "gstin_type": "27ABCDE1234F1Z5",
            "cb_code": "",
            "inv_count": 1,
            "item_count": 2,
            "cont_count": 0,
            "pkg_count": 1,
            "gross_weight_kgs": 54.6
        },
        "part1_status": {
            "be_status": "Cleared",
            "mode": "AIR",
            "def_be": "N",
            "kacha": "N",
            "sec_48": "N",
            "reimp": "N",
            "country_origin": "CHINA",
            "country_consignment": "CHINA"
        },
        "part1_declarant": {
            "importer_name": "Test Importer Ltd",
            "importer_address": "123 Test Street",
            "cb_name": "Test CB",
            "ad_code": "1234567"
        },
        "part1_duty_summary": {
            "bcd": 1000.0,
            "igst": 5000.0,
            "g_cess": 100.0,
            "total_duty": 6100.0,
            "tot_ass_val": 50000.0,
            "tot_amount": 6100.0
        },
        "part1_manifest": {
            "igm_no": "1000001",
            "igm_date": "14/04/2022",
            "mawb_no": "12345678901",
            "hawb_no": "HAWB1234567",
            "pkg": 1,
            "gross_weight": 54.6
        },
        "part1_payments": [
            {
                "sr_no": 1,
                "challan_no": "CH001",
                "paid_on": "16/04/2022",
                "amount": 6100.0
            }
        ],
        "part1_processing": [],
        "part2_invoices": [
            {
                "invoice_sno": 1,
                "invoice_no": "INV001",
                "invoice_date": "10/04/2022",
                "buyer_name": "Test Buyer",
                "seller_name": "Test Seller",
                "inv_value": 10000.0,
                "currency": "USD"
            }
        ],
        "part2_items": [
            {
                "invoice_sno": 1,
                "item_sno": 1,
                "cth": "84714190",
                "description": "Test Item 1",
                "unit_price": 100.0,
                "quantity": 50,
                "uqc": "NOS",
                "amount": 5000.0
            },
            {
                "invoice_sno": 1,
                "item_sno": 2,
                "cth": "84714190",
                "description": "Test Item 2",
                "unit_price": 100.0,
                "quantity": 50,
                "uqc": "NOS",
                "amount": 5000.0
            }
        ],
        "part3_item_duties": [],
        "part4_licences": [
            {
                "invoice_sno": 1,
                "item_sno": 1,
                "lic_slno": 1,
                "lic_no": "LIC001",
                "lic_date": "01-MAR-22",
                "code": "12",
                "port": "INLDH6",
                "debit_value": 2500.0
            },
            {
                "invoice_sno": 1,
                "item_sno": 2,
                "lic_slno": 1,
                "lic_no": "LIC001",
                "lic_date": "01-MAR-22",
                "code": "12",
                "port": "INLDH6",
                "debit_value": 2500.0
            }
        ],
        "part5_compliance": {
            "ooc_no": "OOC001",
            "ooc_date": "17/04/2022"
        }
    }


class TestDatabaseManager:
    """Tests for BoEDatabaseManager"""

    def test_create_tables(self, test_db):
        """Test table creation"""
        from sqlalchemy import text
        session = test_db.get_session()
        # Check documents table exists
        result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result]
        session.close()

        assert "documents" in tables
        assert "part1_duty_summary" in tables
        assert "part4_licence" in tables

    def test_insert_full_document(self, test_db, sample_boe_data):
        """Test inserting a complete document"""
        success = test_db.insert_full_document(sample_boe_data)
        assert success is True

        # Verify document exists
        session = test_db.get_session()
        doc = session.query(Document).filter(
            Document.document_id == "BE_TEST_001"
        ).first()
        session.close()

        assert doc is not None
        assert doc.be_no == "1234567"
        assert doc.port_code == "INDEL4"

    def test_insert_duplicate_skipped(self, test_db, sample_boe_data):
        """Test that duplicate documents are skipped"""
        # First insert
        success1 = test_db.insert_full_document(sample_boe_data)
        assert success1 is True

        # Second insert (should be skipped)
        success2 = test_db.insert_full_document(sample_boe_data, skip_existing=True)
        assert success2 is False

    def test_document_exists(self, test_db, sample_boe_data):
        """Test document_exists check"""
        session = test_db.get_session()

        # Before insert
        assert test_db.document_exists(session, "BE_TEST_001") is False

        session.close()

        # Insert
        test_db.insert_full_document(sample_boe_data)

        # After insert
        session = test_db.get_session()
        assert test_db.document_exists(session, "BE_TEST_001") is True
        session.close()

    def test_delete_document(self, test_db, sample_boe_data):
        """Test document deletion with cascade"""
        # Insert
        test_db.insert_full_document(sample_boe_data)

        # Verify exists
        session = test_db.get_session()
        assert test_db.document_exists(session, "BE_TEST_001") is True
        session.close()

        # Delete
        result = test_db.delete_document("BE_TEST_001")
        assert result is True

        # Verify deleted
        session = test_db.get_session()
        assert test_db.document_exists(session, "BE_TEST_001") is False
        session.close()

    def test_get_document_summary(self, test_db, sample_boe_data):
        """Test getting document summary"""
        test_db.insert_full_document(sample_boe_data)

        summary = test_db.get_document_summary("BE_TEST_001")

        assert summary is not None
        assert summary["document_id"] == "BE_TEST_001"
        assert summary["be_no"] == "1234567"
        assert summary["licence_count"] == 2


class TestRelationships:
    """Tests for database relationships"""

    def test_duty_summary_relationship(self, test_db, sample_boe_data):
        """Test document-duty_summary relationship"""
        test_db.insert_full_document(sample_boe_data)

        session = test_db.get_session()
        doc = session.query(Document).filter(
            Document.document_id == "BE_TEST_001"
        ).first()

        assert doc.duty_summary is not None
        assert doc.duty_summary.igst == 5000.0
        assert doc.duty_summary.total_duty == 6100.0
        session.close()

    def test_manifest_relationship(self, test_db, sample_boe_data):
        """Test document-manifest relationship"""
        test_db.insert_full_document(sample_boe_data)

        session = test_db.get_session()
        doc = session.query(Document).filter(
            Document.document_id == "BE_TEST_001"
        ).first()

        assert doc.manifest is not None
        assert doc.manifest.igm_no == "1000001"
        assert doc.manifest.pkg == 1
        session.close()

    def test_licences_relationship(self, test_db, sample_boe_data):
        """Test document-licences relationship"""
        test_db.insert_full_document(sample_boe_data)

        session = test_db.get_session()
        doc = session.query(Document).filter(
            Document.document_id == "BE_TEST_001"
        ).first()

        assert doc.licences is not None
        assert len(doc.licences) == 2
        assert doc.licences[0].lic_no == "LIC001"
        session.close()

    def test_items_relationship(self, test_db, sample_boe_data):
        """Test document-items relationship"""
        test_db.insert_full_document(sample_boe_data)

        session = test_db.get_session()
        doc = session.query(Document).filter(
            Document.document_id == "BE_TEST_001"
        ).first()

        assert doc.items is not None
        assert len(doc.items) == 2
        assert doc.items[0].cth == "84714190"
        session.close()


class TestDateParsing:
    """Tests for date parsing in database operations"""

    def test_licence_date_parsing(self, test_db, sample_boe_data):
        """Test that DD-MMM-YY dates are parsed correctly"""
        test_db.insert_full_document(sample_boe_data)

        session = test_db.get_session()
        licence = session.query(Licence).filter(
            Licence.document_id == "BE_TEST_001"
        ).first()

        assert licence.lic_date is not None
        assert licence.lic_date == date(2022, 3, 1)
        session.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
