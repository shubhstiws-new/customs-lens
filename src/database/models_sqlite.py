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

    # Relationships
    status: Mapped[Optional["Status"]] = relationship(back_populates="document", uselist=False, cascade="all, delete-orphan")
    declarant: Mapped[Optional["Declarant"]] = relationship(back_populates="document", uselist=False, cascade="all, delete-orphan")
    duty_summary: Mapped[Optional["DutySummary"]] = relationship(back_populates="document", uselist=False, cascade="all, delete-orphan")
    manifest: Mapped[Optional["Manifest"]] = relationship(back_populates="document", uselist=False, cascade="all, delete-orphan")
    bond: Mapped[Optional["Bond"]] = relationship(back_populates="document", uselist=False, cascade="all, delete-orphan")
    invoice_summaries: Mapped[List["InvoiceSummary"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    payments: Mapped[List["Payment"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    processing_events: Mapped[List["Processing"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    invoices: Mapped[List["Invoice"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    items: Mapped[List["Item"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    item_duties: Mapped[List["ItemDuty"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    licences: Mapped[List["Licence"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    compliance: Mapped[Optional["Compliance"]] = relationship(back_populates="document", uselist=False, cascade="all, delete-orphan")


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
    compulsory_compliance: Mapped[Optional[str]] = mapped_column(Text)
    ooc_no: Mapped[Optional[str]] = mapped_column(String(30))
    ooc_date: Mapped[Optional[date]] = mapped_column(Date)

    document: Mapped["Document"] = relationship(back_populates="compliance")
