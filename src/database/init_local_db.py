"""
Initialize Local SQLite Database for Testing
This allows testing the schema without Azure SQL connectivity
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import create_engine, text, inspect
from src.database.models_sqlite import Base


def create_local_database(db_path: str = "output/boe_local.db"):
    """Create local SQLite database with all tables"""

    # Ensure output directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Creating Local SQLite Database")
    print("=" * 60)

    # Create engine
    engine = create_engine(f"sqlite:///{db_path}", echo=False)

    # Create all tables
    print("\nCreating tables...")
    Base.metadata.create_all(engine)

    # List created tables
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    print(f"\nTables created: {len(tables)}")
    for table in sorted(tables):
        columns = inspector.get_columns(table)
        print(f"  {table}: {len(columns)} columns")

    print(f"\nDatabase created at: {db_path}")

    return engine


def test_insert_sample_data(engine):
    """Test inserting sample data"""

    from src.database.models_sqlite import Document, DutySummary, Manifest, Licence
    from sqlalchemy.orm import sessionmaker
    from datetime import date

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Create sample document
        doc = Document(
            document_id="BE7654321",
            port_code="INDEL4",
            port_name="NEW CUSTOM HOUSE, IGI AIRPORT, NEW DELHI - 110037",
            be_no="7654321",
            be_date=date(2022, 4, 15),
            be_type="H",
            iec_br="0512345678/6",
            gstin_type="27ABCDE1234F1Z5",
            inv_count=1,
            item_count=30,
        )
        session.add(doc)
        session.flush()

        # Add duty summary (using float for SQLite)
        duty = DutySummary(
            document_id="BE7654321",
            igst=113241.00,
            g_cess=140.00,
            total_duty=118381.00,
            tot_ass_val=576262.00,
        )
        session.add(duty)

        # Add manifest
        manifest = Manifest(
            document_id="BE7654321",
            igm_no="1000001",
            igm_date=date(2022, 4, 14),
            mawb_no="12345678901",
            hawb_no="HAWB1234567",
            pkg=1,
            gross_weight=54.6,
        )
        session.add(manifest)

        # Add sample licences
        for i in range(1, 4):
            lic = Licence(
                document_id="BE7654321",
                invoice_sno=1,
                item_sno=i,
                lic_slno=19,
                lic_no="1100000001",
                lic_date=date(2022, 3, 30),
                code="12",
                port="INLDH6",
            )
            session.add(lic)

        session.commit()
        print("\nSample data inserted successfully!")

        # Query back
        doc_count = session.query(Document).count()
        lic_count = session.query(Licence).count()
        print(f"Documents: {doc_count}")
        print(f"Licences: {lic_count}")

    except Exception as e:
        session.rollback()
        print(f"Error inserting sample data: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    engine = create_local_database()
    test_insert_sample_data(engine)
