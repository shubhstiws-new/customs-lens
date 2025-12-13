"""
SQLAlchemy ORM Models for Bill of Entry Database
Based on OCR-extracted JSON structure
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


# ============================================
# Header Schema
# ============================================

class Document(Base):
    """Main documents table - one row per Bill of Entry"""
    __tablename__ = "documents"
    __table_args__ = {"schema": "header"}

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
    gross_weight_kgs: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 3))
    ocr_confidence_avg: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    status: Mapped[Optional["Status"]] = relationship(back_populates="document", uselist=False, cascade="all, delete-orphan")
    declarant: Mapped[Optional["Declarant"]] = relationship(back_populates="document", uselist=False, cascade="all, delete-orphan")
    duty_summary: Mapped[Optional["DutySummary"]] = relationship(back_populates="document", uselist=False, cascade="all, delete-orphan")
    manifest: Mapped[Optional["Manifest"]] = relationship(back_populates="document", uselist=False, cascade="all, delete-orphan")
    bond: Mapped[Optional["Bond"]] = relationship(back_populates="document", uselist=False, cascade="all, delete-orphan")
    payments: Mapped[List["Payment"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    processing_events: Mapped[List["Processing"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    invoices: Mapped[List["Invoice"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    items: Mapped[List["Item"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    item_duties: Mapped[List["ItemDuty"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    licences: Mapped[List["Licence"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    sw_declarations: Mapped[List["SWDeclaration"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    supporting_docs: Mapped[List["SupportingDoc"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    compliance: Mapped[Optional["Compliance"]] = relationship(back_populates="document", uselist=False, cascade="all, delete-orphan")


# ============================================
# Part 1 Schema
# ============================================

class Status(Base):
    """Part I - Section A: Status"""
    __tablename__ = "status"
    __table_args__ = {"schema": "part1"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("header.documents.document_id", ondelete="CASCADE"))
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
    __tablename__ = "declarant"
    __table_args__ = {"schema": "part1"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("header.documents.document_id", ondelete="CASCADE"))
    importer_name: Mapped[Optional[str]] = mapped_column(String(255))
    importer_address: Mapped[Optional[str]] = mapped_column(String(500))
    cb_name: Mapped[Optional[str]] = mapped_column(String(255))
    aeo: Mapped[Optional[str]] = mapped_column(String(100))
    ucr: Mapped[Optional[str]] = mapped_column(String(100))
    ad_code: Mapped[Optional[str]] = mapped_column(String(20))

    document: Mapped["Document"] = relationship(back_populates="declarant")


class DutySummary(Base):
    """Part I - Section C: Duty Summary"""
    __tablename__ = "duty_summary"
    __table_args__ = {"schema": "part1"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("header.documents.document_id", ondelete="CASCADE"))
    bcd: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    acd: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    sws: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    nccd: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    add_duty: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    cvd: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    igst: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    g_cess: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    sg: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    saed: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    gsia: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    tta: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    health: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    total_duty: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    interest: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    penalty: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    fine: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    tot_ass_val: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    tot_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)

    document: Mapped["Document"] = relationship(back_populates="duty_summary")


class Manifest(Base):
    """Part I - Section D: Manifest Details"""
    __tablename__ = "manifest"
    __table_args__ = {"schema": "part1"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("header.documents.document_id", ondelete="CASCADE"))
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
    gross_weight: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 3))

    document: Mapped["Document"] = relationship(back_populates="manifest")


class Bond(Base):
    """Part I - Section E: Bond Details"""
    __tablename__ = "bond"
    __table_args__ = {"schema": "part1"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("header.documents.document_id", ondelete="CASCADE"))
    bond_no: Mapped[Optional[str]] = mapped_column(String(30))
    port: Mapped[Optional[str]] = mapped_column(String(20))
    bond_code: Mapped[Optional[str]] = mapped_column(String(10))
    debt_amt: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    bg_amt: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))

    document: Mapped["Document"] = relationship(back_populates="bond")


class Payment(Base):
    """Part I - Section F: Payment Details"""
    __tablename__ = "payment"
    __table_args__ = {"schema": "part1"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("header.documents.document_id", ondelete="CASCADE"))
    sr_no: Mapped[Optional[int]] = mapped_column(Integer)
    challan_no: Mapped[Optional[str]] = mapped_column(String(30))
    paid_on: Mapped[Optional[date]] = mapped_column(Date)
    amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))

    document: Mapped["Document"] = relationship(back_populates="payments")


class Processing(Base):
    """Part I - Section H: Processing Details"""
    __tablename__ = "processing"
    __table_args__ = {"schema": "part1"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("header.documents.document_id", ondelete="CASCADE"))
    event: Mapped[Optional[str]] = mapped_column(String(50))
    event_date: Mapped[Optional[date]] = mapped_column(Date)
    event_time: Mapped[Optional[time]] = mapped_column(Time)
    exchange_rate: Mapped[Optional[str]] = mapped_column(String(50))

    document: Mapped["Document"] = relationship(back_populates="processing_events")


# ============================================
# Part 2 Schema
# ============================================

class Invoice(Base):
    """Part II - Invoice Details"""
    __tablename__ = "invoice"
    __table_args__ = {"schema": "part2"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("header.documents.document_id", ondelete="CASCADE"))
    invoice_sno: Mapped[Optional[int]] = mapped_column(Integer)
    invoice_no: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    invoice_date: Mapped[Optional[date]] = mapped_column(Date)
    buyer_name: Mapped[Optional[str]] = mapped_column(String(255))
    buyer_address: Mapped[Optional[str]] = mapped_column(String(500))
    seller_name: Mapped[Optional[str]] = mapped_column(String(255))
    seller_address: Mapped[Optional[str]] = mapped_column(String(500))
    supplier_name: Mapped[Optional[str]] = mapped_column(String(255))
    supplier_address: Mapped[Optional[str]] = mapped_column(String(500))
    inv_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    currency: Mapped[Optional[str]] = mapped_column(String(10))
    terms: Mapped[Optional[str]] = mapped_column(String(20))
    valuation_method: Mapped[Optional[str]] = mapped_column(String(100))
    assessed_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))

    document: Mapped["Document"] = relationship(back_populates="invoices")


class Item(Base):
    """Part II - Section E: Item Details"""
    __tablename__ = "item"
    __table_args__ = {"schema": "part2"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("header.documents.document_id", ondelete="CASCADE"))
    invoice_sno: Mapped[int] = mapped_column(Integer, default=1)
    item_sno: Mapped[int] = mapped_column(Integer, nullable=False)
    cth: Mapped[Optional[str]] = mapped_column(String(20), index=True)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    unit_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 6))
    quantity: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 6))
    uqc: Mapped[Optional[str]] = mapped_column(String(20))
    amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))

    document: Mapped["Document"] = relationship(back_populates="items")


# ============================================
# Part 3 Schema
# ============================================

class ItemDuty(Base):
    """Part III - Item Duty Details"""
    __tablename__ = "item_duty"
    __table_args__ = (
        Index("idx_item_duty_item", "document_id", "item_sno"),
        {"schema": "part3"}
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("header.documents.document_id", ondelete="CASCADE"))
    invoice_sno: Mapped[Optional[int]] = mapped_column(Integer)
    item_sno: Mapped[int] = mapped_column(Integer, nullable=False)
    cth: Mapped[Optional[str]] = mapped_column(String(20))
    ceth: Mapped[Optional[str]] = mapped_column(String(20))
    description: Mapped[Optional[str]] = mapped_column(String(500))
    unit_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 6))
    country_origin: Mapped[Optional[str]] = mapped_column(String(10))
    commercial_qty: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 6))
    commercial_uqc: Mapped[Optional[str]] = mapped_column(String(20))
    standard_qty: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 6))
    standard_uqc: Mapped[Optional[str]] = mapped_column(String(20))
    scheme_code: Mapped[Optional[str]] = mapped_column(String(30))
    assessed_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))
    total_duty: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    bcd_notn_no: Mapped[Optional[str]] = mapped_column(String(20))
    bcd_notn_sno: Mapped[Optional[str]] = mapped_column(String(20))
    bcd_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4))
    bcd_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    igst_notn_no: Mapped[Optional[str]] = mapped_column(String(20))
    igst_notn_sno: Mapped[Optional[str]] = mapped_column(String(20))
    igst_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4))
    igst_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    acd_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    sws_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    sad_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    g_cess_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    cvd_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    sg_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))

    document: Mapped["Document"] = relationship(back_populates="item_duties")


# ============================================
# Part 4 Schema
# ============================================

class Licence(Base):
    """Part IV - Licence Details"""
    __tablename__ = "licence"
    __table_args__ = {"schema": "part4"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("header.documents.document_id", ondelete="CASCADE"))
    invoice_sno: Mapped[Optional[int]] = mapped_column(Integer)
    item_sno: Mapped[Optional[int]] = mapped_column(Integer)
    lic_slno: Mapped[Optional[int]] = mapped_column(Integer)
    lic_no: Mapped[Optional[str]] = mapped_column(String(30))
    lic_date: Mapped[Optional[date]] = mapped_column(Date)
    code: Mapped[Optional[str]] = mapped_column(String(20))
    port: Mapped[Optional[str]] = mapped_column(String(20))
    debit_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))
    qty: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 6))
    uqc: Mapped[Optional[str]] = mapped_column(String(20))

    document: Mapped["Document"] = relationship(back_populates="licences")


class SWDeclaration(Base):
    """Part IV - Single Window Declaration"""
    __tablename__ = "sw_declaration"
    __table_args__ = {"schema": "part4"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("header.documents.document_id", ondelete="CASCADE"))
    invoice_sno: Mapped[Optional[int]] = mapped_column(Integer)
    item_sno: Mapped[Optional[int]] = mapped_column(Integer)
    info_type: Mapped[Optional[str]] = mapped_column(String(20))
    qualifier: Mapped[Optional[str]] = mapped_column(String(30))
    info_code: Mapped[Optional[str]] = mapped_column(String(30))
    info_text: Mapped[Optional[str]] = mapped_column(String(100))
    info_msr: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 6))
    uqc: Mapped[Optional[str]] = mapped_column(String(20))

    document: Mapped["Document"] = relationship(back_populates="sw_declarations")


class SupportingDoc(Base):
    """Part IV - Supporting Documents"""
    __tablename__ = "supporting_doc"
    __table_args__ = {"schema": "part4"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("header.documents.document_id", ondelete="CASCADE"))
    invoice_sno: Mapped[Optional[int]] = mapped_column(Integer)
    item_sno: Mapped[Optional[int]] = mapped_column(Integer)
    doc_type: Mapped[Optional[str]] = mapped_column(String(20))
    icegate_id: Mapped[Optional[str]] = mapped_column(String(50))
    irn: Mapped[Optional[str]] = mapped_column(String(50))
    doc_code: Mapped[Optional[str]] = mapped_column(String(30))
    issue_place: Mapped[Optional[str]] = mapped_column(String(100))
    issue_date: Mapped[Optional[date]] = mapped_column(Date)
    exp_date: Mapped[Optional[date]] = mapped_column(Date)

    document: Mapped["Document"] = relationship(back_populates="supporting_docs")


# ============================================
# Part 5 Schema
# ============================================

class Compliance(Base):
    """Part V - Compliance Details"""
    __tablename__ = "compliance"
    __table_args__ = {"schema": "part5"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("header.documents.document_id", ondelete="CASCADE"))
    examination_order: Mapped[Optional[str]] = mapped_column(Text)
    examination_instructions: Mapped[Optional[str]] = mapped_column(Text)
    compulsory_compliance: Mapped[Optional[str]] = mapped_column(Text)
    ac_remarks: Mapped[Optional[str]] = mapped_column(Text)
    examination_report: Mapped[Optional[str]] = mapped_column(Text)
    superintendent_comments: Mapped[Optional[str]] = mapped_column(Text)
    ooc_no: Mapped[Optional[str]] = mapped_column(String(30))
    ooc_date: Mapped[Optional[date]] = mapped_column(Date)

    document: Mapped["Document"] = relationship(back_populates="compliance")
