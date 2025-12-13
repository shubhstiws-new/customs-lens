"""
Bill of Entry Parser
Extracts structured data from OCR output based on document sections
"""

import json
import re
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class BoEHeader:
    """Bill of Entry Header Information"""
    document_id: str = ""
    port_code: str = ""
    port_name: str = ""
    be_no: str = ""
    be_date: str = ""
    be_type: str = ""
    iec_br: str = ""
    gstin_type: str = ""
    cb_code: str = ""
    inv_count: int = 0
    item_count: int = 0
    cont_count: int = 0
    pkg_count: int = 0
    gross_weight_kgs: float = 0.0


@dataclass
class Part1Status:
    """Part I - Section A: Status"""
    be_status: str = ""
    mode: str = ""
    def_be: str = ""
    kacha: str = ""
    sec_48: str = ""
    reimp: str = ""
    adv_be: str = ""
    assess: str = ""
    exam: str = ""
    hss: str = ""
    first_check: str = ""
    prov_final: str = ""
    country_origin: str = ""
    country_consignment: str = ""
    port_loading: str = ""
    port_shipment: str = ""


@dataclass
class Part1Declarant:
    """Part I - Section B: Declarant"""
    importer_name: str = ""
    importer_address: str = ""
    cb_name: str = ""
    aeo: str = ""
    ucr: str = ""
    ad_code: str = ""


@dataclass
class Part1DutySummary:
    """Part I - Section C: Duty Summary"""
    bcd: float = 0.0
    acd: float = 0.0
    sws: float = 0.0
    nccd: float = 0.0
    add_duty: float = 0.0
    cvd: float = 0.0
    igst: float = 0.0
    g_cess: float = 0.0
    sg: float = 0.0
    saed: float = 0.0
    gsia: float = 0.0
    tta: float = 0.0
    health: float = 0.0
    total_duty: float = 0.0
    interest: float = 0.0
    penalty: float = 0.0
    fine: float = 0.0
    tot_ass_val: float = 0.0
    tot_amount: float = 0.0


@dataclass
class Part1Manifest:
    """Part I - Section D: Manifest Details"""
    igm_no: str = ""
    igm_date: str = ""
    inw_date: str = ""
    gigm_no: str = ""
    gigm_date: str = ""
    mawb_no: str = ""
    mawb_date: str = ""
    hawb_no: str = ""
    hawb_date: str = ""
    pkg: int = 0
    gross_weight: float = 0.0


@dataclass
class Part1Payment:
    """Part I - Section F: Payment Details"""
    sr_no: int = 0
    challan_no: str = ""
    paid_on: str = ""
    amount: float = 0.0


@dataclass
class Part1Bond:
    """Part I - Section E: Bond Details"""
    bond_no: str = ""
    port: str = ""
    bond_code: str = ""
    debt_amt: float = 0.0
    bg_amt: float = 0.0


@dataclass
class Part1InvoiceSummary:
    """Part I - Section I: Invoice Details Summary"""
    sno: int = 0
    invoice_no: str = ""
    inv_amt: float = 0.0
    currency: str = ""


@dataclass
class Part1Processing:
    """Part I - Section H: Processing Details"""
    event: str = ""
    event_date: str = ""
    event_time: str = ""
    exchange_rate: str = ""


@dataclass
class Part2Invoice:
    """Part II - Invoice Details"""
    invoice_sno: int = 0
    invoice_no: str = ""
    invoice_date: str = ""
    buyer_name: str = ""
    buyer_address: str = ""
    seller_name: str = ""
    seller_address: str = ""
    supplier_name: str = ""
    supplier_address: str = ""
    inv_value: float = 0.0
    currency: str = ""
    terms: str = ""
    valuation_method: str = ""
    assessed_value: float = 0.0


@dataclass
class Part2Item:
    """Part II - Section E: Item Details"""
    invoice_sno: int = 0
    item_sno: int = 0
    cth: str = ""
    description: str = ""
    unit_price: float = 0.0
    quantity: float = 0.0
    uqc: str = ""
    amount: float = 0.0


@dataclass
class Part3ItemDuty:
    """Part III - Item Duty Details"""
    invoice_sno: int = 0
    item_sno: int = 0
    cth: str = ""
    ceth: str = ""
    description: str = ""
    unit_price: float = 0.0
    country_origin: str = ""
    commercial_qty: float = 0.0
    commercial_uqc: str = ""
    standard_qty: float = 0.0
    standard_uqc: str = ""
    scheme_code: str = ""
    assessed_value: float = 0.0
    total_duty: float = 0.0
    bcd_rate: float = 0.0
    bcd_amount: float = 0.0
    igst_rate: float = 0.0
    igst_amount: float = 0.0


@dataclass
class Part4Licence:
    """Part IV - Licence Details"""
    invoice_sno: int = 0
    item_sno: int = 0
    lic_slno: int = 0
    lic_no: str = ""
    lic_date: str = ""
    code: str = ""
    port: str = ""
    debit_value: float = 0.0
    qty: float = 0.0
    uqc: str = ""


@dataclass
class Part1Container:
    """Part I - Section G: Container Details"""
    container_number: str = ""
    truck_number: str = ""
    seal_number: str = ""
    fcl_lcl: str = ""


@dataclass
class Part4Certificate:
    """Part IV - Section G: Certificate Details"""
    certificate_number: str = ""
    certificate_date: str = ""
    certificate_type: str = ""
    prc_level: str = ""
    iec: str = ""
    branch_slno: str = ""


@dataclass
class Part5Compliance:
    """Part V - Compliance Details"""
    examination_order: str = ""
    examination_instructions: str = ""
    compulsory_compliance: str = ""
    ooc_no: str = ""
    ooc_date: str = ""


@dataclass
class BillOfEntry:
    """Complete Bill of Entry Structure"""
    header: BoEHeader = field(default_factory=BoEHeader)
    part1_status: Part1Status = field(default_factory=Part1Status)
    part1_declarant: Part1Declarant = field(default_factory=Part1Declarant)
    part1_duty_summary: Part1DutySummary = field(default_factory=Part1DutySummary)
    part1_manifest: Part1Manifest = field(default_factory=Part1Manifest)
    part1_bond: Part1Bond = field(default_factory=Part1Bond)
    part1_invoice_summary: list = field(default_factory=list)
    part1_payments: list = field(default_factory=list)
    part1_processing: list = field(default_factory=list)
    part1_containers: list = field(default_factory=list)
    part2_invoices: list = field(default_factory=list)
    part2_items: list = field(default_factory=list)
    part3_item_duties: list = field(default_factory=list)
    part4_licences: list = field(default_factory=list)
    part4_certificates: list = field(default_factory=list)
    part5_compliance: Part5Compliance = field(default_factory=Part5Compliance)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "header": asdict(self.header),
            "part1_status": asdict(self.part1_status),
            "part1_declarant": asdict(self.part1_declarant),
            "part1_duty_summary": asdict(self.part1_duty_summary),
            "part1_manifest": asdict(self.part1_manifest),
            "part1_bond": asdict(self.part1_bond),
            "part1_invoice_summary": [asdict(i) for i in self.part1_invoice_summary],
            "part1_payments": [asdict(p) for p in self.part1_payments],
            "part1_processing": [asdict(p) for p in self.part1_processing],
            "part1_containers": [asdict(c) for c in self.part1_containers],
            "part2_invoices": [asdict(i) for i in self.part2_invoices],
            "part2_items": [asdict(i) for i in self.part2_items],
            "part3_item_duties": [asdict(d) for d in self.part3_item_duties],
            "part4_licences": [asdict(l) for l in self.part4_licences],
            "part4_certificates": [asdict(c) for c in self.part4_certificates],
            "part5_compliance": asdict(self.part5_compliance),
        }


def parse_float(value: Any) -> float:
    """Safely parse a float value"""
    if value is None:
        return 0.0
    try:
        # Remove commas and other formatting
        cleaned = str(value).replace(",", "").replace(" ", "").strip()
        return float(cleaned) if cleaned else 0.0
    except (ValueError, TypeError):
        return 0.0


def parse_int(value: Any) -> int:
    """Safely parse an integer value"""
    if value is None:
        return 0
    try:
        cleaned = str(value).replace(",", "").replace(" ", "").strip()
        return int(float(cleaned)) if cleaned else 0
    except (ValueError, TypeError):
        return 0


def find_table_by_headers(tables: list, header_keywords: list, page: Optional[int] = None) -> Optional[dict]:
    """Find a table containing specific header keywords"""
    for table in tables:
        if page is not None and table.get("page") != page:
            continue

        headers = table.get("headers", [])
        headers_text = " ".join(str(h) for h in headers if h).upper()

        if all(kw.upper() in headers_text for kw in header_keywords):
            return table

    return None


def extract_from_lines(lines: list, start_keyword: str, offset: int = 1) -> str:
    """Extract value from lines following a keyword"""
    for i, line in enumerate(lines):
        content = str(line.get('content', '') if isinstance(line, dict) else line)
        if start_keyword.upper() in content.upper():
            if i + offset < len(lines):
                next_line = lines[i + offset]
                return str(next_line.get('content', '') if isinstance(next_line, dict) else next_line).strip()
    return ""


def extract_multiline_value(lines: list, start_idx: int, end_keywords: list, max_lines: int = 5) -> str:
    """Extract multi-line value until we hit an end keyword or max lines"""
    values = []
    for i in range(start_idx, min(start_idx + max_lines, len(lines))):
        content = str(lines[i].get('content', '') if isinstance(lines[i], dict) else lines[i]).strip()
        # Check if we've hit an end keyword
        if any(kw.upper() in content.upper() for kw in end_keywords):
            break
        if content and not content.startswith(('1.', '2.', '3.', '4.', '5.')):
            values.append(content)
    return ' '.join(values)


def find_line_index(lines: list, keyword: str) -> int:
    """Find the index of a line containing the keyword"""
    for i, line in enumerate(lines):
        content = str(line.get('content', '') if isinstance(line, dict) else line)
        if keyword.upper() in content.upper():
            return i
    return -1


def parse_ocr_output(ocr_data: dict) -> BillOfEntry:
    """Parse OCR output into structured Bill of Entry data"""

    boe = BillOfEntry()
    tables = ocr_data.get("tables_raw", [])

    # Get page lines for line-based extraction
    raw_data_path = Path(__file__).parent.parent / "output" / "ocr_raw_output.json"
    page_lines = []
    if raw_data_path.exists():
        try:
            with open(raw_data_path) as f:
                raw_ocr = json.load(f)
            pages = raw_ocr.get('pages', [])
            if pages:
                page_lines = pages[0].get('lines', [])
        except Exception:
            pass

    # Parse Header from first page tables
    header_table = find_table_by_headers(tables, ["Port Code", "BE No"], page=1)
    if header_table:
        data = header_table.get("data", [])
        if len(data) >= 2:
            # Row 0: headers, Row 1: values
            for i, val in enumerate(data[1]):
                if i == 0:
                    boe.header.port_code = str(val or "").strip()
                elif i == 1:
                    boe.header.be_no = str(val or "").strip()
                elif i == 2:
                    boe.header.be_date = str(val or "").strip()
                elif i == 3:
                    boe.header.be_type = str(val or "").strip()

    # Parse Status section (A. STATUS)
    status_table = find_table_by_headers(tables, ["STATUS", "BE STATUS"], page=1)
    if status_table:
        data = status_table.get("data", [])
        if len(data) >= 2:
            # Row 1 contains the values
            row = data[1]
            if len(row) >= 13:
                boe.part1_status.be_status = str(row[1] or "").strip()
                boe.part1_status.mode = str(row[2] or "").strip()
                boe.part1_status.def_be = str(row[3] or "").strip()
                boe.part1_status.kacha = str(row[4] or "").strip()
                boe.part1_status.sec_48 = str(row[5] or "").strip()
                boe.part1_status.reimp = str(row[6] or "").strip()
                boe.part1_status.adv_be = str(row[7] or "").strip()
                boe.part1_status.assess = str(row[8] or "").strip()
                boe.part1_status.exam = str(row[9] or "").strip()
                boe.part1_status.hss = str(row[10] or "").strip()
                boe.part1_status.first_check = str(row[11] or "").strip()
                boe.part1_status.prov_final = str(row[12] or "").strip()

    # Parse TYPE table (INV, ITEM, CONT counts)
    type_table = find_table_by_headers(tables, ["TYPE", "INV", "ITEM"], page=1)
    if type_table:
        data = type_table.get("data", [])
        for row in data:
            row_text = " ".join(str(c) for c in row if c)
            if "Nos" in row_text or any(str(c).isdigit() for c in row if c):
                for i, val in enumerate(row):
                    if i == 1:
                        boe.header.inv_count = parse_int(val)
                    elif i == 2:
                        boe.header.item_count = parse_int(val)
                    elif i == 3:
                        boe.header.cont_count = parse_int(val)

    # === LINE-BASED EXTRACTION FOR MISSING FIELDS ===
    if page_lines:
        # Extract CB CODE from lines (line after "CB CODE" label)
        cb_code_idx = find_line_index(page_lines, "CB CODE")
        if cb_code_idx >= 0:
            # CB CODE value is typically 3 lines after the label
            for offset in range(1, 5):
                if cb_code_idx + offset < len(page_lines):
                    val = page_lines[cb_code_idx + offset].get('content', '') if isinstance(page_lines[cb_code_idx + offset], dict) else page_lines[cb_code_idx + offset]
                    val = str(val).strip()
                    # CB code pattern: alphanumeric, typically 15 chars
                    if val and len(val) >= 10 and val[0].isalpha() and not val.startswith(('INDIAN', 'PORT', 'OOC')):
                        boe.header.cb_code = val
                        break

        # Extract Gross Weight from lines
        gw_idx = find_line_index(page_lines, "G.WT (KGS)")
        if gw_idx >= 0 and gw_idx + 1 < len(page_lines):
            gw_val = page_lines[gw_idx + 1].get('content', '') if isinstance(page_lines[gw_idx + 1], dict) else page_lines[gw_idx + 1]
            boe.header.gross_weight_kgs = parse_float(gw_val)

        # Extract Country of Origin
        origin_idx = find_line_index(page_lines, "COUNTRY OF ORIGIN")
        if origin_idx >= 0 and origin_idx + 1 < len(page_lines):
            origin_val = page_lines[origin_idx + 1].get('content', '') if isinstance(page_lines[origin_idx + 1], dict) else page_lines[origin_idx + 1]
            boe.part1_status.country_origin = str(origin_val).strip()

        # Extract Country of Consignment
        consignment_idx = find_line_index(page_lines, "COUNTRY OF CONSIGNMENT")
        if consignment_idx >= 0 and consignment_idx + 1 < len(page_lines):
            consignment_val = page_lines[consignment_idx + 1].get('content', '') if isinstance(page_lines[consignment_idx + 1], dict) else page_lines[consignment_idx + 1]
            boe.part1_status.country_consignment = str(consignment_val).strip()

        # Extract Port of Loading
        loading_idx = find_line_index(page_lines, "PORT OF LOADING")
        if loading_idx >= 0 and loading_idx + 1 < len(page_lines):
            loading_val = page_lines[loading_idx + 1].get('content', '') if isinstance(page_lines[loading_idx + 1], dict) else page_lines[loading_idx + 1]
            boe.part1_status.port_loading = str(loading_val).strip()

        # Extract Port of Shipment
        shipment_idx = find_line_index(page_lines, "PORT OF SHIPMENT")
        if shipment_idx >= 0 and shipment_idx + 1 < len(page_lines):
            shipment_val = page_lines[shipment_idx + 1].get('content', '') if isinstance(page_lines[shipment_idx + 1], dict) else page_lines[shipment_idx + 1]
            boe.part1_status.port_shipment = str(shipment_val).strip()

        # Extract Importer Name & Address (multi-line)
        # Structure varies - text may be interleaved with DECLARANT header
        importer_idx = find_line_index(page_lines, "IMPORTER NAME")
        if importer_idx >= 0:
            importer_lines = []
            for offset in range(1, 10):
                if importer_idx + offset < len(page_lines):
                    line_val = page_lines[importer_idx + offset].get('content', '') if isinstance(page_lines[importer_idx + offset], dict) else page_lines[importer_idx + offset]
                    line_val = str(line_val).strip()
                    # Stop at CB NAME (the next section)
                    if 'CB NAME' in line_val.upper():
                        break
                    # Skip DECLARANT header but continue collecting address lines
                    if line_val.upper() == 'DECLARANT':
                        continue
                    # Skip section prefixes
                    if line_val.upper().startswith(('1.', '2.', '3.', '4.', 'B.', 'C.')):
                        continue
                    # Skip section headers
                    if line_val.upper() in ['AEO', 'UCR', 'AD CODE']:
                        break
                    if line_val:
                        importer_lines.append(line_val)
            boe.part1_declarant.importer_name = ' '.join(importer_lines)

        # Extract CB Name
        cb_name_idx = find_line_index(page_lines, "CB NAME")
        if cb_name_idx >= 0:
            cb_name_line = page_lines[cb_name_idx].get('content', '') if isinstance(page_lines[cb_name_idx], dict) else page_lines[cb_name_idx]
            cb_name_line = str(cb_name_line)
            # CB NAME might be on the same line (e.g., "2.CB NAME CORE LOGISTICS")
            if 'CB NAME' in cb_name_line:
                parts = cb_name_line.split('CB NAME')
                if len(parts) > 1:
                    boe.part1_declarant.cb_name = parts[1].strip()
                elif cb_name_idx + 1 < len(page_lines):
                    next_val = page_lines[cb_name_idx + 1].get('content', '') if isinstance(page_lines[cb_name_idx + 1], dict) else page_lines[cb_name_idx + 1]
                    boe.part1_declarant.cb_name = str(next_val).strip()

        # Extract AD Code
        ad_code_idx = find_line_index(page_lines, "AD CODE")
        if ad_code_idx >= 0 and ad_code_idx + 1 < len(page_lines):
            ad_code_val = page_lines[ad_code_idx + 1].get('content', '') if isinstance(page_lines[ad_code_idx + 1], dict) else page_lines[ad_code_idx + 1]
            boe.part1_declarant.ad_code = str(ad_code_val).strip()

        # Extract Bond Details (Part I, Section E)
        # Structure: Line 138: 1.BOND NO., 139: 2.PORT, 140: bond_no, 141: port
        #            142: 3.BOND CD 4.DEBT AMT 5.BG AMT, 143: bond_cd, 144: debt_amt, 145: bg_amt
        bond_no_idx = find_line_index(page_lines, "BOND NO")
        if bond_no_idx >= 0:
            # Bond number is at bond_no_idx + 2 (skip "2.PORT")
            if bond_no_idx + 2 < len(page_lines):
                val = page_lines[bond_no_idx + 2].get('content', '') if isinstance(page_lines[bond_no_idx + 2], dict) else page_lines[bond_no_idx + 2]
                val = str(val).strip()
                if val and val.isdigit() and len(val) >= 8:
                    boe.part1_bond.bond_no = val

            # Port is at bond_no_idx + 3
            if bond_no_idx + 3 < len(page_lines):
                val = page_lines[bond_no_idx + 3].get('content', '') if isinstance(page_lines[bond_no_idx + 3], dict) else page_lines[bond_no_idx + 3]
                val = str(val).strip()
                if val and len(val) >= 5 and val.startswith('IN'):
                    boe.part1_bond.port = val

            # Bond CD line is at bond_no_idx + 4, values follow at +5, +6, +7
            if bond_no_idx + 5 < len(page_lines):
                val = page_lines[bond_no_idx + 5].get('content', '') if isinstance(page_lines[bond_no_idx + 5], dict) else page_lines[bond_no_idx + 5]
                val = str(val).strip()
                if val and len(val) <= 3:
                    boe.part1_bond.bond_code = val

            if bond_no_idx + 6 < len(page_lines):
                val = page_lines[bond_no_idx + 6].get('content', '') if isinstance(page_lines[bond_no_idx + 6], dict) else page_lines[bond_no_idx + 6]
                boe.part1_bond.debt_amt = parse_float(val)

            if bond_no_idx + 7 < len(page_lines):
                val = page_lines[bond_no_idx + 7].get('content', '') if isinstance(page_lines[bond_no_idx + 7], dict) else page_lines[bond_no_idx + 7]
                boe.part1_bond.bg_amt = parse_float(val)

        # Extract INV/ITEM/CONT counts from lines (fixed structure)
        # Structure: Line 22-25: TYPE, INV, ITEM, CONT (headers)
        #            Line 26-29: Nos, 1, 30, 0 (values)
        # Need to find the exact "TYPE" line (not "BE Type" or "GSTIN/TYPE")
        type_idx = -1
        for i, line in enumerate(page_lines):
            content = str(line.get('content', '') if isinstance(line, dict) else line).strip()
            if content == "TYPE":
                type_idx = i
                break

        if type_idx >= 0:
            # Find the "Nos" line to get correct values
            for offset in range(1, 6):
                if type_idx + offset < len(page_lines):
                    line_content = page_lines[type_idx + offset].get('content', '') if isinstance(page_lines[type_idx + offset], dict) else page_lines[type_idx + offset]
                    if str(line_content).strip() == "Nos":
                        # Next 3 lines are INV, ITEM, CONT values
                        if type_idx + offset + 1 < len(page_lines):
                            inv_val = page_lines[type_idx + offset + 1].get('content', '') if isinstance(page_lines[type_idx + offset + 1], dict) else page_lines[type_idx + offset + 1]
                            boe.header.inv_count = parse_int(inv_val)
                        if type_idx + offset + 2 < len(page_lines):
                            item_val = page_lines[type_idx + offset + 2].get('content', '') if isinstance(page_lines[type_idx + offset + 2], dict) else page_lines[type_idx + offset + 2]
                            boe.header.item_count = parse_int(item_val)
                        if type_idx + offset + 3 < len(page_lines):
                            cont_val = page_lines[type_idx + offset + 3].get('content', '') if isinstance(page_lines[type_idx + offset + 3], dict) else page_lines[type_idx + offset + 3]
                            boe.header.cont_count = parse_int(cont_val)
                        break

        # Extract Invoice Summary (Part I, Section I)
        # Structure: Line N: 2.INVOICE NO, N+1: invoice_no, N+2: 3.INV. AMT, N+3: amount
        inv_no_idx = find_line_index(page_lines, "INVOICE NO")
        if inv_no_idx >= 0:
            invoice_summary = Part1InvoiceSummary(sno=1)

            # Invoice number is next line
            if inv_no_idx + 1 < len(page_lines):
                inv_no = page_lines[inv_no_idx + 1].get('content', '') if isinstance(page_lines[inv_no_idx + 1], dict) else page_lines[inv_no_idx + 1]
                invoice_summary.invoice_no = str(inv_no).strip()

            # Find INV. AMT
            inv_amt_idx = find_line_index(page_lines, "INV. AMT")
            if inv_amt_idx >= 0 and inv_amt_idx + 1 < len(page_lines):
                inv_amt = page_lines[inv_amt_idx + 1].get('content', '') if isinstance(page_lines[inv_amt_idx + 1], dict) else page_lines[inv_amt_idx + 1]
                invoice_summary.inv_amt = parse_float(inv_amt)

            # Find currency (4.CUR)
            cur_idx = find_line_index(page_lines, "CUR")
            if cur_idx >= 0 and cur_idx + 1 < len(page_lines):
                cur_val = page_lines[cur_idx + 1].get('content', '') if isinstance(page_lines[cur_idx + 1], dict) else page_lines[cur_idx + 1]
                cur_val = str(cur_val).strip()
                # Currency codes are typically 3 letters
                if len(cur_val) == 3 and cur_val.isalpha():
                    invoice_summary.currency = cur_val

            if invoice_summary.invoice_no:
                boe.part1_invoice_summary.append(invoice_summary)

    # Parse Duty Summary - use raw_table from ocr_data if available
    duty_raw = ocr_data.get("part1_duty_summary", {}).get("raw_table", [])
    if duty_raw and len(duty_raw) >= 4:
        # Row 0: headers (BCD, ACD, SWS, NCCD, ADD, CVD, IGST, G.CESS, TOT.ASS VAL)
        # Row 1: values for row 0 headers
        # Row 2: headers (SG, SAED, GSIA, TTA, HEALTH, TOTAL DUTY, INT, PNLTY, FINE, TOT.AMOUNT)
        # Row 3: values for row 2 headers
        row1 = duty_raw[1] if len(duty_raw) > 1 else []
        row3 = duty_raw[3] if len(duty_raw) > 3 else []

        # Parse first row of values (BCD through TOT.ASS VAL)
        boe.part1_duty_summary.bcd = parse_float(row1[1]) if len(row1) > 1 else 0
        boe.part1_duty_summary.acd = parse_float(row1[2]) if len(row1) > 2 else 0
        boe.part1_duty_summary.sws = parse_float(row1[3]) if len(row1) > 3 else 0
        boe.part1_duty_summary.nccd = parse_float(row1[4]) if len(row1) > 4 else 0
        boe.part1_duty_summary.add_duty = parse_float(row1[5]) if len(row1) > 5 else 0
        boe.part1_duty_summary.cvd = parse_float(row1[6]) if len(row1) > 6 else 0
        boe.part1_duty_summary.igst = parse_float(row1[7]) if len(row1) > 7 else 0
        boe.part1_duty_summary.g_cess = parse_float(row1[9]) if len(row1) > 9 else 0
        boe.part1_duty_summary.tot_ass_val = parse_float(row1[10]) if len(row1) > 10 else 0

        # Parse second row of values (SG through TOT.AMOUNT)
        boe.part1_duty_summary.sg = parse_float(row3[1]) if len(row3) > 1 else 0
        boe.part1_duty_summary.saed = parse_float(row3[2]) if len(row3) > 2 else 0
        boe.part1_duty_summary.gsia = parse_float(row3[3]) if len(row3) > 3 else 0
        boe.part1_duty_summary.tta = parse_float(row3[4]) if len(row3) > 4 else 0
        boe.part1_duty_summary.health = parse_float(row3[5]) if len(row3) > 5 else 0
        boe.part1_duty_summary.total_duty = parse_float(row3[6]) if len(row3) > 6 else 0
        boe.part1_duty_summary.interest = parse_float(row3[7]) if len(row3) > 7 else 0
        boe.part1_duty_summary.penalty = parse_float(row3[8]) if len(row3) > 8 else 0
        boe.part1_duty_summary.fine = parse_float(row3[9]) if len(row3) > 9 else 0
        boe.part1_duty_summary.tot_amount = parse_float(row3[10]) if len(row3) > 10 else 0
    else:
        # Fallback to table parsing
        duty_table = find_table_by_headers(tables, ["BCD", "ACD"], page=1)
        if duty_table:
            data = duty_table.get("data", [])
            # Find the row with numeric values
            for row in data:
                values = [parse_float(c) for c in row]
                if sum(values) > 0:
                    # Map values to duty fields based on position
                    if len(values) >= 10:
                        boe.part1_duty_summary.bcd = values[0] if len(values) > 0 else 0
                        boe.part1_duty_summary.acd = values[1] if len(values) > 1 else 0
                        boe.part1_duty_summary.sws = values[2] if len(values) > 2 else 0
                        boe.part1_duty_summary.nccd = values[3] if len(values) > 3 else 0
                        boe.part1_duty_summary.add_duty = values[4] if len(values) > 4 else 0
                        boe.part1_duty_summary.cvd = values[5] if len(values) > 5 else 0
                        boe.part1_duty_summary.igst = values[6] if len(values) > 6 else 0
                        boe.part1_duty_summary.g_cess = values[7] if len(values) > 7 else 0
                        boe.part1_duty_summary.tot_ass_val = values[8] if len(values) > 8 else 0
                        boe.part1_duty_summary.total_duty = values[9] if len(values) > 9 else 0

    # Parse Payment section (F. PAYMENT)
    payment_table = find_table_by_headers(tables, ["SR NO", "CHALLAN"], page=1)
    if payment_table:
        data = payment_table.get("data", [])
        for row in data[1:]:  # Skip header row
            if len(row) >= 4:
                sr_no = parse_int(row[1]) if len(row) > 1 else 0
                if sr_no > 0:
                    payment = Part1Payment(
                        sr_no=sr_no,
                        challan_no=str(row[2] or "").strip() if len(row) > 2 else "",
                        paid_on=str(row[3] or "").strip() if len(row) > 3 else "",
                        amount=parse_float(row[4]) if len(row) > 4 else 0.0,
                    )
                    boe.part1_payments.append(payment)

    # Parse Manifest Details (D. MANIFEST)
    manifest_table = find_table_by_headers(tables, ["IGM NO"], page=1)
    if manifest_table:
        data = manifest_table.get("data", [])
        if len(data) >= 2:
            # Row 1 contains values: IGM NO, IGM DATE, INW DATE, GIGMNO, GIGMDT, MAWB NO, DATE, HAWB NO, DATE, PKG, GW
            row = data[1]
            if len(row) >= 11:
                boe.part1_manifest.igm_no = str(row[1] or "").strip()
                boe.part1_manifest.igm_date = str(row[2] or "").strip()
                boe.part1_manifest.inw_date = str(row[3] or "").strip()
                boe.part1_manifest.gigm_no = str(row[4] or "").strip()
                boe.part1_manifest.gigm_date = str(row[5] or "").strip()
                boe.part1_manifest.mawb_no = str(row[6] or "").strip()
                boe.part1_manifest.mawb_date = str(row[7] or "").strip()
                boe.part1_manifest.hawb_no = str(row[8] or "").strip()
                boe.part1_manifest.hawb_date = str(row[9] or "").strip()
                boe.part1_manifest.pkg = parse_int(row[10]) if len(row) > 10 else 0
                boe.part1_manifest.gross_weight = parse_float(row[11]) if len(row) > 11 else 0.0

    # Parse Part II Items from pages 2-3 (E. ITEM DETAILS)
    # Note: Some tables have CTH in headers, others have empty headers but CTH pattern in data rows
    seen_item_snos = set()  # Deduplicate items
    for table in tables:
        if table.get("page") in [2, 3]:
            headers = table.get("headers", [])
            headers_text = " ".join(str(h) for h in headers if h).upper()
            data = table.get("data", [])

            # Check if this is an item table (CTH in headers or in first few data rows)
            is_item_table = "CTH" in headers_text and "ITEM" in headers_text

            # Also check data rows for CTH pattern (handles tables with empty headers)
            if not is_item_table:
                for row in data[:5]:
                    row_text = " ".join(str(c) for c in row if c).upper()
                    if "2.CTH" in row_text or "S NO" in row_text:
                        is_item_table = True
                        break

            if is_item_table:
                for row in data:
                    if len(row) >= 6:
                        # Check if this is a header row (skip it)
                        row_text = " ".join(str(c) for c in row if c).upper()
                        if "S NO" in row_text or "CTH" in row_text and "DESCRIPTION" in row_text:
                            continue

                        # Serial number is at index 1
                        sno = parse_int(row[1])
                        if sno > 0 and sno not in seen_item_snos:
                            seen_item_snos.add(sno)
                            item = Part2Item(
                                invoice_sno=1,  # Default to invoice 1
                                item_sno=sno,
                                cth=str(row[2] or "").strip(),
                                description=str(row[3] or "").strip()[:500],
                                unit_price=parse_float(row[4]),
                                quantity=parse_float(row[5]),
                                uqc=str(row[6] or "").strip() if len(row) > 6 else "",
                                amount=parse_float(row[7]) if len(row) > 7 else 0.0,
                            )
                            boe.part2_items.append(item)

    # Parse Part III Item Duties from pages 4-13
    # Each "A. ITEM DETAILS" table contains duty info for one item
    # Structure: Row 1=values, Row 3=assess value, Rows 4-9=B. ITEM DUTY, Rows 10-15=C. OTHER DUTIES
    # Note: OCR may detect duplicate tables, so deduplicate by assessed_value
    seen_assessed_values = set()
    item_duty_counter = 0

    for table in tables:
        page = table.get("page", 0)
        if 4 <= page <= 13:
            headers = table.get("headers", [])
            headers_text = " ".join(str(h) for h in headers if h).upper()

            # Look for "A. ITEM DETAILS" tables which contain duty information
            if "A. ITEM DETAILS" in headers_text and "UPI" in headers_text:
                data = table.get("data", [])
                if len(data) >= 9:
                    # Row 1: Item values (UPI, COO, C.QTY, C.UQC, S.QTY, S.UQC, SCH, STND/PR, RSP)
                    row1 = data[1] if len(data) > 1 else []
                    # Row 3: Contains ASSESS VALUE
                    row3 = data[3] if len(data) > 3 else []

                    # Get assessed value for deduplication
                    assessed_value = parse_float(row3[9]) if len(row3) > 9 else 0
                    unit_price = parse_float(row1[1]) if len(row1) > 1 else 0

                    # Create unique key for deduplication
                    dedup_key = f"{assessed_value:.2f}_{unit_price:.4f}"
                    if dedup_key in seen_assessed_values:
                        continue  # Skip duplicate
                    seen_assessed_values.add(dedup_key)

                    item_duty_counter += 1

                    # Row 7: Duty rates (BCD at col 2, SWS at col 4, IGST at col 6)
                    row7 = data[7] if len(data) > 7 else []
                    # Row 8: Duty amounts
                    row8 = data[8] if len(data) > 8 else []

                    duty = Part3ItemDuty(
                        invoice_sno=1,  # Default invoice
                        item_sno=item_duty_counter,
                        unit_price=unit_price,
                        country_origin=str(row1[2] or "").strip() if len(row1) > 2 else "",
                        commercial_qty=parse_float(row1[3]) if len(row1) > 3 else 0,
                        commercial_uqc=str(row1[4] or "").strip() if len(row1) > 4 else "",
                        standard_qty=parse_float(row1[5]) if len(row1) > 5 else 0,
                        standard_uqc=str(row1[6] or "").strip() if len(row1) > 6 else "",
                        scheme_code=str(row1[7] or "").strip() if len(row1) > 7 else "",
                        assessed_value=assessed_value,
                        bcd_rate=parse_float(row7[2]) if len(row7) > 2 else 0,
                        igst_rate=parse_float(row7[6]) if len(row7) > 6 else 0,
                        bcd_amount=parse_float(row8[2]) if len(row8) > 2 else 0,
                        igst_amount=parse_float(row8[6]) if len(row8) > 6 else 0,
                    )

                    # Try to get total_duty from row 8 (T. VALUE column, usually col 9 or 13)
                    if len(row8) > 9:
                        duty.total_duty = parse_float(row8[9])

                    boe.part3_item_duties.append(duty)

    # Parse Part IV Licence Details from page 14
    for table in tables:
        if table.get("page") == 14:
            headers = table.get("headers", [])
            headers_text = " ".join(str(h) for h in headers if h).upper()

            if "LIC" in headers_text:
                data = table.get("data", [])
                for row in data:
                    if len(row) >= 8:
                        inv_sno = parse_int(row[0])
                        if inv_sno > 0:
                            licence = Part4Licence(
                                invoice_sno=inv_sno,
                                item_sno=parse_int(row[1]),
                                lic_slno=parse_int(row[2]),
                                lic_no=str(row[3] or "").strip(),
                                lic_date=str(row[4] or "").strip(),
                                code=str(row[5] or "").strip(),
                                port=str(row[6] or "").strip(),
                                debit_value=parse_float(row[7]),
                            )
                            boe.part4_licences.append(licence)

            # Parse Certificate Details (G. CERTIFICATE)
            if "CERTIFICATE" in headers_text and "NUMBER" in headers_text:
                data = table.get("data", [])
                for row in data[1:]:  # Skip header
                    if len(row) >= 6:
                        cert_num = str(row[2] or "").strip() if len(row) > 2 else ""
                        if cert_num:  # Only add if there's a certificate number
                            cert = Part4Certificate(
                                certificate_number=cert_num,
                                certificate_date=str(row[3] or "").strip() if len(row) > 3 else "",
                                certificate_type=str(row[4] or "").strip() if len(row) > 4 else "",
                                prc_level=str(row[5] or "").strip() if len(row) > 5 else "",
                                iec=str(row[6] or "").strip() if len(row) > 6 else "",
                                branch_slno=str(row[7] or "").strip() if len(row) > 7 else "",
                            )
                            boe.part4_certificates.append(cert)

    # Parse Container Details from page 15 (G. CONTAINER)
    for table in tables:
        if table.get("page") == 15:
            headers = table.get("headers", [])
            headers_text = " ".join(str(h) for h in headers if h).upper()

            if "CONTAINER" in headers_text:
                data = table.get("data", [])
                for row in data[1:]:  # Skip header
                    if len(row) >= 4:
                        container_num = str(row[0] or "").strip()
                        if container_num:  # Only add if there's a container number
                            container = Part1Container(
                                container_number=container_num,
                                truck_number=str(row[1] or "").strip() if len(row) > 1 else "",
                                seal_number=str(row[2] or "").strip() if len(row) > 2 else "",
                                fcl_lcl=str(row[3] or "").strip() if len(row) > 3 else "",
                            )
                            boe.part1_containers.append(container)

    # Parse Part V Compliance (OOC details) from page 16
    for table in tables:
        if table.get("page") in [15, 16]:
            headers = table.get("headers", [])
            data = table.get("data", [])

            # Look for OOC No and Date in the data
            for row in data:
                row_text = " ".join(str(c) for c in row if c).upper()
                if "OOC" in row_text:
                    for i, cell in enumerate(row):
                        cell_str = str(cell or "").strip()
                        if "OOC" in cell_str.upper() and "NO" in cell_str.upper():
                            # Next cell might be the OOC number
                            if i + 1 < len(row):
                                boe.part5_compliance.ooc_no = str(row[i + 1] or "").strip()
                        if "DATE" in cell_str.upper():
                            # Look for date pattern nearby
                            if i + 1 < len(row):
                                date_val = str(row[i + 1] or "").strip()
                                if date_val and any(c.isdigit() for c in date_val):
                                    boe.part5_compliance.ooc_date = date_val

    # Set document ID
    boe.header.document_id = f"BE{boe.header.be_no}" if boe.header.be_no else ""

    # Parse Part1 Processing Details from extracted data
    if "part1_processing" in ocr_data:
        for proc in ocr_data["part1_processing"]:
            if isinstance(proc, dict):
                processing = Part1Processing(
                    event=str(proc.get("event", "")).strip(),
                    event_date=str(proc.get("event_date", "")).strip(),
                    event_time=str(proc.get("event_time", "")).strip(),
                    exchange_rate=str(proc.get("exchange_rate", "")).strip(),
                )
                boe.part1_processing.append(processing)

    # Extract from original OCR header data if available
    if "header" in ocr_data:
        orig_header = ocr_data["header"]
        if not boe.header.port_code and orig_header.get("port_code"):
            boe.header.port_code = orig_header["port_code"]
        if not boe.header.port_name and orig_header.get("port_name"):
            boe.header.port_name = orig_header["port_name"]
        if not boe.header.iec_br and orig_header.get("iec_br"):
            boe.header.iec_br = orig_header["iec_br"]
        if not boe.header.gstin_type and orig_header.get("gstin_type"):
            boe.header.gstin_type = orig_header["gstin_type"]

    return boe


def main():
    """Main function to parse OCR output"""

    output_dir = Path(__file__).parent.parent / "output"

    # Load OCR extracted data
    with open(output_dir / "boe_extracted_data.json") as f:
        ocr_data = json.load(f)

    print("=" * 60)
    print("Parsing Bill of Entry from OCR Output")
    print("=" * 60)

    # Parse into structured format
    boe = parse_ocr_output(ocr_data)

    # Save parsed output
    parsed_output = boe.to_dict()
    parsed_path = output_dir / "boe_parsed_final.json"
    with open(parsed_path, "w") as f:
        json.dump(parsed_output, f, indent=2)

    print(f"\nParsed output saved to: {parsed_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("Parsing Summary")
    print("=" * 60)

    print(f"\nHeader:")
    print(f"  Document ID: {boe.header.document_id}")
    print(f"  Port Code: {boe.header.port_code}")
    print(f"  BE No: {boe.header.be_no}")
    print(f"  BE Date: {boe.header.be_date}")
    print(f"  IEC/Br: {boe.header.iec_br}")
    print(f"  Items: {boe.header.item_count}")

    print(f"\nDuty Summary:")
    print(f"  BCD: {boe.part1_duty_summary.bcd}")
    print(f"  IGST: {boe.part1_duty_summary.igst}")
    print(f"  Total Duty: {boe.part1_duty_summary.total_duty}")
    print(f"  Total Assessed Value: {boe.part1_duty_summary.tot_ass_val}")

    print(f"\nExtracted Records:")
    print(f"  Part I Processing Events: {len(boe.part1_processing)}")
    print(f"  Part II Items: {len(boe.part2_items)}")
    print(f"  Part III Item Duties: {len(boe.part3_item_duties)}")
    print(f"  Part IV Licences: {len(boe.part4_licences)}")

    if boe.part1_processing:
        print(f"\nProcessing Details:")
        for proc in boe.part1_processing:
            print(f"  {proc.event}: {proc.event_date} {proc.event_time} | {proc.exchange_rate}")

    return boe


if __name__ == "__main__":
    main()
