"""
Update all database tables with parsed BOE data
"""

import json
import pymssql
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).parent.parent / "config" / ".env")
OUTPUT_DIR = Path(__file__).parent.parent / "output"


def main():
    print("=" * 60)
    print("Updating All Tables with Parsed BOE Data")
    print("=" * 60)

    # Load parsed data
    with open(OUTPUT_DIR / "boe_parsed_final.json") as f:
        boe = json.load(f)

    document_id = boe["header"]["document_id"]
    print(f"\nDocument ID: {document_id}")

    # Connect to Azure SQL
    conn = pymssql.connect(
        server=os.getenv("AZURE_SQL_SERVER"),
        user=os.getenv("AZURE_SQL_USERNAME"),
        password=os.getenv("AZURE_SQL_PASSWORD"),
        database=os.getenv("AZURE_SQL_DATABASE")
    )
    cursor = conn.cursor()

    # Update part1.status
    print("\nUpdating part1.status...")
    status = boe["part1_status"]
    cursor.execute("DELETE FROM part1.status WHERE document_id = %s", (document_id,))
    cursor.execute("""
        INSERT INTO part1.status
        (document_id, be_status, mode, def_be, kacha, sec_48, reimp, adv_be, assess, exam, hss, first_check, prov_final)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        document_id,
        status.get("be_status", ""),
        status.get("mode", ""),
        status.get("def_be", ""),
        status.get("kacha", ""),
        status.get("sec_48", ""),
        status.get("reimp", ""),
        status.get("adv_be", ""),
        status.get("assess", ""),
        status.get("exam", ""),
        status.get("hss", ""),
        status.get("first_check", ""),
        status.get("prov_final", ""),
    ))
    print(f"  - BE Status: {status.get('be_status')}, Mode: {status.get('mode')}")

    # Update part1.manifest
    print("\nUpdating part1.manifest...")
    manifest = boe["part1_manifest"]
    cursor.execute("DELETE FROM part1.manifest WHERE document_id = %s", (document_id,))
    cursor.execute("""
        INSERT INTO part1.manifest
        (document_id, igm_no, igm_date, inw_date, gigm_no, gigm_date, mawb_no, mawb_date, hawb_no, hawb_date, pkg, gross_weight)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        document_id,
        manifest.get("igm_no", ""),
        manifest.get("igm_date", ""),
        manifest.get("inw_date", ""),
        manifest.get("gigm_no", ""),
        manifest.get("gigm_date", ""),
        manifest.get("mawb_no", ""),
        manifest.get("mawb_date", ""),
        manifest.get("hawb_no", ""),
        manifest.get("hawb_date", ""),
        manifest.get("pkg", 0),
        manifest.get("gross_weight", 0),
    ))
    print(f"  - IGM: {manifest.get('igm_no')}, MAWB: {manifest.get('mawb_no')}, HAWB: {manifest.get('hawb_no')}")

    # Update part1.payment
    print("\nUpdating part1.payment...")
    cursor.execute("DELETE FROM part1.payment WHERE document_id = %s", (document_id,))
    for payment in boe.get("part1_payments", []):
        cursor.execute("""
            INSERT INTO part1.payment (document_id, sr_no, challan_no, paid_on, amount)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            document_id,
            payment.get("sr_no", 0),
            payment.get("challan_no", ""),
            payment.get("paid_on", ""),
            payment.get("amount", 0),
        ))
    print(f"  - Inserted {len(boe.get('part1_payments', []))} payment records")

    # Update part2.item
    print("\nUpdating part2.item...")
    cursor.execute("DELETE FROM part2.item WHERE document_id = %s", (document_id,))
    for item in boe.get("part2_items", []):
        cursor.execute("""
            INSERT INTO part2.item
            (document_id, invoice_sno, item_sno, cth, description, unit_price, quantity, uqc, amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            document_id,
            item.get("invoice_sno", 1),
            item.get("item_sno", 0),
            item.get("cth", ""),
            item.get("description", "")[:500],
            item.get("unit_price", 0),
            item.get("quantity", 0),
            item.get("uqc", ""),
            item.get("amount", 0),
        ))
    print(f"  - Inserted {len(boe.get('part2_items', []))} item records")

    conn.commit()

    # Verify updates
    print("\n" + "=" * 60)
    print("Verification - Data in Tables")
    print("=" * 60)

    tables = [
        ("part1", "status", "be_status, mode, def_be"),
        ("part1", "manifest", "igm_no, mawb_no, hawb_no"),
        ("part1", "payment", "challan_no, amount"),
        ("part2", "item", "item_sno, cth, quantity, amount"),
    ]

    for schema, table, cols in tables:
        cursor.execute(f"SELECT {cols} FROM [{schema}].[{table}] WHERE document_id = %s", (document_id,))
        rows = cursor.fetchall()
        print(f"\n{schema}.{table}: {len(rows)} rows")
        for row in rows[:3]:
            print(f"  {row}")

    cursor.close()
    conn.close()
    print("\nDone!")


if __name__ == "__main__":
    main()
