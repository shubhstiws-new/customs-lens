"""
Database Operations Module
Handles insertion and management of BoE data in SQLite/Azure SQL
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError

from src.database.models_sqlite import (
    Base, Document, Status, Declarant, DutySummary, Manifest, Bond, InvoiceSummary,
    Payment, Processing, Invoice, Item, ItemDuty, Licence, Compliance,
    # New Part I tables
    Warehouse, Container,
    # New Part II tables
    TransactingParties, Valuation, CostServices,
    # New Part IV tables
    SVBDetails, PreviousBE, Reimport, Manufacturer, Accessory, Certificate,
    HSSDetails, SWDeclaration, SWConstituent, SWControl, SupportingDoc, Part4Container,
    # New Part VI tables
    Declaration, AuthorizedSignatory
)
from .transformers import parse_date, parse_number, clean_text, safe_int

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BoEDatabaseManager:
    """Manager for Bill of Entry database operations"""

    def __init__(self, db_path: str = "output/boe_local.db"):
        """Initialize database connection"""
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()

    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(self.engine)
        logger.info("Database tables created/verified")

    def document_exists(self, session: Session, document_id: str) -> bool:
        """Check if a document already exists"""
        return session.query(Document).filter(
            Document.document_id == document_id
        ).first() is not None

    def insert_document(self, session: Session, data: Dict[str, Any]) -> Document:
        """Insert main document record"""
        header = data.get("header", {})

        doc = Document(
            document_id=header.get("document_id", ""),
            port_code=clean_text(header.get("port_code")),
            port_name=clean_text(header.get("port_name")),
            be_no=clean_text(header.get("be_no", "")),
            be_date=parse_date(header.get("be_date")),
            be_type=clean_text(header.get("be_type")),
            iec_br=clean_text(header.get("iec_br")),
            gstin_type=clean_text(header.get("gstin_type")),
            cb_code=clean_text(header.get("cb_code")),
            inv_count=safe_int(header.get("inv_count", 0)),
            item_count=safe_int(header.get("item_count", 0)),
            cont_count=safe_int(header.get("cont_count", 0)),
            pkg_count=safe_int(header.get("pkg_count", 0)),
            gross_weight_kgs=parse_number(header.get("gross_weight_kgs")),
        )

        session.add(doc)
        session.flush()  # Get ID
        logger.info(f"Inserted document: {doc.document_id}")
        return doc

    def insert_status(self, session: Session, document_id: str, data: Dict[str, Any]):
        """Insert Part 1 Status data"""
        status_data = data.get("part1_status", {})
        if not any(status_data.values()):  # Skip if all empty
            return

        status = Status(
            document_id=document_id,
            be_status=clean_text(status_data.get("be_status")),
            mode=clean_text(status_data.get("mode")),
            def_be=clean_text(status_data.get("def_be")),
            kacha=clean_text(status_data.get("kacha")),
            sec_48=clean_text(status_data.get("sec_48")),
            reimp=clean_text(status_data.get("reimp")),
            adv_be=clean_text(status_data.get("adv_be")),
            assess=clean_text(status_data.get("assess")),
            exam=clean_text(status_data.get("exam")),
            hss=clean_text(status_data.get("hss")),
            first_check=clean_text(status_data.get("first_check")),
            prov_final=clean_text(status_data.get("prov_final")),
            country_origin=clean_text(status_data.get("country_origin")),
            country_consignment=clean_text(status_data.get("country_consignment")),
            port_loading=clean_text(status_data.get("port_loading")),
            port_shipment=clean_text(status_data.get("port_shipment")),
        )
        session.add(status)
        logger.info(f"Inserted status for: {document_id}")

    def insert_declarant(self, session: Session, document_id: str, data: Dict[str, Any]):
        """Insert Part 1 Declarant data"""
        decl_data = data.get("part1_declarant", {})
        if not any(decl_data.values()):
            return

        declarant = Declarant(
            document_id=document_id,
            importer_name=clean_text(decl_data.get("importer_name")),
            importer_address=clean_text(decl_data.get("importer_address")),
            cb_name=clean_text(decl_data.get("cb_name")),
            aeo=clean_text(decl_data.get("aeo")),
            ucr=clean_text(decl_data.get("ucr")),
            ad_code=clean_text(decl_data.get("ad_code")),
        )
        session.add(declarant)
        logger.info(f"Inserted declarant for: {document_id}")

    def insert_duty_summary(self, session: Session, document_id: str, data: Dict[str, Any]):
        """Insert Part 1 Duty Summary data"""
        duty_data = data.get("part1_duty_summary", {})

        duty_summary = DutySummary(
            document_id=document_id,
            bcd=parse_number(duty_data.get("bcd")) or 0,
            acd=parse_number(duty_data.get("acd")) or 0,
            sws=parse_number(duty_data.get("sws")) or 0,
            nccd=parse_number(duty_data.get("nccd")) or 0,
            add_duty=parse_number(duty_data.get("add_duty")) or 0,
            cvd=parse_number(duty_data.get("cvd")) or 0,
            igst=parse_number(duty_data.get("igst")) or 0,
            g_cess=parse_number(duty_data.get("g_cess")) or 0,
            sg=parse_number(duty_data.get("sg")) or 0,
            saed=parse_number(duty_data.get("saed")) or 0,
            gsia=parse_number(duty_data.get("gsia")) or 0,
            tta=parse_number(duty_data.get("tta")) or 0,
            health=parse_number(duty_data.get("health")) or 0,
            total_duty=parse_number(duty_data.get("total_duty")) or 0,
            interest=parse_number(duty_data.get("interest")) or 0,
            penalty=parse_number(duty_data.get("penalty")) or 0,
            fine=parse_number(duty_data.get("fine")) or 0,
            tot_ass_val=parse_number(duty_data.get("tot_ass_val")) or 0,
            tot_amount=parse_number(duty_data.get("tot_amount")) or 0,
        )
        session.add(duty_summary)
        logger.info(f"Inserted duty summary for: {document_id}")

    def insert_manifest(self, session: Session, document_id: str, data: Dict[str, Any]):
        """Insert Part 1 Manifest data"""
        manifest_data = data.get("part1_manifest", {})

        manifest = Manifest(
            document_id=document_id,
            igm_no=clean_text(manifest_data.get("igm_no")),
            igm_date=parse_date(manifest_data.get("igm_date")),
            inw_date=parse_date(manifest_data.get("inw_date")),
            gigm_no=clean_text(manifest_data.get("gigm_no")),
            gigm_date=parse_date(manifest_data.get("gigm_date")),
            mawb_no=clean_text(manifest_data.get("mawb_no")),
            mawb_date=parse_date(manifest_data.get("mawb_date")),
            hawb_no=clean_text(manifest_data.get("hawb_no")),
            hawb_date=parse_date(manifest_data.get("hawb_date")),
            pkg=safe_int(manifest_data.get("pkg")) or 0,
            gross_weight=parse_number(manifest_data.get("gross_weight")),
        )
        session.add(manifest)
        logger.info(f"Inserted manifest for: {document_id}")

    def insert_bond(self, session: Session, document_id: str, data: Dict[str, Any]):
        """Insert Part 1 Bond data"""
        bond_data = data.get("part1_bond", {})
        if not any(bond_data.values()):
            return

        bond = Bond(
            document_id=document_id,
            bond_no=clean_text(bond_data.get("bond_no")),
            port=clean_text(bond_data.get("port")),
            bond_code=clean_text(bond_data.get("bond_code")),
            debt_amt=parse_number(bond_data.get("debt_amt")),
            bg_amt=parse_number(bond_data.get("bg_amt")),
        )
        session.add(bond)
        logger.info(f"Inserted bond for: {document_id}")

    def insert_invoice_summary(self, session: Session, document_id: str, data: Dict[str, Any]):
        """Insert Part 1 Invoice Summary records"""
        summaries = data.get("part1_invoice_summary", [])
        for sum_data in summaries:
            inv_summary = InvoiceSummary(
                document_id=document_id,
                sno=safe_int(sum_data.get("sno")),
                invoice_no=clean_text(sum_data.get("invoice_no")),
                inv_amt=parse_number(sum_data.get("inv_amt")),
                currency=clean_text(sum_data.get("currency")),
            )
            session.add(inv_summary)

        if summaries:
            logger.info(f"Inserted {len(summaries)} invoice summaries for: {document_id}")

    def insert_payments(self, session: Session, document_id: str, data: Dict[str, Any]):
        """Insert Part 1 Payment records"""
        payments = data.get("part1_payments", [])
        for payment_data in payments:
            payment = Payment(
                document_id=document_id,
                sr_no=safe_int(payment_data.get("sr_no")),
                challan_no=clean_text(payment_data.get("challan_no")),
                paid_on=parse_date(payment_data.get("paid_on")),
                amount=parse_number(payment_data.get("amount")),
            )
            session.add(payment)

        if payments:
            logger.info(f"Inserted {len(payments)} payments for: {document_id}")

    def insert_processing(self, session: Session, document_id: str, data: Dict[str, Any]):
        """Insert Part 1 Processing events"""
        events = data.get("part1_processing", [])
        for event_data in events:
            processing = Processing(
                document_id=document_id,
                event=clean_text(event_data.get("event")),
                event_date=parse_date(event_data.get("event_date")),
                event_time=clean_text(event_data.get("event_time")),
                exchange_rate=clean_text(event_data.get("exchange_rate")),
            )
            session.add(processing)

        if events:
            logger.info(f"Inserted {len(events)} processing events for: {document_id}")

    def insert_invoices(self, session: Session, document_id: str, data: Dict[str, Any]):
        """Insert Part 2 Invoice records"""
        invoices = data.get("part2_invoices", [])
        for inv_data in invoices:
            invoice = Invoice(
                document_id=document_id,
                invoice_sno=safe_int(inv_data.get("invoice_sno")),
                invoice_no=clean_text(inv_data.get("invoice_no")),
                invoice_date=parse_date(inv_data.get("invoice_date")),
                buyer_name=clean_text(inv_data.get("buyer_name")),
                buyer_address=clean_text(inv_data.get("buyer_address")),
                seller_name=clean_text(inv_data.get("seller_name")),
                seller_address=clean_text(inv_data.get("seller_address")),
                supplier_name=clean_text(inv_data.get("supplier_name")),
                supplier_address=clean_text(inv_data.get("supplier_address")),
                inv_value=parse_number(inv_data.get("inv_value")),
                currency=clean_text(inv_data.get("currency")),
                terms=clean_text(inv_data.get("terms")),
                valuation_method=clean_text(inv_data.get("valuation_method")),
                assessed_value=parse_number(inv_data.get("assessed_value")),
            )
            session.add(invoice)

        if invoices:
            logger.info(f"Inserted {len(invoices)} invoices for: {document_id}")

    def insert_items(self, session: Session, document_id: str, data: Dict[str, Any]):
        """Insert Part 2 Item records"""
        items = data.get("part2_items", [])
        for item_data in items:
            item = Item(
                document_id=document_id,
                invoice_sno=safe_int(item_data.get("invoice_sno")) or 1,
                item_sno=safe_int(item_data.get("item_sno")) or 0,
                cth=clean_text(item_data.get("cth")),
                description=clean_text(item_data.get("description")),
                unit_price=parse_number(item_data.get("unit_price")),
                quantity=parse_number(item_data.get("quantity")),
                uqc=clean_text(item_data.get("uqc")),
                amount=parse_number(item_data.get("amount")),
            )
            session.add(item)

        if items:
            logger.info(f"Inserted {len(items)} items for: {document_id}")

    def insert_item_duties(self, session: Session, document_id: str, data: Dict[str, Any]):
        """Insert Part 3 Item Duty records"""
        duties = data.get("part3_item_duties", [])
        for duty_data in duties:
            item_duty = ItemDuty(
                document_id=document_id,
                invoice_sno=safe_int(duty_data.get("invoice_sno")),
                item_sno=safe_int(duty_data.get("item_sno")) or 0,
                cth=clean_text(duty_data.get("cth")),
                ceth=clean_text(duty_data.get("ceth")),
                description=clean_text(duty_data.get("description")),
                unit_price=parse_number(duty_data.get("unit_price")),
                country_origin=clean_text(duty_data.get("country_origin")),
                commercial_qty=parse_number(duty_data.get("commercial_qty")),
                commercial_uqc=clean_text(duty_data.get("commercial_uqc")),
                standard_qty=parse_number(duty_data.get("standard_qty")),
                standard_uqc=clean_text(duty_data.get("standard_uqc")),
                scheme_code=clean_text(duty_data.get("scheme_code")),
                assessed_value=parse_number(duty_data.get("assessed_value")),
                total_duty=parse_number(duty_data.get("total_duty")),
                bcd_notn_no=clean_text(duty_data.get("bcd_notn_no")),
                bcd_notn_sno=clean_text(duty_data.get("bcd_notn_sno")),
                bcd_rate=parse_number(duty_data.get("bcd_rate")),
                bcd_amount=parse_number(duty_data.get("bcd_amount")),
                igst_notn_no=clean_text(duty_data.get("igst_notn_no")),
                igst_notn_sno=clean_text(duty_data.get("igst_notn_sno")),
                igst_rate=parse_number(duty_data.get("igst_rate")),
                igst_amount=parse_number(duty_data.get("igst_amount")),
            )
            session.add(item_duty)

        if duties:
            logger.info(f"Inserted {len(duties)} item duties for: {document_id}")

    def insert_licences(self, session: Session, document_id: str, data: Dict[str, Any]):
        """Insert Part 4 Licence records"""
        licences = data.get("part4_licences", [])
        for lic_data in licences:
            licence = Licence(
                document_id=document_id,
                invoice_sno=safe_int(lic_data.get("invoice_sno")),
                item_sno=safe_int(lic_data.get("item_sno")),
                lic_slno=safe_int(lic_data.get("lic_slno")),
                lic_no=clean_text(lic_data.get("lic_no")),
                lic_date=parse_date(lic_data.get("lic_date")),
                code=clean_text(lic_data.get("code")),
                port=clean_text(lic_data.get("port")),
                debit_value=parse_number(lic_data.get("debit_value")),
                qty=parse_number(lic_data.get("qty")),
                uqc=clean_text(lic_data.get("uqc")),
            )
            session.add(licence)

        if licences:
            logger.info(f"Inserted {len(licences)} licences for: {document_id}")

    def insert_compliance(self, session: Session, document_id: str, data: Dict[str, Any]):
        """Insert Part 5 Compliance data"""
        comp_data = data.get("part5_compliance", {})
        if not any(comp_data.values()):
            return

        compliance = Compliance(
            document_id=document_id,
            examination_order=clean_text(comp_data.get("examination_order")),
            examination_instructions=clean_text(comp_data.get("examination_instructions")),
            pga_instructions=clean_text(comp_data.get("pga_instructions")),
            compulsory_compliance=clean_text(comp_data.get("compulsory_compliance")),
            ac_remarks=clean_text(comp_data.get("ac_remarks")),
            examination_report=clean_text(comp_data.get("examination_report")),
            superintendent_comments=clean_text(comp_data.get("superintendent_comments")),
            ooc_no=clean_text(comp_data.get("ooc_no")),
            ooc_date=parse_date(comp_data.get("ooc_date")),
        )
        session.add(compliance)
        logger.info(f"Inserted compliance for: {document_id}")

    # ========== Part I - Additional Sections ==========

    def insert_warehouse(self, session: Session, document_id: str, data: Dict[str, Any]):
        """Insert Part 1 Warehouse data"""
        wh_data = data.get("part1_warehouse", {})
        if not any(wh_data.values()):
            return

        warehouse = Warehouse(
            document_id=document_id,
            wh_code=clean_text(wh_data.get("wh_code")),
            wh_name=clean_text(wh_data.get("wh_name")),
            wh_address=clean_text(wh_data.get("wh_address")),
            wbe_no=clean_text(wh_data.get("wbe_no")),
            wbe_date=parse_date(wh_data.get("wbe_date")),
            wbe_site=clean_text(wh_data.get("wbe_site")),
        )
        session.add(warehouse)
        logger.info(f"Inserted warehouse for: {document_id}")

    def insert_containers(self, session: Session, document_id: str, data: Dict[str, Any]):
        """Insert Part 1 Container records"""
        containers = data.get("part1_containers", [])
        for cont_data in containers:
            container = Container(
                document_id=document_id,
                sno=safe_int(cont_data.get("sno")),
                container_no=clean_text(cont_data.get("container_no")),
                seal_no=clean_text(cont_data.get("seal_no")),
                container_size=clean_text(cont_data.get("container_size")),
                container_type=clean_text(cont_data.get("container_type")),
                fcl_lcl=clean_text(cont_data.get("fcl_lcl")),
            )
            session.add(container)

        if containers:
            logger.info(f"Inserted {len(containers)} containers for: {document_id}")

    # ========== Part II - Additional Sections ==========

    def insert_transacting_parties(self, session: Session, document_id: str, data: Dict[str, Any]):
        """Insert Part 2 Transacting Parties records"""
        parties = data.get("part2_transacting_parties", [])
        for party_data in parties:
            party = TransactingParties(
                document_id=document_id,
                invoice_sno=safe_int(party_data.get("invoice_sno")),
                buyer_name=clean_text(party_data.get("buyer_name")),
                buyer_address=clean_text(party_data.get("buyer_address")),
                seller_name=clean_text(party_data.get("seller_name")),
                seller_address=clean_text(party_data.get("seller_address")),
                supplier_name=clean_text(party_data.get("supplier_name")),
                supplier_address=clean_text(party_data.get("supplier_address")),
                third_party_name=clean_text(party_data.get("third_party_name")),
                third_party_address=clean_text(party_data.get("third_party_address")),
            )
            session.add(party)

        if parties:
            logger.info(f"Inserted {len(parties)} transacting parties for: {document_id}")

    def insert_valuations(self, session: Session, document_id: str, data: Dict[str, Any]):
        """Insert Part 2 Valuation records"""
        valuations = data.get("part2_valuations", [])
        for val_data in valuations:
            valuation = Valuation(
                document_id=document_id,
                invoice_sno=safe_int(val_data.get("invoice_sno")),
                valuation_method=clean_text(val_data.get("valuation_method")),
                related=clean_text(val_data.get("related")),
                svb_ch=clean_text(val_data.get("svb_ch")),
                svb_no=clean_text(val_data.get("svb_no")),
                svb_date=parse_date(val_data.get("svb_date")),
                loa=clean_text(val_data.get("loa")),
            )
            session.add(valuation)

        if valuations:
            logger.info(f"Inserted {len(valuations)} valuations for: {document_id}")

    def insert_cost_services(self, session: Session, document_id: str, data: Dict[str, Any]):
        """Insert Part 2 Cost & Services records"""
        costs = data.get("part2_cost_services", [])
        for cost_data in costs:
            cost = CostServices(
                document_id=document_id,
                invoice_sno=safe_int(cost_data.get("invoice_sno")),
                freight=parse_number(cost_data.get("freight")),
                insurance=parse_number(cost_data.get("insurance")),
                loading=parse_number(cost_data.get("loading")),
                commission=parse_number(cost_data.get("commission")),
                misc_charge=parse_number(cost_data.get("misc_charge")),
                pay_terms=clean_text(cost_data.get("pay_terms")),
                hss=clean_text(cost_data.get("hss")),
                assessed_value=parse_number(cost_data.get("assessed_value")),
            )
            session.add(cost)

        if costs:
            logger.info(f"Inserted {len(costs)} cost services for: {document_id}")

    # ========== Part IV - Additional Sections ==========

    def insert_svb_details(self, session: Session, document_id: str, data: Dict[str, Any]):
        """Insert Part 4 SVB Details records"""
        svbs = data.get("part4_svb_details", [])
        for svb_data in svbs:
            svb = SVBDetails(
                document_id=document_id,
                invoice_sno=safe_int(svb_data.get("invoice_sno")),
                item_sno=safe_int(svb_data.get("item_sno")),
                svb_no=clean_text(svb_data.get("svb_no")),
                svb_date=parse_date(svb_data.get("svb_date")),
                svb_load_on_duty=parse_number(svb_data.get("svb_load_on_duty")),
                svb_load_on_value=parse_number(svb_data.get("svb_load_on_value")),
            )
            session.add(svb)

        if svbs:
            logger.info(f"Inserted {len(svbs)} SVB details for: {document_id}")

    def insert_previous_bes(self, session: Session, document_id: str, data: Dict[str, Any]):
        """Insert Part 4 Previous BE records"""
        prev_bes = data.get("part4_previous_bes", [])
        for prev_data in prev_bes:
            prev_be = PreviousBE(
                document_id=document_id,
                invoice_sno=safe_int(prev_data.get("invoice_sno")),
                item_sno=safe_int(prev_data.get("item_sno")),
                prev_be_no=clean_text(prev_data.get("prev_be_no")),
                prev_be_date=parse_date(prev_data.get("prev_be_date")),
                prev_port=clean_text(prev_data.get("prev_port")),
                prev_qty=parse_number(prev_data.get("prev_qty")),
                prev_uqc=clean_text(prev_data.get("prev_uqc")),
            )
            session.add(prev_be)

        if prev_bes:
            logger.info(f"Inserted {len(prev_bes)} previous BEs for: {document_id}")

    def insert_reimports(self, session: Session, document_id: str, data: Dict[str, Any]):
        """Insert Part 4 Reimport records"""
        reimports = data.get("part4_reimports", [])
        for reimp_data in reimports:
            reimport = Reimport(
                document_id=document_id,
                invoice_sno=safe_int(reimp_data.get("invoice_sno")),
                item_sno=safe_int(reimp_data.get("item_sno")),
                sb_no=clean_text(reimp_data.get("sb_no")),
                sb_date=parse_date(reimp_data.get("sb_date")),
                sb_port=clean_text(reimp_data.get("sb_port")),
                export_qty=parse_number(reimp_data.get("export_qty")),
                export_uqc=clean_text(reimp_data.get("export_uqc")),
            )
            session.add(reimport)

        if reimports:
            logger.info(f"Inserted {len(reimports)} reimports for: {document_id}")

    def insert_manufacturers(self, session: Session, document_id: str, data: Dict[str, Any]):
        """Insert Part 4 Manufacturer records"""
        manufacturers = data.get("part4_manufacturers", [])
        for mfr_data in manufacturers:
            manufacturer = Manufacturer(
                document_id=document_id,
                invoice_sno=safe_int(mfr_data.get("invoice_sno")),
                item_sno=safe_int(mfr_data.get("item_sno")),
                manufacturer_name=clean_text(mfr_data.get("manufacturer_name")),
                manufacturer_address=clean_text(mfr_data.get("manufacturer_address")),
                manufacturer_country=clean_text(mfr_data.get("manufacturer_country")),
            )
            session.add(manufacturer)

        if manufacturers:
            logger.info(f"Inserted {len(manufacturers)} manufacturers for: {document_id}")

    def insert_accessories(self, session: Session, document_id: str, data: Dict[str, Any]):
        """Insert Part 4 Accessory records"""
        accessories = data.get("part4_accessories", [])
        for acc_data in accessories:
            accessory = Accessory(
                document_id=document_id,
                invoice_sno=safe_int(acc_data.get("invoice_sno")),
                item_sno=safe_int(acc_data.get("item_sno")),
                accessory_type=clean_text(acc_data.get("accessory_type")),
                accessory_desc=clean_text(acc_data.get("accessory_desc")),
                accessory_value=parse_number(acc_data.get("accessory_value")),
            )
            session.add(accessory)

        if accessories:
            logger.info(f"Inserted {len(accessories)} accessories for: {document_id}")

    def insert_certificates(self, session: Session, document_id: str, data: Dict[str, Any]):
        """Insert Part 4 Certificate records"""
        certificates = data.get("part4_certificates", [])
        for cert_data in certificates:
            certificate = Certificate(
                document_id=document_id,
                invoice_sno=safe_int(cert_data.get("invoice_sno")),
                item_sno=safe_int(cert_data.get("item_sno")),
                cert_type=clean_text(cert_data.get("cert_type")),
                cert_no=clean_text(cert_data.get("cert_no")),
                cert_date=parse_date(cert_data.get("cert_date")),
                issuing_authority=clean_text(cert_data.get("issuing_authority")),
            )
            session.add(certificate)

        if certificates:
            logger.info(f"Inserted {len(certificates)} certificates for: {document_id}")

    def insert_hss_details(self, session: Session, document_id: str, data: Dict[str, Any]):
        """Insert Part 4 HSS Details records"""
        hss_list = data.get("part4_hss_details", [])
        for hss_data in hss_list:
            hss = HSSDetails(
                document_id=document_id,
                invoice_sno=safe_int(hss_data.get("invoice_sno")),
                item_sno=safe_int(hss_data.get("item_sno")),
                hss_code=clean_text(hss_data.get("hss_code")),
                hss_desc=clean_text(hss_data.get("hss_desc")),
                hss_qty=parse_number(hss_data.get("hss_qty")),
                hss_uqc=clean_text(hss_data.get("hss_uqc")),
            )
            session.add(hss)

        if hss_list:
            logger.info(f"Inserted {len(hss_list)} HSS details for: {document_id}")

    def insert_sw_declarations(self, session: Session, document_id: str, data: Dict[str, Any]):
        """Insert Part 4 SW Declaration records"""
        sw_decls = data.get("part4_sw_declarations", [])
        for sw_data in sw_decls:
            sw_decl = SWDeclaration(
                document_id=document_id,
                invoice_sno=safe_int(sw_data.get("invoice_sno")),
                item_sno=safe_int(sw_data.get("item_sno")),
                info_type=clean_text(sw_data.get("info_type")),
                qualifier=clean_text(sw_data.get("qualifier")),
                info_code=clean_text(sw_data.get("info_code")),
                info_text=clean_text(sw_data.get("info_text")),
                info_msr=parse_number(sw_data.get("info_msr")),
                uqc=clean_text(sw_data.get("uqc")),
            )
            session.add(sw_decl)

        if sw_decls:
            logger.info(f"Inserted {len(sw_decls)} SW declarations for: {document_id}")

    def insert_sw_constituents(self, session: Session, document_id: str, data: Dict[str, Any]):
        """Insert Part 4 SW Constituent records"""
        constituents = data.get("part4_sw_constituents", [])
        for const_data in constituents:
            constituent = SWConstituent(
                document_id=document_id,
                invoice_sno=safe_int(const_data.get("invoice_sno")),
                item_sno=safe_int(const_data.get("item_sno")),
                constituent_code=clean_text(const_data.get("constituent_code")),
                constituent_name=clean_text(const_data.get("constituent_name")),
                constituent_pct=parse_number(const_data.get("constituent_pct")),
            )
            session.add(constituent)

        if constituents:
            logger.info(f"Inserted {len(constituents)} SW constituents for: {document_id}")

    def insert_sw_controls(self, session: Session, document_id: str, data: Dict[str, Any]):
        """Insert Part 4 SW Control records"""
        controls = data.get("part4_sw_controls", [])
        for ctrl_data in controls:
            control = SWControl(
                document_id=document_id,
                invoice_sno=safe_int(ctrl_data.get("invoice_sno")),
                item_sno=safe_int(ctrl_data.get("item_sno")),
                control_code=clean_text(ctrl_data.get("control_code")),
                control_value=clean_text(ctrl_data.get("control_value")),
            )
            session.add(control)

        if controls:
            logger.info(f"Inserted {len(controls)} SW controls for: {document_id}")

    def insert_supporting_docs(self, session: Session, document_id: str, data: Dict[str, Any]):
        """Insert Part 4 Supporting Document records"""
        docs = data.get("part4_supporting_docs", [])
        for doc_data in docs:
            supporting_doc = SupportingDoc(
                document_id=document_id,
                invoice_sno=safe_int(doc_data.get("invoice_sno")),
                item_sno=safe_int(doc_data.get("item_sno")),
                doc_type=clean_text(doc_data.get("doc_type")),
                doc_no=clean_text(doc_data.get("doc_no")),
                doc_date=parse_date(doc_data.get("doc_date")),
                icegate_id=clean_text(doc_data.get("icegate_id")),
                irn=clean_text(doc_data.get("irn")),
            )
            session.add(supporting_doc)

        if docs:
            logger.info(f"Inserted {len(docs)} supporting docs for: {document_id}")

    def insert_part4_containers(self, session: Session, document_id: str, data: Dict[str, Any]):
        """Insert Part 4 Container records"""
        containers = data.get("part4_containers", [])
        for cont_data in containers:
            container = Part4Container(
                document_id=document_id,
                invoice_sno=safe_int(cont_data.get("invoice_sno")),
                item_sno=safe_int(cont_data.get("item_sno")),
                container_no=clean_text(cont_data.get("container_no")),
                seal_no=clean_text(cont_data.get("seal_no")),
            )
            session.add(container)

        if containers:
            logger.info(f"Inserted {len(containers)} Part4 containers for: {document_id}")

    # ========== Part VI - Declaration ==========

    def insert_declaration(self, session: Session, document_id: str, data: Dict[str, Any]):
        """Insert Part 6 Declaration data"""
        decl_data = data.get("part6_declaration", {})
        if not any(decl_data.values()):
            return

        declaration = Declaration(
            document_id=document_id,
            declaration_text=clean_text(decl_data.get("declaration_text")),
            declaration_date=parse_date(decl_data.get("declaration_date")),
            declaration_place=clean_text(decl_data.get("declaration_place")),
        )
        session.add(declaration)
        logger.info(f"Inserted declaration for: {document_id}")

    def insert_signatory(self, session: Session, document_id: str, data: Dict[str, Any]):
        """Insert Part 6 Authorized Signatory data"""
        sig_data = data.get("part6_signatory", {})
        if not any(sig_data.values()):
            return

        signatory = AuthorizedSignatory(
            document_id=document_id,
            signatory_name=clean_text(sig_data.get("signatory_name")),
            signatory_designation=clean_text(sig_data.get("signatory_designation")),
            signatory_date=parse_date(sig_data.get("signatory_date")),
        )
        session.add(signatory)
        logger.info(f"Inserted signatory for: {document_id}")

    def insert_full_document(self, data: Dict[str, Any], skip_existing: bool = True) -> bool:
        """
        Insert a complete Bill of Entry document with all related records

        Args:
            data: Parsed JSON data from OCR
            skip_existing: If True, skip if document already exists

        Returns:
            True if inserted successfully, False otherwise
        """
        session = self.get_session()
        document_id = data.get("header", {}).get("document_id", "")

        try:
            # Check if exists
            if skip_existing and self.document_exists(session, document_id):
                logger.warning(f"Document {document_id} already exists, skipping")
                return False

            # Insert all components - Part I
            doc = self.insert_document(session, data)
            self.insert_status(session, document_id, data)
            self.insert_declarant(session, document_id, data)
            self.insert_duty_summary(session, document_id, data)
            self.insert_manifest(session, document_id, data)
            self.insert_bond(session, document_id, data)
            self.insert_warehouse(session, document_id, data)
            self.insert_invoice_summary(session, document_id, data)
            self.insert_containers(session, document_id, data)
            self.insert_payments(session, document_id, data)
            self.insert_processing(session, document_id, data)

            # Part II
            self.insert_invoices(session, document_id, data)
            self.insert_items(session, document_id, data)
            self.insert_transacting_parties(session, document_id, data)
            self.insert_valuations(session, document_id, data)
            self.insert_cost_services(session, document_id, data)

            # Part III
            self.insert_item_duties(session, document_id, data)

            # Part IV
            self.insert_licences(session, document_id, data)
            self.insert_svb_details(session, document_id, data)
            self.insert_previous_bes(session, document_id, data)
            self.insert_reimports(session, document_id, data)
            self.insert_manufacturers(session, document_id, data)
            self.insert_accessories(session, document_id, data)
            self.insert_certificates(session, document_id, data)
            self.insert_hss_details(session, document_id, data)
            self.insert_sw_declarations(session, document_id, data)
            self.insert_sw_constituents(session, document_id, data)
            self.insert_sw_controls(session, document_id, data)
            self.insert_supporting_docs(session, document_id, data)
            self.insert_part4_containers(session, document_id, data)

            # Part V
            self.insert_compliance(session, document_id, data)

            # Part VI
            self.insert_declaration(session, document_id, data)
            self.insert_signatory(session, document_id, data)

            # Commit transaction
            session.commit()
            logger.info(f"Successfully inserted document: {document_id}")
            return True

        except IntegrityError as e:
            session.rollback()
            logger.error(f"Integrity error inserting {document_id}: {e}")
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error inserting {document_id}: {e}")
            raise
        finally:
            session.close()

    def delete_document(self, document_id: str) -> bool:
        """Delete a document and all related records"""
        session = self.get_session()
        try:
            doc = session.query(Document).filter(
                Document.document_id == document_id
            ).first()

            if doc:
                session.delete(doc)  # Cascade will handle related records
                session.commit()
                logger.info(f"Deleted document: {document_id}")
                return True

            logger.warning(f"Document not found: {document_id}")
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting {document_id}: {e}")
            return False
        finally:
            session.close()

    def get_document_summary(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of document data"""
        session = self.get_session()
        try:
            doc = session.query(Document).filter(
                Document.document_id == document_id
            ).first()

            if not doc:
                return None

            return {
                "document_id": doc.document_id,
                "be_no": doc.be_no,
                "be_date": str(doc.be_date) if doc.be_date else None,
                "port_code": doc.port_code,
                "port_name": doc.port_name,
                "inv_count": doc.inv_count,
                "item_count": doc.item_count,
                "has_duty_summary": doc.duty_summary is not None,
                "has_manifest": doc.manifest is not None,
                "licence_count": len(doc.licences) if doc.licences else 0,
            }
        finally:
            session.close()


def insert_boe_from_json(json_data: Dict[str, Any], db_path: str = "output/boe_local.db") -> bool:
    """
    Convenience function to insert BoE data from JSON

    Args:
        json_data: Parsed JSON data from OCR
        db_path: Path to SQLite database

    Returns:
        True if successful, False otherwise
    """
    manager = BoEDatabaseManager(db_path)
    manager.create_tables()
    return manager.insert_full_document(json_data)
