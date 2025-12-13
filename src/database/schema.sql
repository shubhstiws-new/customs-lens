-- Bill of Entry Database Schema
-- Generated from OCR JSON output structure
-- Database: boe (Azure SQL Database)

-- ============================================
-- SCHEMA: header
-- Contains document-level header information
-- ============================================

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'header')
BEGIN
    EXEC('CREATE SCHEMA header')
END
GO

-- Main documents table (one row per Bill of Entry)
IF OBJECT_ID('header.documents', 'U') IS NULL
CREATE TABLE header.documents (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL UNIQUE,
    port_code VARCHAR(20),
    port_name VARCHAR(255),
    be_no VARCHAR(20) NOT NULL,
    be_date DATE,
    be_type VARCHAR(10),
    iec_br VARCHAR(50),
    gstin_type VARCHAR(50),
    cb_code VARCHAR(50),
    inv_count INT DEFAULT 0,
    item_count INT DEFAULT 0,
    cont_count INT DEFAULT 0,
    pkg_count INT DEFAULT 0,
    gross_weight_kgs DECIMAL(12,3),
    ocr_confidence_avg DECIMAL(5,4),
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2,
    INDEX idx_be_no (be_no),
    INDEX idx_be_date (be_date)
);
GO

-- ============================================
-- SCHEMA: part1
-- Part I - Bill of Entry Summary
-- ============================================

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'part1')
BEGIN
    EXEC('CREATE SCHEMA part1')
END
GO

-- Section A: Status
IF OBJECT_ID('part1.status', 'U') IS NULL
CREATE TABLE part1.status (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    be_status VARCHAR(50),
    mode VARCHAR(20),
    def_be VARCHAR(10),
    kacha VARCHAR(10),
    sec_48 VARCHAR(10),
    reimp VARCHAR(10),
    adv_be VARCHAR(20),
    assess VARCHAR(10),
    exam VARCHAR(10),
    hss VARCHAR(10),
    first_check VARCHAR(10),
    prov_final VARCHAR(10),
    country_origin VARCHAR(100),
    country_consignment VARCHAR(100),
    port_loading VARCHAR(100),
    port_shipment VARCHAR(100),
    CONSTRAINT fk_status_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section B: Declarant
IF OBJECT_ID('part1.declarant', 'U') IS NULL
CREATE TABLE part1.declarant (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    importer_name VARCHAR(255),
    importer_address VARCHAR(500),
    cb_name VARCHAR(255),
    aeo VARCHAR(100),
    ucr VARCHAR(100),
    ad_code VARCHAR(20),
    CONSTRAINT fk_declarant_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section C: Duty Summary
IF OBJECT_ID('part1.duty_summary', 'U') IS NULL
CREATE TABLE part1.duty_summary (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    bcd DECIMAL(15,2) DEFAULT 0,
    acd DECIMAL(15,2) DEFAULT 0,
    sws DECIMAL(15,2) DEFAULT 0,
    nccd DECIMAL(15,2) DEFAULT 0,
    add_duty DECIMAL(15,2) DEFAULT 0,
    cvd DECIMAL(15,2) DEFAULT 0,
    igst DECIMAL(15,2) DEFAULT 0,
    g_cess DECIMAL(15,2) DEFAULT 0,
    sg DECIMAL(15,2) DEFAULT 0,
    saed DECIMAL(15,2) DEFAULT 0,
    gsia DECIMAL(15,2) DEFAULT 0,
    tta DECIMAL(15,2) DEFAULT 0,
    health DECIMAL(15,2) DEFAULT 0,
    total_duty DECIMAL(15,2) DEFAULT 0,
    interest DECIMAL(15,2) DEFAULT 0,
    penalty DECIMAL(15,2) DEFAULT 0,
    fine DECIMAL(15,2) DEFAULT 0,
    tot_ass_val DECIMAL(18,2) DEFAULT 0,
    tot_amount DECIMAL(18,2) DEFAULT 0,
    CONSTRAINT fk_duty_summary_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section D: Manifest Details
IF OBJECT_ID('part1.manifest', 'U') IS NULL
CREATE TABLE part1.manifest (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    igm_no VARCHAR(30),
    igm_date DATE,
    inw_date DATE,
    gigm_no VARCHAR(30),
    gigm_date DATE,
    mawb_no VARCHAR(50),
    mawb_date DATE,
    hawb_no VARCHAR(50),
    hawb_date DATE,
    pkg INT DEFAULT 0,
    gross_weight DECIMAL(12,3),
    CONSTRAINT fk_manifest_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section E: Bond Details
IF OBJECT_ID('part1.bond', 'U') IS NULL
CREATE TABLE part1.bond (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    bond_no VARCHAR(30),
    port VARCHAR(20),
    bond_code VARCHAR(10),
    debt_amt DECIMAL(15,2),
    bg_amt DECIMAL(15,2),
    CONSTRAINT fk_bond_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section F: Payment Details
IF OBJECT_ID('part1.payment', 'U') IS NULL
CREATE TABLE part1.payment (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    sr_no INT,
    challan_no VARCHAR(30),
    paid_on DATE,
    amount DECIMAL(15,2),
    CONSTRAINT fk_payment_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section H: Processing Details
IF OBJECT_ID('part1.processing', 'U') IS NULL
CREATE TABLE part1.processing (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    event VARCHAR(50),
    event_date VARCHAR(50),  -- Stored as text to handle various OCR date formats
    event_time VARCHAR(50),  -- Stored as text to handle various OCR time formats
    exchange_rate VARCHAR(50),
    CONSTRAINT fk_processing_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- ============================================
-- SCHEMA: part2
-- Part II - Invoice & Valuation Details
-- ============================================

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'part2')
BEGIN
    EXEC('CREATE SCHEMA part2')
END
GO

-- Invoice header
IF OBJECT_ID('part2.invoice', 'U') IS NULL
CREATE TABLE part2.invoice (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    invoice_sno INT,
    invoice_no VARCHAR(50),
    invoice_date DATE,
    buyer_name VARCHAR(255),
    buyer_address VARCHAR(500),
    seller_name VARCHAR(255),
    seller_address VARCHAR(500),
    supplier_name VARCHAR(255),
    supplier_address VARCHAR(500),
    inv_value DECIMAL(15,2),
    currency VARCHAR(10),
    terms VARCHAR(20),
    valuation_method VARCHAR(100),
    assessed_value DECIMAL(18,2),
    CONSTRAINT fk_invoice_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE,
    INDEX idx_invoice_no (invoice_no)
);
GO

-- Section E: Item Details
IF OBJECT_ID('part2.item', 'U') IS NULL
CREATE TABLE part2.item (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    invoice_sno INT DEFAULT 1,
    item_sno INT NOT NULL,
    cth VARCHAR(20),
    description VARCHAR(500),
    unit_price DECIMAL(15,6),
    quantity DECIMAL(15,6),
    uqc VARCHAR(20),
    amount DECIMAL(15,2),
    CONSTRAINT fk_item_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE,
    INDEX idx_item_cth (cth)
);
GO

-- ============================================
-- SCHEMA: part3
-- Part III - Duties (Item-level)
-- ============================================

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'part3')
BEGIN
    EXEC('CREATE SCHEMA part3')
END
GO

-- Item Duty Details
IF OBJECT_ID('part3.item_duty', 'U') IS NULL
CREATE TABLE part3.item_duty (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    invoice_sno INT,
    item_sno INT NOT NULL,
    cth VARCHAR(20),
    ceth VARCHAR(20),
    description VARCHAR(500),
    unit_price DECIMAL(15,6),
    country_origin VARCHAR(10),
    commercial_qty DECIMAL(15,6),
    commercial_uqc VARCHAR(20),
    standard_qty DECIMAL(15,6),
    standard_uqc VARCHAR(20),
    scheme_code VARCHAR(30),
    assessed_value DECIMAL(18,2),
    total_duty DECIMAL(15,2),
    -- BCD (Basic Customs Duty)
    bcd_notn_no VARCHAR(20),
    bcd_notn_sno VARCHAR(20),
    bcd_rate DECIMAL(8,4),
    bcd_amount DECIMAL(15,2),
    -- IGST
    igst_notn_no VARCHAR(20),
    igst_notn_sno VARCHAR(20),
    igst_rate DECIMAL(8,4),
    igst_amount DECIMAL(15,2),
    -- Other duties
    acd_amount DECIMAL(15,2),
    sws_amount DECIMAL(15,2),
    sad_amount DECIMAL(15,2),
    g_cess_amount DECIMAL(15,2),
    cvd_amount DECIMAL(15,2),
    sg_amount DECIMAL(15,2),
    CONSTRAINT fk_item_duty_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE,
    INDEX idx_item_duty_item (document_id, item_sno)
);
GO

-- ============================================
-- SCHEMA: part4
-- Part IV - Additional Details
-- ============================================

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'part4')
BEGIN
    EXEC('CREATE SCHEMA part4')
END
GO

-- Licence Details
IF OBJECT_ID('part4.licence', 'U') IS NULL
CREATE TABLE part4.licence (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    invoice_sno INT,
    item_sno INT,
    lic_slno INT,
    lic_no VARCHAR(30),
    lic_date DATE,
    code VARCHAR(20),
    port VARCHAR(20),
    debit_value DECIMAL(18,2),
    qty DECIMAL(15,6),
    uqc VARCHAR(20),
    CONSTRAINT fk_licence_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Single Window Declaration
IF OBJECT_ID('part4.sw_declaration', 'U') IS NULL
CREATE TABLE part4.sw_declaration (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    invoice_sno INT,
    item_sno INT,
    info_type VARCHAR(20),
    qualifier VARCHAR(30),
    info_code VARCHAR(30),
    info_text VARCHAR(100),
    info_msr DECIMAL(15,6),
    uqc VARCHAR(20),
    CONSTRAINT fk_sw_declaration_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Supporting Documents
IF OBJECT_ID('part4.supporting_doc', 'U') IS NULL
CREATE TABLE part4.supporting_doc (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    invoice_sno INT,
    item_sno INT,
    doc_type VARCHAR(20),
    icegate_id VARCHAR(50),
    irn VARCHAR(50),
    doc_code VARCHAR(30),
    issue_place VARCHAR(100),
    issue_date DATE,
    exp_date DATE,
    CONSTRAINT fk_supporting_doc_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- ============================================
-- SCHEMA: part5
-- Part V - Compliances
-- ============================================

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'part5')
BEGIN
    EXEC('CREATE SCHEMA part5')
END
GO

IF OBJECT_ID('part5.compliance', 'U') IS NULL
CREATE TABLE part5.compliance (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    examination_order NVARCHAR(MAX),
    examination_instructions NVARCHAR(MAX),
    compulsory_compliance NVARCHAR(MAX),
    ac_remarks NVARCHAR(MAX),
    examination_report NVARCHAR(MAX),
    superintendent_comments NVARCHAR(MAX),
    ooc_no VARCHAR(30),
    ooc_date DATE,
    CONSTRAINT fk_compliance_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- ============================================
-- SCHEMA: reference
-- Reference/Dimension tables
-- ============================================

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'reference')
BEGIN
    EXEC('CREATE SCHEMA reference')
END
GO

-- Glossary terms
IF OBJECT_ID('reference.glossary', 'U') IS NULL
CREATE TABLE reference.glossary (
    id INT IDENTITY(1,1) PRIMARY KEY,
    term VARCHAR(100),
    abbreviation VARCHAR(20),
    definition NVARCHAR(500),
    section VARCHAR(50)
);
GO

-- CTH (Customs Tariff Heading) codes
IF OBJECT_ID('reference.cth_code', 'U') IS NULL
CREATE TABLE reference.cth_code (
    cth VARCHAR(20) PRIMARY KEY,
    description VARCHAR(500),
    chapter VARCHAR(10),
    section VARCHAR(50)
);
GO

-- ============================================
-- SCHEMA: audit
-- Audit and tracking tables
-- ============================================

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'audit')
BEGIN
    EXEC('CREATE SCHEMA audit')
END
GO

-- OCR confidence tracking
IF OBJECT_ID('audit.ocr_confidence', 'U') IS NULL
CREATE TABLE audit.ocr_confidence (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    page_number INT,
    field_name VARCHAR(100),
    extracted_value NVARCHAR(500),
    confidence_score DECIMAL(5,4),
    needs_review BIT DEFAULT 0,
    reviewed_by VARCHAR(100),
    reviewed_at DATETIME2,
    corrected_value NVARCHAR(500),
    CONSTRAINT fk_ocr_confidence_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Processing log
IF OBJECT_ID('audit.processing_log', 'U') IS NULL
CREATE TABLE audit.processing_log (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50),
    action VARCHAR(50),
    status VARCHAR(20),
    message NVARCHAR(1000),
    created_at DATETIME2 DEFAULT GETDATE()
);
GO

PRINT 'Database schema created successfully!'
GO
