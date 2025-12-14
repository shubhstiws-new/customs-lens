"""
SQLAlchemy ORM Models for SQLite (Local Testing)
No schema prefixes - SQLite doesn't support schemas
"""

from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import (
    String, Integer, Float, Date, Time, DateTime, Text, Boolean,
    ForeignKey, Index, Numeric, create_engine
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship
)


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


class Document(Base):
    """Main documents table - one row per Bill of Entry"""
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    port_code: Mapped[Optional[str]] = mapped_column(String(20))
    port_name: Mapped[Optional[str]] = mapped_column(String(255))
    be_no: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    be_date: Mapped[Optional[date]] = mapped_column(Date, index=True)
    be_type: Mapped[Optional[str]] = mapped_column(String(10))
    iec_br: Mapped[Optional[str]] = mapped_column(String(50))
    gstin_type: Mapped[Optional[str]] = mapped_column(String(50))
    cb_code: Mapped[Optional[str]] = mapped_column(String(50))
    inv_count: Mapped[int] = mapped_column(Integer, default=0)
    item_count: Mapped[int] = mapped_column(Integer, default=0)
    cont_count: Mapped[int] = mapped_column(Integer, default=0)
    pkg_count: Mapped[int] = mapped_column(Integer, default=0)
    gross_weight_kgs: Mapped[Optional[float]] = mapped_column(Float)
    ocr_confidence_avg: Mapped[Optional[float]] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=datetime.utcnow)

    # Relationships - Part I
    status: Mapped[Optional["Status"]] = relationship(back_populates="document", uselist=False, cascade="all, delete-orphan")
    declarant: Mapped[Optional["Declarant"]] = relationship(back_populates="document", uselist=False, cascade="all, delete-orphan")
    duty_summary: Mapped[Optional["DutySummary"]] = relationship(back_populates="document", uselist=False, cascade="all, delete-orphan")
    manifest: Mapped[Optional["Manifest"]] = relationship(back_populates="document", uselist=False, cascade="all, delete-orphan")
    bond: Mapped[Optional["Bond"]] = relationship(back_populates="document", uselist=False, cascade="all, delete-orphan")
    warehouse: Mapped[Optional["Warehouse"]] = relationship(back_populates="document", uselist=False, cascade="all, delete-orphan")
    invoice_summaries: Mapped[List["InvoiceSummary"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    containers: Mapped[List["Container"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    payments: Mapped[List["Payment"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    processing_events: Mapped[List["Processing"]] = relationship(back_populates="document", cascade="all, delete-orphan")

    # Relationships - Part II
    invoices: Mapped[List["Invoice"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    items: Mapped[List["Item"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    transacting_parties: Mapped[List["TransactingParties"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    valuations: Mapped[List["Valuation"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    cost_services: Mapped[List["CostServices"]] = relationship(back_populates="document", cascade="all, delete-orphan")

    # Relationships - Part III
    item_duties: Mapped[List["ItemDuty"]] = relationship(back_populates="document", cascade="all, delete-orphan")

    # Relationships - Part IV
    licences: Mapped[List["Licence"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    svb_details: Mapped[List["SVBDetails"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    previous_bes: Mapped[List["PreviousBE"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    reimports: Mapped[List["Reimport"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    manufacturers: Mapped[List["Manufacturer"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    accessories: Mapped[List["Accessory"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    certificates: Mapped[List["Certificate"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    hss_details: Mapped[List["HSSDetails"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    sw_declarations: Mapped[List["SWDeclaration"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    sw_constituents: Mapped[List["SWConstituent"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    sw_controls: Mapped[List["SWControl"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    supporting_docs: Mapped[List["SupportingDoc"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    part4_containers: Mapped[List["Part4Container"]] = relationship(back_populates="document", cascade="all, delete-orphan")

    # Relationships - Part V
    compliance: Mapped[Optional["Compliance"]] = relationship(back_populates="document", uselist=False, cascade="all, delete-orphan")

    # Relationships - Part VI
    declaration: Mapped[Optional["Declaration"]] = relationship(back_populates="document", uselist=False, cascade="all, delete-orphan")
    signatory: Mapped[Optional["AuthorizedSignatory"]] = relationship(back_populates="document", uselist=False, cascade="all, delete-orphan")


class Status(Base):
    """Part I - Section A: Status"""
    __tablename__ = "part1_status"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"))
    be_status: Mapped[Optional[str]] = mapped_column(String(50))
    mode: Mapped[Optional[str]] = mapped_column(String(20))
    def_be: Mapped[Optional[str]] = mapped_column(String(10))
    kacha: Mapped[Optional[str]] = mapped_column(String(10))
    sec_48: Mapped[Optional[str]] = mapped_column(String(10))
    reimp: Mapped[Optional[str]] = mapped_column(String(10))
    adv_be: Mapped[Optional[str]] = mapped_column(String(20))
    assess: Mapped[Optional[str]] = mapped_column(String(10))
    exam: Mapped[Optional[str]] = mapped_column(String(10))
    hss: Mapped[Optional[str]] = mapped_column(String(10))
    first_check: Mapped[Optional[str]] = mapped_column(String(10))
    prov_final: Mapped[Optional[str]] = mapped_column(String(10))
    country_origin: Mapped[Optional[str]] = mapped_column(String(100))
    country_consignment: Mapped[Optional[str]] = mapped_column(String(100))
    port_loading: Mapped[Optional[str]] = mapped_column(String(100))
    port_shipment: Mapped[Optional[str]] = mapped_column(String(100))

    document: Mapped["Document"] = relationship(back_populates="status")


class Declarant(Base):
    """Part I - Section B: Declarant"""
    __tablename__ = "part1_declarant"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"))
    importer_name: Mapped[Optional[str]] = mapped_column(String(255))
    importer_address: Mapped[Optional[str]] = mapped_column(String(500))
    cb_name: Mapped[Optional[str]] = mapped_column(String(255))
    aeo: Mapped[Optional[str]] = mapped_column(String(100))
    ucr: Mapped[Optional[str]] = mapped_column(String(100))
    ad_code: Mapped[Optional[str]] = mapped_column(String(20))

    document: Mapped["Document"] = relationship(back_populates="declarant")


class DutySummary(Base):
    """Part I - Section C: Duty Summary"""
    __tablename__ = "part1_duty_summary"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"))
    bcd: Mapped[float] = mapped_column(Float, default=0)
    acd: Mapped[float] = mapped_column(Float, default=0)
    sws: Mapped[float] = mapped_column(Float, default=0)
    nccd: Mapped[float] = mapped_column(Float, default=0)
    add_duty: Mapped[float] = mapped_column(Float, default=0)
    cvd: Mapped[float] = mapped_column(Float, default=0)
    igst: Mapped[float] = mapped_column(Float, default=0)
    g_cess: Mapped[float] = mapped_column(Float, default=0)
    sg: Mapped[float] = mapped_column(Float, default=0)
    saed: Mapped[float] = mapped_column(Float, default=0)
    gsia: Mapped[float] = mapped_column(Float, default=0)
    tta: Mapped[float] = mapped_column(Float, default=0)
    health: Mapped[float] = mapped_column(Float, default=0)
    total_duty: Mapped[float] = mapped_column(Float, default=0)
    interest: Mapped[float] = mapped_column(Float, default=0)
    penalty: Mapped[float] = mapped_column(Float, default=0)
    fine: Mapped[float] = mapped_column(Float, default=0)
    tot_ass_val: Mapped[float] = mapped_column(Float, default=0)
    tot_amount: Mapped[float] = mapped_column(Float, default=0)

    document: Mapped["Document"] = relationship(back_populates="duty_summary")


class Manifest(Base):
    """Part I - Section D: Manifest Details"""
    __tablename__ = "part1_manifest"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"))
    igm_no: Mapped[Optional[str]] = mapped_column(String(30))
    igm_date: Mapped[Optional[date]] = mapped_column(Date)
    inw_date: Mapped[Optional[date]] = mapped_column(Date)
    gigm_no: Mapped[Optional[str]] = mapped_column(String(30))
    gigm_date: Mapped[Optional[date]] = mapped_column(Date)
    mawb_no: Mapped[Optional[str]] = mapped_column(String(50))
    mawb_date: Mapped[Optional[date]] = mapped_column(Date)
    hawb_no: Mapped[Optional[str]] = mapped_column(String(50))
    hawb_date: Mapped[Optional[date]] = mapped_column(Date)
    pkg: Mapped[int] = mapped_column(Integer, default=0)
    gross_weight: Mapped[Optional[float]] = mapped_column(Float)

    document: Mapped["Document"] = relationship(back_populates="manifest")


class Payment(Base):
    """Part I - Section F: Payment Details"""
    __tablename__ = "part1_payment"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"))
    sr_no: Mapped[Optional[int]] = mapped_column(Integer)
    challan_no: Mapped[Optional[str]] = mapped_column(String(30))
    paid_on: Mapped[Optional[date]] = mapped_column(Date)
    amount: Mapped[Optional[float]] = mapped_column(Float)

    document: Mapped["Document"] = relationship(back_populates="payments")


class Bond(Base):
    """Part I - Section E: Bond Details"""
    __tablename__ = "part1_bond"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"))
    bond_no: Mapped[Optional[str]] = mapped_column(String(30))
    port: Mapped[Optional[str]] = mapped_column(String(20))
    bond_code: Mapped[Optional[str]] = mapped_column(String(10))
    debt_amt: Mapped[Optional[float]] = mapped_column(Float)
    bg_amt: Mapped[Optional[float]] = mapped_column(Float)

    document: Mapped["Document"] = relationship(back_populates="bond")


class InvoiceSummary(Base):
    """Part I - Section I: Invoice Details Summary"""
    __tablename__ = "part1_invoice_summary"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"))
    sno: Mapped[Optional[int]] = mapped_column(Integer)
    invoice_no: Mapped[Optional[str]] = mapped_column(String(50))
    inv_amt: Mapped[Optional[float]] = mapped_column(Float)
    currency: Mapped[Optional[str]] = mapped_column(String(10))

    document: Mapped["Document"] = relationship(back_populates="invoice_summaries")


class Processing(Base):
    """Part I - Section H: Processing Details"""
    __tablename__ = "part1_processing"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"))
    event: Mapped[Optional[str]] = mapped_column(String(50))
    event_date: Mapped[Optional[date]] = mapped_column(Date)
    event_time: Mapped[Optional[str]] = mapped_column(String(20))
    exchange_rate: Mapped[Optional[str]] = mapped_column(String(50))

    document: Mapped["Document"] = relationship(back_populates="processing_events")


class Invoice(Base):
    """Part II - Invoice Details"""
    __tablename__ = "part2_invoice"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"))
    invoice_sno: Mapped[Optional[int]] = mapped_column(Integer)
    invoice_no: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    invoice_date: Mapped[Optional[date]] = mapped_column(Date)
    buyer_name: Mapped[Optional[str]] = mapped_column(String(255))
    buyer_address: Mapped[Optional[str]] = mapped_column(String(500))
    seller_name: Mapped[Optional[str]] = mapped_column(String(255))
    seller_address: Mapped[Optional[str]] = mapped_column(String(500))
    supplier_name: Mapped[Optional[str]] = mapped_column(String(255))
    supplier_address: Mapped[Optional[str]] = mapped_column(String(500))
    inv_value: Mapped[Optional[float]] = mapped_column(Float)
    currency: Mapped[Optional[str]] = mapped_column(String(10))
    terms: Mapped[Optional[str]] = mapped_column(String(20))
    valuation_method: Mapped[Optional[str]] = mapped_column(String(100))
    assessed_value: Mapped[Optional[float]] = mapped_column(Float)

    document: Mapped["Document"] = relationship(back_populates="invoices")


class Item(Base):
    """Part II - Section E: Item Details"""
    __tablename__ = "part2_item"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"))
    invoice_sno: Mapped[int] = mapped_column(Integer, default=1)
    item_sno: Mapped[int] = mapped_column(Integer, nullable=False)
    cth: Mapped[Optional[str]] = mapped_column(String(20), index=True)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    unit_price: Mapped[Optional[float]] = mapped_column(Float)
    quantity: Mapped[Optional[float]] = mapped_column(Float)
    uqc: Mapped[Optional[str]] = mapped_column(String(20))
    amount: Mapped[Optional[float]] = mapped_column(Float)

    document: Mapped["Document"] = relationship(back_populates="items")


class ItemDuty(Base):
    """Part III - Item Duty Details"""
    __tablename__ = "part3_item_duty"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"))
    invoice_sno: Mapped[Optional[int]] = mapped_column(Integer)
    item_sno: Mapped[int] = mapped_column(Integer, nullable=False)
    cth: Mapped[Optional[str]] = mapped_column(String(20))
    ceth: Mapped[Optional[str]] = mapped_column(String(20))
    description: Mapped[Optional[str]] = mapped_column(String(500))
    unit_price: Mapped[Optional[float]] = mapped_column(Float)
    country_origin: Mapped[Optional[str]] = mapped_column(String(10))
    commercial_qty: Mapped[Optional[float]] = mapped_column(Float)
    commercial_uqc: Mapped[Optional[str]] = mapped_column(String(20))
    standard_qty: Mapped[Optional[float]] = mapped_column(Float)
    standard_uqc: Mapped[Optional[str]] = mapped_column(String(20))
    scheme_code: Mapped[Optional[str]] = mapped_column(String(30))
    assessed_value: Mapped[Optional[float]] = mapped_column(Float)
    total_duty: Mapped[Optional[float]] = mapped_column(Float)
    bcd_notn_no: Mapped[Optional[str]] = mapped_column(String(20))
    bcd_notn_sno: Mapped[Optional[str]] = mapped_column(String(20))
    bcd_rate: Mapped[Optional[float]] = mapped_column(Float)
    bcd_amount: Mapped[Optional[float]] = mapped_column(Float)
    igst_notn_no: Mapped[Optional[str]] = mapped_column(String(20))
    igst_notn_sno: Mapped[Optional[str]] = mapped_column(String(20))
    igst_rate: Mapped[Optional[float]] = mapped_column(Float)
    igst_amount: Mapped[Optional[float]] = mapped_column(Float)

    document: Mapped["Document"] = relationship(back_populates="item_duties")


class Licence(Base):
    """Part IV - Licence Details"""
    __tablename__ = "part4_licence"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"))
    invoice_sno: Mapped[Optional[int]] = mapped_column(Integer)
    item_sno: Mapped[Optional[int]] = mapped_column(Integer)
    lic_slno: Mapped[Optional[int]] = mapped_column(Integer)
    lic_no: Mapped[Optional[str]] = mapped_column(String(30))
    lic_date: Mapped[Optional[date]] = mapped_column(Date)
    code: Mapped[Optional[str]] = mapped_column(String(20))
    port: Mapped[Optional[str]] = mapped_column(String(20))
    debit_value: Mapped[Optional[float]] = mapped_column(Float)
    qty: Mapped[Optional[float]] = mapped_column(Float)
    uqc: Mapped[Optional[str]] = mapped_column(String(20))

    document: Mapped["Document"] = relationship(back_populates="licences")


class Compliance(Base):
    """Part V - Compliance Details"""
    __tablename__ = "part5_compliance"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"))
    examination_order: Mapped[Optional[str]] = mapped_column(Text)
    examination_instructions: Mapped[Optional[str]] = mapped_column(Text)
    pga_instructions: Mapped[Optional[str]] = mapped_column(Text)
    compulsory_compliance: Mapped[Optional[str]] = mapped_column(Text)
    ac_remarks: Mapped[Optional[str]] = mapped_column(Text)
    examination_report: Mapped[Optional[str]] = mapped_column(Text)
    superintendent_comments: Mapped[Optional[str]] = mapped_column(Text)
    ooc_no: Mapped[Optional[str]] = mapped_column(String(30))
    ooc_date: Mapped[Optional[date]] = mapped_column(Date)

    document: Mapped["Document"] = relationship(back_populates="compliance")


# ============== Part I - Additional Sections ==============

class Warehouse(Base):
    """Part I - Section G: Warehouse Details"""
    __tablename__ = "part1_warehouse"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"))
    wh_code: Mapped[Optional[str]] = mapped_column(String(20))
    wh_name: Mapped[Optional[str]] = mapped_column(String(255))
    wh_address: Mapped[Optional[str]] = mapped_column(String(500))
    wbe_no: Mapped[Optional[str]] = mapped_column(String(30))
    wbe_date: Mapped[Optional[date]] = mapped_column(Date)
    wbe_site: Mapped[Optional[str]] = mapped_column(String(50))

    document: Mapped["Document"] = relationship(back_populates="warehouse")


class Container(Base):
    """Part I - Section J: Container Details"""
    __tablename__ = "part1_container"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"))
    sno: Mapped[Optional[int]] = mapped_column(Integer)
    container_no: Mapped[Optional[str]] = mapped_column(String(20))
    seal_no: Mapped[Optional[str]] = mapped_column(String(30))
    container_size: Mapped[Optional[str]] = mapped_column(String(10))
    container_type: Mapped[Optional[str]] = mapped_column(String(20))
    fcl_lcl: Mapped[Optional[str]] = mapped_column(String(10))

    document: Mapped["Document"] = relationship(back_populates="containers")


# ============== Part II - Additional Sections ==============

class TransactingParties(Base):
    """Part II - Section B: Transacting Parties"""
    __tablename__ = "part2_transacting_parties"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"))
    invoice_sno: Mapped[Optional[int]] = mapped_column(Integer)
    buyer_name: Mapped[Optional[str]] = mapped_column(String(255))
    buyer_address: Mapped[Optional[str]] = mapped_column(String(500))
    seller_name: Mapped[Optional[str]] = mapped_column(String(255))
    seller_address: Mapped[Optional[str]] = mapped_column(String(500))
    supplier_name: Mapped[Optional[str]] = mapped_column(String(255))
    supplier_address: Mapped[Optional[str]] = mapped_column(String(500))
    third_party_name: Mapped[Optional[str]] = mapped_column(String(255))
    third_party_address: Mapped[Optional[str]] = mapped_column(String(500))

    document: Mapped["Document"] = relationship(back_populates="transacting_parties")


class Valuation(Base):
    """Part II - Section C: Valuation"""
    __tablename__ = "part2_valuation"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"))
    invoice_sno: Mapped[Optional[int]] = mapped_column(Integer)
    valuation_method: Mapped[Optional[str]] = mapped_column(String(100))
    related: Mapped[Optional[str]] = mapped_column(String(10))
    svb_ch: Mapped[Optional[str]] = mapped_column(String(10))
    svb_no: Mapped[Optional[str]] = mapped_column(String(30))
    svb_date: Mapped[Optional[date]] = mapped_column(Date)
    loa: Mapped[Optional[str]] = mapped_column(String(10))

    document: Mapped["Document"] = relationship(back_populates="valuations")


class CostServices(Base):
    """Part II - Section D: Cost & Services"""
    __tablename__ = "part2_cost_services"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"))
    invoice_sno: Mapped[Optional[int]] = mapped_column(Integer)
    freight: Mapped[Optional[float]] = mapped_column(Float)
    insurance: Mapped[Optional[float]] = mapped_column(Float)
    loading: Mapped[Optional[float]] = mapped_column(Float)
    commission: Mapped[Optional[float]] = mapped_column(Float)
    misc_charge: Mapped[Optional[float]] = mapped_column(Float)
    pay_terms: Mapped[Optional[str]] = mapped_column(String(50))
    hss: Mapped[Optional[str]] = mapped_column(String(20))
    assessed_value: Mapped[Optional[float]] = mapped_column(Float)

    document: Mapped["Document"] = relationship(back_populates="cost_services")


# ============== Part IV - Additional Sections ==============

class SVBDetails(Base):
    """Part IV - Section A: SVB Details"""
    __tablename__ = "part4_svb"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"))
    invoice_sno: Mapped[Optional[int]] = mapped_column(Integer)
    item_sno: Mapped[Optional[int]] = mapped_column(Integer)
    svb_no: Mapped[Optional[str]] = mapped_column(String(30))
    svb_date: Mapped[Optional[date]] = mapped_column(Date)
    svb_load_on_duty: Mapped[Optional[float]] = mapped_column(Float)
    svb_load_on_value: Mapped[Optional[float]] = mapped_column(Float)

    document: Mapped["Document"] = relationship(back_populates="svb_details")


class PreviousBE(Base):
    """Part IV - Section B: Previous BEs"""
    __tablename__ = "part4_previous_be"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"))
    invoice_sno: Mapped[Optional[int]] = mapped_column(Integer)
    item_sno: Mapped[Optional[int]] = mapped_column(Integer)
    prev_be_no: Mapped[Optional[str]] = mapped_column(String(30))
    prev_be_date: Mapped[Optional[date]] = mapped_column(Date)
    prev_port: Mapped[Optional[str]] = mapped_column(String(20))
    prev_qty: Mapped[Optional[float]] = mapped_column(Float)
    prev_uqc: Mapped[Optional[str]] = mapped_column(String(20))

    document: Mapped["Document"] = relationship(back_populates="previous_bes")


class Reimport(Base):
    """Part IV - Section C: Re-import After Export"""
    __tablename__ = "part4_reimport"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"))
    invoice_sno: Mapped[Optional[int]] = mapped_column(Integer)
    item_sno: Mapped[Optional[int]] = mapped_column(Integer)
    sb_no: Mapped[Optional[str]] = mapped_column(String(30))
    sb_date: Mapped[Optional[date]] = mapped_column(Date)
    sb_port: Mapped[Optional[str]] = mapped_column(String(20))
    export_qty: Mapped[Optional[float]] = mapped_column(Float)
    export_uqc: Mapped[Optional[str]] = mapped_column(String(20))

    document: Mapped["Document"] = relationship(back_populates="reimports")


class Manufacturer(Base):
    """Part IV - Section D: Manufacturer Details"""
    __tablename__ = "part4_manufacturer"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"))
    invoice_sno: Mapped[Optional[int]] = mapped_column(Integer)
    item_sno: Mapped[Optional[int]] = mapped_column(Integer)
    manufacturer_name: Mapped[Optional[str]] = mapped_column(String(255))
    manufacturer_address: Mapped[Optional[str]] = mapped_column(String(500))
    manufacturer_country: Mapped[Optional[str]] = mapped_column(String(50))

    document: Mapped["Document"] = relationship(back_populates="manufacturers")


class Accessory(Base):
    """Part IV - Section E: Accessory Status"""
    __tablename__ = "part4_accessory"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"))
    invoice_sno: Mapped[Optional[int]] = mapped_column(Integer)
    item_sno: Mapped[Optional[int]] = mapped_column(Integer)
    accessory_type: Mapped[Optional[str]] = mapped_column(String(50))
    accessory_desc: Mapped[Optional[str]] = mapped_column(String(255))
    accessory_value: Mapped[Optional[float]] = mapped_column(Float)

    document: Mapped["Document"] = relationship(back_populates="accessories")


class Certificate(Base):
    """Part IV - Section G: Certificate Details"""
    __tablename__ = "part4_certificate"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"))
    invoice_sno: Mapped[Optional[int]] = mapped_column(Integer)
    item_sno: Mapped[Optional[int]] = mapped_column(Integer)
    cert_type: Mapped[Optional[str]] = mapped_column(String(50))
    cert_no: Mapped[Optional[str]] = mapped_column(String(50))
    cert_date: Mapped[Optional[date]] = mapped_column(Date)
    issuing_authority: Mapped[Optional[str]] = mapped_column(String(255))

    document: Mapped["Document"] = relationship(back_populates="certificates")


class HSSDetails(Base):
    """Part IV - Section H: HSS Details"""
    __tablename__ = "part4_hss"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"))
    invoice_sno: Mapped[Optional[int]] = mapped_column(Integer)
    item_sno: Mapped[Optional[int]] = mapped_column(Integer)
    hss_code: Mapped[Optional[str]] = mapped_column(String(20))
    hss_desc: Mapped[Optional[str]] = mapped_column(String(255))
    hss_qty: Mapped[Optional[float]] = mapped_column(Float)
    hss_uqc: Mapped[Optional[str]] = mapped_column(String(20))

    document: Mapped["Document"] = relationship(back_populates="hss_details")


class SWDeclaration(Base):
    """Part IV - Section I: Single Window Declaration"""
    __tablename__ = "part4_sw_declaration"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"))
    invoice_sno: Mapped[Optional[int]] = mapped_column(Integer)
    item_sno: Mapped[Optional[int]] = mapped_column(Integer)
    info_type: Mapped[Optional[str]] = mapped_column(String(20))
    qualifier: Mapped[Optional[str]] = mapped_column(String(30))
    info_code: Mapped[Optional[str]] = mapped_column(String(30))
    info_text: Mapped[Optional[str]] = mapped_column(String(255))
    info_msr: Mapped[Optional[float]] = mapped_column(Float)
    uqc: Mapped[Optional[str]] = mapped_column(String(20))

    document: Mapped["Document"] = relationship(back_populates="sw_declarations")


class SWConstituent(Base):
    """Part IV - Section J: SW Constituents"""
    __tablename__ = "part4_sw_constituent"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"))
    invoice_sno: Mapped[Optional[int]] = mapped_column(Integer)
    item_sno: Mapped[Optional[int]] = mapped_column(Integer)
    constituent_code: Mapped[Optional[str]] = mapped_column(String(30))
    constituent_name: Mapped[Optional[str]] = mapped_column(String(100))
    constituent_pct: Mapped[Optional[float]] = mapped_column(Float)

    document: Mapped["Document"] = relationship(back_populates="sw_constituents")


class SWControl(Base):
    """Part IV - Section K: SW Control"""
    __tablename__ = "part4_sw_control"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"))
    invoice_sno: Mapped[Optional[int]] = mapped_column(Integer)
    item_sno: Mapped[Optional[int]] = mapped_column(Integer)
    control_code: Mapped[Optional[str]] = mapped_column(String(30))
    control_value: Mapped[Optional[str]] = mapped_column(String(100))

    document: Mapped["Document"] = relationship(back_populates="sw_controls")


class SupportingDoc(Base):
    """Part IV - Section L: Supporting Documents"""
    __tablename__ = "part4_supporting_doc"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"))
    invoice_sno: Mapped[Optional[int]] = mapped_column(Integer)
    item_sno: Mapped[Optional[int]] = mapped_column(Integer)
    doc_type: Mapped[Optional[str]] = mapped_column(String(30))
    doc_no: Mapped[Optional[str]] = mapped_column(String(50))
    doc_date: Mapped[Optional[date]] = mapped_column(Date)
    icegate_id: Mapped[Optional[str]] = mapped_column(String(50))
    irn: Mapped[Optional[str]] = mapped_column(String(50))

    document: Mapped["Document"] = relationship(back_populates="supporting_docs")


class Part4Container(Base):
    """Part IV - Section M: Container Details"""
    __tablename__ = "part4_container"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"))
    invoice_sno: Mapped[Optional[int]] = mapped_column(Integer)
    item_sno: Mapped[Optional[int]] = mapped_column(Integer)
    container_no: Mapped[Optional[str]] = mapped_column(String(20))
    seal_no: Mapped[Optional[str]] = mapped_column(String(30))

    document: Mapped["Document"] = relationship(back_populates="part4_containers")


# ============== Part VI - Declaration ==============

class Declaration(Base):
    """Part VI - Section A: Declaration Statement"""
    __tablename__ = "part6_declaration"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"))
    declaration_text: Mapped[Optional[str]] = mapped_column(Text)
    declaration_date: Mapped[Optional[date]] = mapped_column(Date)
    declaration_place: Mapped[Optional[str]] = mapped_column(String(100))

    document: Mapped["Document"] = relationship(back_populates="declaration")


class AuthorizedSignatory(Base):
    """Part VI - Section B: Authorized Signatory"""
    __tablename__ = "part6_signatory"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.document_id", ondelete="CASCADE"))
    signatory_name: Mapped[Optional[str]] = mapped_column(String(255))
    signatory_designation: Mapped[Optional[str]] = mapped_column(String(100))
    signatory_date: Mapped[Optional[date]] = mapped_column(Date)

    document: Mapped["Document"] = relationship(back_populates="signatory")
