"""
Insert Processing Details into Azure SQL Database
"""

import json
import pymssql
from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(Path(__file__).parent.parent / "config" / ".env")

OUTPUT_DIR = Path(__file__).parent.parent / "output"


def main():
    print("=" * 60)
    print("Inserting Processing Details into Azure SQL")
    print("=" * 60)

    # Load parsed data
    parsed_path = OUTPUT_DIR / "boe_parsed_final.json"
    print(f"\nLoading parsed data from: {parsed_path}")

    with open(parsed_path) as f:
        boe_data = json.load(f)

    document_id = boe_data["header"]["document_id"]
    processing = boe_data.get("part1_processing", [])

    print(f"Document ID: {document_id}")
    print(f"Processing events to insert: {len(processing)}")

    if not processing:
        print("No processing events to insert.")
        return

    # Connect to Azure SQL
    server = os.getenv("AZURE_SQL_SERVER")
    database = os.getenv("AZURE_SQL_DATABASE")
    username = os.getenv("AZURE_SQL_USERNAME")
    password = os.getenv("AZURE_SQL_PASSWORD")

    print(f"\nConnecting to {server}...")

    conn = pymssql.connect(
        server=server,
        user=username,
        password=password,
        database=database
    )

    cursor = conn.cursor()

    # Alter table to use VARCHAR for dates/times (OCR data has various formats)
    print("Ensuring table schema can handle various date formats...")
    try:
        cursor.execute("""
            ALTER TABLE part1.processing ALTER COLUMN event_date VARCHAR(50)
        """)
        cursor.execute("""
            ALTER TABLE part1.processing ALTER COLUMN event_time VARCHAR(50)
        """)
        conn.commit()
        print("  - Table schema updated")
    except Exception as e:
        # Column might already be VARCHAR or other error
        print(f"  - Schema update skipped: {e}")
        conn.rollback()

    # Delete existing processing records for this document
    print(f"Clearing existing processing records for {document_id}...")
    cursor.execute("DELETE FROM part1.processing WHERE document_id = %s", (document_id,))

    # Insert new processing records
    print("Inserting processing events...")
    for proc in processing:
        cursor.execute("""
            INSERT INTO part1.processing (document_id, event, event_date, event_time, exchange_rate)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            document_id,
            proc.get("event", ""),
            proc.get("event_date", ""),
            proc.get("event_time", ""),
            proc.get("exchange_rate", "")
        ))
        print(f"  - Inserted: {proc.get('event')}: {proc.get('event_date')} {proc.get('event_time')} | {proc.get('exchange_rate')}")

    conn.commit()

    # Verify insertion
    print("\nVerifying data in part1.processing table:")
    cursor.execute("""
        SELECT event, event_date, event_time, exchange_rate
        FROM part1.processing
        WHERE document_id = %s
    """, (document_id,))

    rows = cursor.fetchall()
    for row in rows:
        print(f"  - {row[0]}: {row[1]} {row[2]} | {row[3]}")

    cursor.close()
    conn.close()

    print(f"\nSuccessfully inserted {len(processing)} processing events!")


if __name__ == "__main__":
    main()
