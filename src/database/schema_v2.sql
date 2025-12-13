-- Bill of Entry Database Schema v2
-- Complete schema based on comprehensive PDF analysis (2025-12-12)
-- Naming convention: {part}_{section_letter}_{section_name}

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
-- Based on PDF header: Port Code, BE No, BE Date, BE Type, IEC/Br, GSTIN/TYPE, CB CODE, etc.
IF OBJECT_ID('header.documents', 'U') IS NULL
CREATE TABLE header.documents (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL UNIQUE,
    -- Header fields (top of every page)
    port_code VARCHAR(20),
    port_name VARCHAR(255),
    be_no VARCHAR(20) NOT NULL,
    be_date DATE,
    be_type VARCHAR(10),
    iec_br VARCHAR(50),
    gstin_type VARCHAR(50),
    cb_code VARCHAR(50),
    -- Counts
    inv_count INT DEFAULT 0,      -- TYPE Nos INV
    item_count INT DEFAULT 0,     -- TYPE Nos ITEM
    cont_count INT DEFAULT 0,     -- TYPE Nos CONT
    pkg_count INT DEFAULT 0,      -- PKG
    gross_weight_kgs DECIMAL(12,3), -- G.WT (KGS)
    -- Metadata
    ocr_confidence_avg DECIMAL(5,4),
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2,
    INDEX idx_be_no (be_no),
    INDEX idx_be_date (be_date)
);
GO

-- ============================================
-- SCHEMA: part1
-- PART I - BILL OF ENTRY SUMMARY (Page 1)
-- ============================================

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'part1')
BEGIN
    EXEC('CREATE SCHEMA part1')
END
GO

-- Section A: STATUS
-- Fields: 1.BE STATUS, 2.MODE, 3.DEF BE, 4.KACHA, 5.SEC 48, 6.REIMP,
--         7.ADV BE (Y/N/P), 8.ASSESS, 9.EXAM, 10.HSS, 11.FIRST CHECK, 12.PROV/FINAL
--         13.COUNTRY OF ORIGIN, 14.COUNTRY OF CONSIGNMENT, 15.PORT OF LOADING, 16.PORT OF SHIPMENT
IF OBJECT_ID('part1.a_status', 'U') IS NULL
CREATE TABLE part1.a_status (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    be_status VARCHAR(50),            -- 1.BE STATUS (e.g., "OOC COPY")
    mode VARCHAR(20),                 -- 2.MODE (e.g., "Air")
    def_be VARCHAR(10),               -- 3.DEF BE (e.g., "T")
    kacha VARCHAR(10),                -- 4.KACHA (e.g., "N")
    sec_48 VARCHAR(10),               -- 5.SEC 48 (e.g., "N")
    reimp VARCHAR(10),                -- 6.REIMP (e.g., "N")
    adv_be VARCHAR(20),               -- 7.ADV BE (Y/N/P)
    assess VARCHAR(10),               -- 8.ASSESS (e.g., "N")
    exam VARCHAR(10),                 -- 9.EXAM (e.g., "N")
    hss VARCHAR(10),                  -- 10.HSS (e.g., "N")
    first_check VARCHAR(10),          -- 11.FIRST CHECK (e.g., "N")
    prov_final VARCHAR(10),           -- 12.PROV/FINAL (e.g., "F")
    country_origin VARCHAR(100),      -- 13.COUNTRY OF ORIGIN (e.g., "ITALY")
    country_consignment VARCHAR(100), -- 14.COUNTRY OF CONSIGNMENT (e.g., "ITALY")
    port_loading VARCHAR(100),        -- 15.PORT OF LOADING (e.g., "MILAN")
    port_shipment VARCHAR(100),       -- 16.PORT OF SHIPMENT (e.g., "MILAN")
    CONSTRAINT fk_a_status_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section B: DECLARANT
-- Fields: 1.IMPORTER NAME & ADDRESS, 2.CB NAME, 3.AEO, 4.UCR, AD CODE
IF OBJECT_ID('part1.b_declarant', 'U') IS NULL
CREATE TABLE part1.b_declarant (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    importer_name VARCHAR(255),       -- 1.IMPORTER NAME
    importer_address VARCHAR(500),    -- 1.IMPORTER ADDRESS
    cb_name VARCHAR(255),             -- 2.CB NAME (e.g., "CORE LOGISTICS")
    aeo VARCHAR(100),                 -- 3.AEO
    ucr VARCHAR(100),                 -- 4.UCR
    ad_code VARCHAR(20),              -- AD CODE (e.g., "0004046")
    CONSTRAINT fk_b_declarant_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section C: DUTY SUMMARY
-- Fields: 1.BCD, 2.ACD, 3.SWS, 4.NCCD, 5.ADD, 6.CVD, 7.IGST, 8.G.CESS,
--         9.SG, 10.SAED, 11.GSIA, 12.TTA, 13.HEALTH, 14.TOTAL DUTY, 15.INT, 16.PNLTY, 17.FINE
--         18.TOT.ASS VAL, 19.TOT. AMOUNT
IF OBJECT_ID('part1.c_duty_summary', 'U') IS NULL
CREATE TABLE part1.c_duty_summary (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    bcd DECIMAL(15,2) DEFAULT 0,           -- 1.BCD (Basic Customs Duty)
    acd DECIMAL(15,2) DEFAULT 0,           -- 2.ACD (Additional Customs Duty)
    sws DECIMAL(15,2) DEFAULT 0,           -- 3.SWS (Social Welfare Surcharge)
    nccd DECIMAL(15,2) DEFAULT 0,          -- 4.NCCD
    add_duty DECIMAL(15,2) DEFAULT 0,      -- 5.ADD (Additional Duty)
    cvd DECIMAL(15,2) DEFAULT 0,           -- 6.CVD (Countervailing Duty)
    igst DECIMAL(15,2) DEFAULT 0,          -- 7.IGST (e.g., 113241)
    g_cess DECIMAL(15,2) DEFAULT 0,        -- 8.G.CESS (e.g., 140)
    sg DECIMAL(15,2) DEFAULT 0,            -- 9.SG (Safeguard)
    saed DECIMAL(15,2) DEFAULT 0,          -- 10.SAED
    gsia DECIMAL(15,2) DEFAULT 0,          -- 11.GSIA
    tta DECIMAL(15,2) DEFAULT 0,           -- 12.TTA
    health DECIMAL(15,2) DEFAULT 0,        -- 13.HEALTH
    total_duty DECIMAL(15,2) DEFAULT 0,    -- 14.TOTAL DUTY (e.g., 5000)
    interest DECIMAL(15,2) DEFAULT 0,      -- 15.INT
    penalty DECIMAL(15,2) DEFAULT 0,       -- 16.PNLTY
    fine DECIMAL(15,2) DEFAULT 0,          -- 17.FINE
    tot_ass_val DECIMAL(18,2) DEFAULT 0,   -- 18.TOT.ASS VAL (e.g., 576262)
    tot_amount DECIMAL(18,2) DEFAULT 0,    -- 19.TOT. AMOUNT (e.g., 118381)
    CONSTRAINT fk_c_duty_summary_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section D: MANIFEST DETAILS
-- Fields: 1.IGM NO, 2.IGM DATE, 3.INW DATE, 4.GIGMNO, 5.GIGMDT, 6.MAWB NO, 7.DATE, 8.HAWB NO, 9.DATE, 10.PKG, 11.GW
IF OBJECT_ID('part1.d_manifest', 'U') IS NULL
CREATE TABLE part1.d_manifest (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    igm_no VARCHAR(30),               -- 1.IGM NO (e.g., "1000001")
    igm_date DATE,                    -- 2.IGM DATE (e.g., "14/04/2022")
    inw_date DATE,                    -- 3.INW DATE (e.g., "14/04/2022")
    gigm_no VARCHAR(30),              -- 4.GIGMNO (e.g., "0")
    gigm_date DATE,                   -- 5.GIGMDT
    mawb_no VARCHAR(50),              -- 6.MAWB NO (e.g., "12345678901")
    mawb_date DATE,                   -- 7.DATE (MAWB date, e.g., "07/04/2022")
    hawb_no VARCHAR(50),              -- 8.HAWB NO (e.g., "HAWB1234567")
    hawb_date DATE,                   -- 9.DATE (HAWB date, e.g., "07/04/2022")
    pkg INT DEFAULT 0,                -- 10.PKG (e.g., 1)
    gross_weight DECIMAL(12,3),       -- 11.GW (e.g., 54.6)
    CONSTRAINT fk_d_manifest_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section E: BOND DETAILS
-- Fields: 1.BOND NO., 2.PORT, 3.BOND CD, 4.DEBT AMT, 5.BG AMT
IF OBJECT_ID('part1.e_bond', 'U') IS NULL
CREATE TABLE part1.e_bond (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    bond_no VARCHAR(30),              -- 1.BOND NO. (e.g., "2001980436")
    port VARCHAR(20),                 -- 2.PORT (e.g., "INLDH6")
    bond_code VARCHAR(10),            -- 3.BOND CD (e.g., "NB")
    debt_amt DECIMAL(15,2),           -- 4.DEBT AMT (e.g., 52856)
    bg_amt DECIMAL(15,2),             -- 5.BG AMT (e.g., 0)
    CONSTRAINT fk_e_bond_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section F: PAYMENT DETAILS
-- Fields: 1.SR NO, 2.CHALLAN NO, 3.PAID ON, 4.AMOUNT(Rs.)
IF OBJECT_ID('part1.f_payment', 'U') IS NULL
CREATE TABLE part1.f_payment (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    sr_no INT,                        -- 1.SR NO (e.g., 1)
    challan_no VARCHAR(30),           -- 2.CHALLAN NO (e.g., "2038905530")
    paid_on DATE,                     -- 3.PAID ON (e.g., "18/04/2022")
    amount DECIMAL(15,2),             -- 4.AMOUNT(Rs.) (e.g., 113241)
    CONSTRAINT fk_f_payment_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section G: WH (Warehouse)
-- Fields: 1.WBE NO., 2.DATE, 3.WBE SITE, 4.WH CODE
IF OBJECT_ID('part1.g_wh', 'U') IS NULL
CREATE TABLE part1.g_wh (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    wbe_no VARCHAR(30),               -- 1.WBE NO.
    wbe_date DATE,                    -- 2.DATE
    wbe_site VARCHAR(50),             -- 3.WBE SITE
    wh_code VARCHAR(20),              -- 4.WH CODE
    CONSTRAINT fk_g_wh_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section H: PROCESSING DETAILS
-- Fields: 1.EVENT, 2.DATE, 3.TIME, EXCHANGE RATE
-- Multiple rows: Submission, Assessment, Examination, OOC
IF OBJECT_ID('part1.h_processing', 'U') IS NULL
CREATE TABLE part1.h_processing (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    event VARCHAR(50),                -- 1.EVENT (e.g., "Submission", "Assessment", "OOC")
    event_date VARCHAR(50),           -- 2.DATE (e.g., "15-APR-22", stored as text for OCR)
    event_time VARCHAR(50),           -- 3.TIME (e.g., "18:40")
    exchange_rate VARCHAR(100),       -- EXCHANGE RATE (e.g., "1 EUR=84.4INR")
    CONSTRAINT fk_h_processing_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section I: INVOICE DETAILS - SUMMARY
-- Fields: 1.S.NO, 2.INVOICE NO, 3.INV. AMT, 4.CUR
IF OBJECT_ID('part1.i_invoice_summary', 'U') IS NULL
CREATE TABLE part1.i_invoice_summary (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    sno INT,                          -- 1.S.NO (e.g., 1)
    invoice_no VARCHAR(50),           -- 2.INVOICE NO (e.g., "VRE/22000254")
    inv_amt DECIMAL(15,2),            -- 3.INV. AMT (e.g., 6397.41)
    currency VARCHAR(10),             -- 4.CUR (e.g., "EUR")
    CONSTRAINT fk_i_invoice_summary_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section J: CONTAINER DETAILS
-- Fields: 1.SNO, 2.LCL/FCL, 3.TRUCK, 4.SEAL, 5.CONTAINER NUMBER
IF OBJECT_ID('part1.j_container', 'U') IS NULL
CREATE TABLE part1.j_container (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    sno INT,                          -- 1.SNO
    lcl_fcl VARCHAR(10),              -- 2.LCL/FCL
    truck VARCHAR(50),                -- 3.TRUCK
    seal VARCHAR(50),                 -- 4.SEAL
    container_number VARCHAR(50),     -- 5.CONTAINER NUMBER
    CONSTRAINT fk_j_container_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- OOC Details (footer of Part I)
-- Fields: OOC NO., OOC DATE
IF OBJECT_ID('part1.ooc', 'U') IS NULL
CREATE TABLE part1.ooc (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    ooc_no VARCHAR(30),               -- OOC NO. (e.g., "2046018092")
    ooc_date DATE,                    -- OOC DATE (e.g., "19-04-2022")
    CONSTRAINT fk_ooc_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- ============================================
-- SCHEMA: part2
-- PART II - INVOICE & VALUATION DETAILS (Pages 2-3)
-- ============================================

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'part2')
BEGIN
    EXEC('CREATE SCHEMA part2')
END
GO

-- Section A: INVOICE
-- Fields: 1.S.NO, 2.INVOICE NO. & DT., 3.PURCHASE ORDER NO & DT, 4.LC NO & DATE, 5.CONTRACT NO & DATE
IF OBJECT_ID('part2.a_invoice', 'U') IS NULL
CREATE TABLE part2.a_invoice (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    sno INT,                          -- 1.S.NO
    invoice_no VARCHAR(50),           -- 2.INVOICE NO.
    invoice_date DATE,                -- 2. Invoice DATE
    purchase_order_no VARCHAR(50),    -- 3.PURCHASE ORDER NO
    purchase_order_date DATE,         -- 3. PO DATE
    lc_no VARCHAR(50),                -- 4.LC NO
    lc_date DATE,                     -- 4. LC DATE
    contract_no VARCHAR(50),          -- 5.CONTRACT NO
    contract_date DATE,               -- 5. CONTRACT DATE
    CONSTRAINT fk_a_invoice_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE,
    INDEX idx_invoice_no (invoice_no)
);
GO

-- Section B: TRANSACTING PARTIES
-- Fields: 1.BUYER'S NAME & ADDRESS, 2.SELLER'S NAME & ADDRESS,
--         3.SUPPLIER NAME & ADDRESS, 4.THIRD PARTY NAME & ADDRESS, 5.AEO
IF OBJECT_ID('part2.b_transacting_parties', 'U') IS NULL
CREATE TABLE part2.b_transacting_parties (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    invoice_sno INT,
    buyer_name VARCHAR(255),          -- 1.BUYER'S NAME
    buyer_address VARCHAR(500),       -- 1.BUYER'S ADDRESS
    seller_name VARCHAR(255),         -- 2.SELLER'S NAME
    seller_address VARCHAR(500),      -- 2.SELLER'S ADDRESS
    supplier_name VARCHAR(255),       -- 3.SUPPLIER NAME
    supplier_address VARCHAR(500),    -- 3.SUPPLIER ADDRESS
    third_party_name VARCHAR(255),    -- 4.THIRD PARTY NAME
    third_party_address VARCHAR(500), -- 4.THIRD PARTY ADDRESS
    aeo VARCHAR(100),                 -- 5.AEO
    CONSTRAINT fk_b_transacting_parties_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section C: VALUATION
-- Fields: 1.INV VALUE, 2.FREIGHT, 3.INSURANCE, 4.HSS., 5.LOADING, 6.COMMN, 7.PAY TERMS, 8.VALUATION METHOD
--         9.RELTD, 10.SVB CH, 11.SVB NO, 12.DATE, 13.LOA, 14.Cur, 15.Term
IF OBJECT_ID('part2.c_valuation', 'U') IS NULL
CREATE TABLE part2.c_valuation (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    invoice_sno INT,
    inv_value DECIMAL(15,2),          -- 1.INV VALUE (e.g., 6397.41)
    freight DECIMAL(15,6),            -- 2.FREIGHT (e.g., .005%)
    insurance DECIMAL(15,6),          -- 3.INSURANCE
    hss DECIMAL(15,2),                -- 4.HSS.
    loading DECIMAL(15,2),            -- 5.LOADING
    commission DECIMAL(15,2),         -- 6.COMMN
    pay_terms VARCHAR(50),            -- 7.PAY TERMS (e.g., "OTH")
    valuation_method VARCHAR(100),    -- 8.VALUATION METHOD (e.g., "RULE 4 (TRANSACTION VALUE)")
    related VARCHAR(10),              -- 9.RELTD (e.g., "No")
    svb_ch VARCHAR(20),               -- 10.SVB CH
    svb_no VARCHAR(30),               -- 11.SVB NO
    svb_date DATE,                    -- 12.DATE
    loa VARCHAR(20),                  -- 13.LOA
    currency VARCHAR(10),             -- 14.Cur (e.g., "EUR")
    terms VARCHAR(20),                -- 15.Term (e.g., "CF")
    ad_code VARCHAR(20),              -- 6.AD CODE
    CONSTRAINT fk_c_valuation_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section D: COST & SERVICES
-- Fields: 1.C&B, 2.CoC, 3.CoP, 4.HND CHG, 5.G&S, 6.DOC. CH
--         7.COO, 8.R & LF, 9.OTH COST, 10.LD / ULD, 11.WS, 12.OTC, 13.MISC CHARGE, 14.ASS. VALUE
IF OBJECT_ID('part2.d_cost_services', 'U') IS NULL
CREATE TABLE part2.d_cost_services (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    invoice_sno INT,
    c_and_b DECIMAL(15,2),            -- 1.C&B (Commission & Brokerage)
    coc DECIMAL(15,2),                -- 2.CoC (Cost of Container)
    cop DECIMAL(15,2),                -- 3.CoP (Cost of Packing)
    hnd_chg DECIMAL(15,2),            -- 4.HND CHG (Handling Charges)
    g_and_s DECIMAL(15,2),            -- 5.G&S (Goods and Service input cost)
    doc_ch DECIMAL(15,2),             -- 6.DOC. CH (Document Charges)
    coo VARCHAR(50),                  -- 7.COO (Country of Origin Certificate)
    r_and_lf DECIMAL(15,2),           -- 8.R & LF (Royalty and Licence Fees)
    oth_cost DECIMAL(15,2),           -- 9.OTH COST
    ld_uld DECIMAL(15,2),             -- 10.LD / ULD (Loading Unloading)
    ws DECIMAL(15,2),                 -- 11.WS (Warranty Services)
    otc DECIMAL(15,2),                -- 12.OTC (Other Costs)
    misc_charge DECIMAL(15,2),        -- 13.MISC CHARGE (e.g., 430)
    ass_value DECIMAL(18,2),          -- 14.ASS. VALUE (e.g., 576262.27)
    CONSTRAINT fk_d_cost_services_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section E: ITEM DETAILS
-- Fields: 1.S NO., 2.CTH, 3.DESCRIPTION, 4.UNIT PRICE, 5.QUANTITY, 6.UQC, 7.AMOUNT
IF OBJECT_ID('part2.e_item', 'U') IS NULL
CREATE TABLE part2.e_item (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    invoice_sno INT DEFAULT 1,
    item_sno INT NOT NULL,            -- 1.S NO.
    cth VARCHAR(20),                  -- 2.CTH (e.g., "84484990")
    description VARCHAR(500),         -- 3.DESCRIPTION
    unit_price DECIMAL(15,6),         -- 4.UNIT PRICE (e.g., 308.080000)
    quantity DECIMAL(15,6),           -- 5.QUANTITY (e.g., 2.000000)
    uqc VARCHAR(20),                  -- 6.UQC (e.g., "PCS")
    amount DECIMAL(15,2),             -- 7.AMOUNT (e.g., 616.16)
    CONSTRAINT fk_e_item_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE,
    INDEX idx_item_cth (cth)
);
GO

-- ============================================
-- SCHEMA: part3
-- PART III - DUTIES (Pages 4-13)
-- ============================================

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'part3')
BEGIN
    EXEC('CREATE SCHEMA part3')
END
GO

-- Section A: ITEM DETAILS
-- Fields: 1.INVSNO, 2.ITEMSN, 3.CTH, 4.CETH, 5.ITEM DESCRIPTION, 6.FS, 7.PQ, 8.DC, 9.WC, 10.AQ
--         11.UPI, 12.COO, 13.C.QTY, 14.C.UQC, 15.S.QTY, 16.S.UQC, 17.SCH, 18.STND/PR, 19.RSP
--         20.REIMP, 21.PROV, 22.END USE, 23.PRODN, 24.CNTRL, 25.QUALFR, 26.CONTNT, 27.STMNT, 28.SUP DOCS
--         29.ASSESS VALUE, 30.TOTAL DUTY
IF OBJECT_ID('part3.a_item_details', 'U') IS NULL
CREATE TABLE part3.a_item_details (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    inv_sno INT,                      -- 1.INVSNO
    item_sno INT NOT NULL,            -- 2.ITEMSN
    cth VARCHAR(20),                  -- 3.CTH
    ceth VARCHAR(20),                 -- 4.CETH (e.g., "NOEXCISE")
    item_description VARCHAR(500),    -- 5.ITEM DESCRIPTION
    fs VARCHAR(10),                   -- 6.FS (Food Safety)
    pq VARCHAR(10),                   -- 7.PQ (Plant Quarantine)
    dc VARCHAR(10),                   -- 8.DC (Drugs Control)
    wc VARCHAR(10),                   -- 9.WC (Wildlife Crime)
    aq VARCHAR(10),                   -- 10.AQ (Animal Quarantine)
    upi DECIMAL(15,6),                -- 11.UPI (Unit Price Invoiced)
    coo VARCHAR(10),                  -- 12.COO (Country of Origin)
    c_qty DECIMAL(15,6),              -- 13.C.QTY (Commercial Quantity)
    c_uqc VARCHAR(20),                -- 14.C.UQC
    s_qty DECIMAL(15,6),              -- 15.S.QTY (Standard Quantity)
    s_uqc VARCHAR(20),                -- 16.S.UQC
    sch VARCHAR(30),                  -- 17.SCH (Scheme)
    stnd_pr VARCHAR(10),              -- 18.STND/PR
    rsp VARCHAR(10),                  -- 19.RSP
    reimp VARCHAR(10),                -- 20.REIMP
    prov VARCHAR(10),                 -- 21.PROV
    end_use VARCHAR(30),              -- 22.END USE (e.g., "GNX200")
    prodn VARCHAR(10),                -- 23.PRODN
    cntrl VARCHAR(10),                -- 24.CNTRL
    qualfr VARCHAR(10),               -- 25.QUALFR
    contnt VARCHAR(10),               -- 26.CONTNT
    stmnt VARCHAR(10),                -- 27.STMNT
    sup_docs VARCHAR(10),             -- 28.SUP DOCS
    assess_value DECIMAL(18,2),       -- 29.ASSESS VALUE
    total_duty DECIMAL(15,2),         -- 30.TOTAL DUTY
    CONSTRAINT fk_a_item_details_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE,
    INDEX idx_item_duty_item (document_id, item_sno)
);
GO

-- Section B: ITEM DUTY
-- Fields: DUTY (Notn No., Notn SNo., Rate, Amount, Duty Fg) for:
--         1.BCD, 2.ACD, 3.SWS, 4.SAD, 5.IGST, 6.G.CESS, 7.ADD, 8.CVD, 9.SG, 10.T.VALUE
IF OBJECT_ID('part3.b_item_duty', 'U') IS NULL
CREATE TABLE part3.b_item_duty (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    inv_sno INT,
    item_sno INT NOT NULL,
    -- BCD (Basic Customs Duty)
    bcd_notn_no VARCHAR(20),          -- Notn No.
    bcd_notn_sno VARCHAR(20),         -- Notn SNo.
    bcd_rate DECIMAL(8,4),            -- Rate
    bcd_amount DECIMAL(15,2),         -- Amount
    bcd_duty_fg VARCHAR(10),          -- Duty Fg
    -- ACD
    acd_rate DECIMAL(8,4),
    acd_amount DECIMAL(15,2),
    -- SWS
    sws_rate DECIMAL(8,4),
    sws_amount DECIMAL(15,2),
    -- SAD
    sad_amount DECIMAL(15,2),
    -- IGST
    igst_notn_no VARCHAR(20),
    igst_notn_sno VARCHAR(20),
    igst_rate DECIMAL(8,4),
    igst_amount DECIMAL(15,2),
    -- G.CESS
    g_cess_amount DECIMAL(15,2),
    -- ADD
    add_amount DECIMAL(15,2),
    -- CVD
    cvd_amount DECIMAL(15,2),
    -- SG
    sg_amount DECIMAL(15,2),
    -- T.VALUE
    t_value DECIMAL(18,2),            -- 10.T.VALUE
    CONSTRAINT fk_b_item_duty_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section C: OTHER DUTIES
-- Fields: 1.SP EXD, 2.CHCESS, 3.TTA, 4.CESS, 5.CAIDC, 6.EAIDC, 7.CUS EDC, 8.CUS HEC, 9.NCD, 10.AGGR
IF OBJECT_ID('part3.c_other_duties', 'U') IS NULL
CREATE TABLE part3.c_other_duties (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    inv_sno INT,
    item_sno INT NOT NULL,
    notn_no VARCHAR(20),              -- Notn No.
    notn_sno VARCHAR(20),             -- Notn SNo.
    sp_exd DECIMAL(15,2),             -- 1.SP EXD
    chcess DECIMAL(15,2),             -- 2.CHCESS
    tta DECIMAL(15,2),                -- 3.TTA
    cess DECIMAL(15,2),               -- 4.CESS
    caidc DECIMAL(15,2),              -- 5.CAIDC
    eaidc DECIMAL(15,2),              -- 6.EAIDC
    cus_edc DECIMAL(15,2),            -- 7.CUS EDC
    cus_hec DECIMAL(15,2),            -- 8.CUS HEC
    ncd DECIMAL(15,2),                -- 9.NCD
    aggr DECIMAL(15,2),               -- 10.AGGR
    duty_fg DECIMAL(15,2),            -- Duty Fg (total)
    CONSTRAINT fk_c_other_duties_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- ============================================
-- SCHEMA: part4
-- PART IV - ADDITIONAL DETAILS (Pages 14-15)
-- ============================================

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'part4')
BEGIN
    EXEC('CREATE SCHEMA part4')
END
GO

-- Section A: SVB DETAILS
-- Fields: 1.INVSNO, 2.ITMSNO, 3.REF NO, 4.REF DT, 5.PRT CD, 6.LAB, 7.P/F, 8.LOAD DATE, 9.P/F
IF OBJECT_ID('part4.a_svb', 'U') IS NULL
CREATE TABLE part4.a_svb (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    inv_sno INT,
    item_sno INT,
    ref_no VARCHAR(50),               -- 3.REF NO (SVB Reference Number)
    ref_dt DATE,                      -- 4.REF DT (SVB Reference Date)
    prt_cd VARCHAR(20),               -- 5.PRT CD
    lab VARCHAR(50),                  -- 6.LAB
    pf_1 VARCHAR(10),                 -- 7.P/F
    load_date DATE,                   -- 8.LOAD DATE
    pf_2 VARCHAR(10),                 -- 9.P/F
    CONSTRAINT fk_a_svb_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section B: PREVIOUS BEs
-- Fields: 1.INVSNO, 2.ITMSNO, 3.BE NO, 4.BE DATE, 5.PRT CD, 6.UNITPRICE, 7.CURRENCY CODE
IF OBJECT_ID('part4.b_previous_be', 'U') IS NULL
CREATE TABLE part4.b_previous_be (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    inv_sno INT,
    item_sno INT,
    be_no VARCHAR(30),                -- 3.BE NO
    be_date DATE,                     -- 4.BE DATE
    prt_cd VARCHAR(20),               -- 5.PRT CD
    unit_price DECIMAL(15,6),         -- 6.UNITPRICE
    currency_code VARCHAR(10),        -- 7.CURRENCY CODE
    CONSTRAINT fk_b_previous_be_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section C: RE-IMPORT AFTER EXPORT
-- Fields: 1.INVSNO, 2.ITMSNO, 3.NOTN NO, 4.SLNO, 5.FRT, 6.INS, 7.DUTY, 8.SB NO, 9.SB DT, 10.PORTCD, 11.SINV, 12.SITEMN
IF OBJECT_ID('part4.c_reimport', 'U') IS NULL
CREATE TABLE part4.c_reimport (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    inv_sno INT,
    item_sno INT,
    notn_no VARCHAR(30),              -- 3.NOTN NO
    slno VARCHAR(20),                 -- 4.SLNO
    frt DECIMAL(15,2),                -- 5.FRT
    ins DECIMAL(15,2),                -- 6.INS
    duty DECIMAL(15,2),               -- 7.DUTY
    sb_no VARCHAR(30),                -- 8.SB NO
    sb_dt DATE,                       -- 9.SB DT
    port_cd VARCHAR(20),              -- 10.PORTCD
    sinv INT,                         -- 11.SINV
    sitemn INT,                       -- 12.SITEMN
    CONSTRAINT fk_c_reimport_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section D: ITEM MANUFACTURER/PRODUCER/GROWER DETAILS
-- Fields: 1.INVSNO, 2.ITMSNO, 3.TYPE, 4.MANUFACT CD, 5.SOURCE CY, 6.TRANS CY, 7.ADDRESS
IF OBJECT_ID('part4.d_manufacturer', 'U') IS NULL
CREATE TABLE part4.d_manufacturer (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    inv_sno INT,
    item_sno INT,
    type VARCHAR(50),                 -- 3.TYPE
    manufact_cd VARCHAR(50),          -- 4.MANUFACT CD
    source_cy VARCHAR(50),            -- 5.SOURCE CY
    trans_cy VARCHAR(50),             -- 6.TRANS CY
    address VARCHAR(500),             -- 7.ADDRESS
    CONSTRAINT fk_d_manufacturer_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section E: ACCESSORY STATUS
-- Fields: 1.INVSNO, 2.ITMSNO, 3.ACESSORY ITEM DETAILS
IF OBJECT_ID('part4.e_accessory', 'U') IS NULL
CREATE TABLE part4.e_accessory (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    inv_sno INT,
    item_sno INT,
    accessory_item_details VARCHAR(500), -- 3.ACESSORY ITEM DETAILS
    CONSTRAINT fk_e_accessory_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section F: LICENCE DETAILS
-- Fields: 1.INVSNO, 2.ITMSNO, 3.LIC SLNO, 4.LIC NO, 5.LIC DATE, 6.CODE, 7.PORT, 8.DEBIT VALUE, 9.QTY, 10.UQC, 11.DEBIT DUTY
IF OBJECT_ID('part4.f_licence', 'U') IS NULL
CREATE TABLE part4.f_licence (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    inv_sno INT,                      -- 1.INVSNO (e.g., 1)
    item_sno INT,                     -- 2.ITMSNO (e.g., 1-30)
    lic_slno INT,                     -- 3.LIC SLNO (e.g., 19)
    lic_no VARCHAR(30),               -- 4.LIC NO (e.g., "1100000001")
    lic_date DATE,                    -- 5.LIC DATE (e.g., "30-MAR-22")
    code VARCHAR(20),                 -- 6.CODE (e.g., "12")
    port VARCHAR(20),                 -- 7.PORT (e.g., "INLDH6")
    debit_value DECIMAL(18,2),        -- 8.DEBIT VALUE (e.g., 55502.11)
    qty DECIMAL(15,6),                -- 9.QTY (e.g., 2)
    uqc VARCHAR(20),                  -- 10.UQC (e.g., "NOS")
    debit_duty DECIMAL(15,2),         -- 11.DEBIT DUTY
    CONSTRAINT fk_f_licence_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section G: CERTIFICATE DETAILS
-- Fields: 1.CERTIFICATE NUMBER, 2.DATE, 3.TYPE
IF OBJECT_ID('part4.g_certificate', 'U') IS NULL
CREATE TABLE part4.g_certificate (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    certificate_number VARCHAR(50),   -- 1.CERTIFICATE NUMBER
    certificate_date DATE,            -- 2.DATE
    certificate_type VARCHAR(50),     -- 3.TYPE
    CONSTRAINT fk_g_certificate_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section H: HSS DETAILS
-- Fields: 1.PRC LEVEL, 2.IEC, 3.BRANCH SLNO
IF OBJECT_ID('part4.h_hss', 'U') IS NULL
CREATE TABLE part4.h_hss (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    prc_level VARCHAR(50),            -- 1.PRC LEVEL (Preceding)
    iec VARCHAR(50),                  -- 2.IEC
    branch_slno VARCHAR(30),          -- 3.BRANCH SLNO
    CONSTRAINT fk_h_hss_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section I: SINGLE WINDOW DECLARATION
-- Fields: 1.INVSN, 2.ITMSNO, 3.INFO TYP, 4.QUALIFIER, 5.INFO CD, 6.INFO TEXT, 7.INFO MSR, 8.UQC
IF OBJECT_ID('part4.i_sw_declaration', 'U') IS NULL
CREATE TABLE part4.i_sw_declaration (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    inv_sno INT,                      -- 1.INVSN
    item_sno INT,                     -- 2.ITMSNO
    info_type VARCHAR(20),            -- 3.INFO TYP (e.g., "CHR", "PNM")
    qualifier VARCHAR(30),            -- 4.QUALIFIER (e.g., "SQC", "SIU")
    info_cd VARCHAR(30),              -- 5.INFO CD (e.g., "SIUNAF")
    info_text VARCHAR(100),           -- 6.INFO TEXT (e.g., "SIUN000")
    info_msr DECIMAL(15,6),           -- 7.INFO MSR (e.g., 3.206)
    uqc VARCHAR(20),                  -- 8.UQC (e.g., "KGS")
    CONSTRAINT fk_i_sw_declaration_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section J: SINGLE WINDOW DECLARATION - CONSTITUENTS
-- Fields: 1.INVSN, 2.ITMSNO, 3.C SNO, 4.NAME, 5.CODE, 6.PERCENTAGE, 7.YIELD PCT, 8.ING
IF OBJECT_ID('part4.j_sw_constituents', 'U') IS NULL
CREATE TABLE part4.j_sw_constituents (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    inv_sno INT,
    item_sno INT,
    c_sno INT,                        -- 3.C SNO
    name VARCHAR(100),                -- 4.NAME
    code VARCHAR(30),                 -- 5.CODE
    percentage DECIMAL(8,4),          -- 6.PERCENTAGE
    yield_pct DECIMAL(8,4),           -- 7.YIELD PCT
    ing VARCHAR(20),                  -- 8.ING (Ingredient)
    CONSTRAINT fk_j_sw_constituents_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section K: SINGLE WINDOW DECLARATION - CONTROL
-- Fields: 1.INVSN, 2.ITMSNO, 3.CONTROL TYPE, 4.LOCATION, 5.SRT DT, 6.END DT, 7.RES CD, 8.RES TEXT
IF OBJECT_ID('part4.k_sw_control', 'U') IS NULL
CREATE TABLE part4.k_sw_control (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    inv_sno INT,
    item_sno INT,
    control_type VARCHAR(50),         -- 3.CONTROL TYPE
    location VARCHAR(100),            -- 4.LOCATION
    srt_dt DATE,                      -- 5.SRT DT
    end_dt DATE,                      -- 6.END DT
    res_cd VARCHAR(30),               -- 7.RES CD (Control Result Code)
    res_text VARCHAR(255),            -- 8.RES TEXT (Control Result Text)
    CONSTRAINT fk_k_sw_control_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section L: SUPPORTING DOCUMENTS
-- Fields: 1.INVSN, 2.ITMSNO, 3.TYP, 4.ICEGATE ID, 5.IRN, 6.DOC CODE, 7.ISSUE PLACE, 8.ISSUE DT, 9.EXP DT
IF OBJECT_ID('part4.l_supporting_docs', 'U') IS NULL
CREATE TABLE part4.l_supporting_docs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    inv_sno INT,                      -- 1.INVSN (e.g., 0, 1)
    item_sno INT,                     -- 2.ITMSNO (e.g., 0)
    doc_type VARCHAR(20),             -- 3.TYP (e.g., "70300", "929AS")
    icegate_id VARCHAR(50),           -- 4.ICEGATE ID (e.g., "CORELOGISTICS18")
    irn VARCHAR(50),                  -- 5.IRN (e.g., "2022041500058503")
    doc_code VARCHAR(30),             -- 6.DOC CODE
    issue_place VARCHAR(100),         -- 7.ISSUE PLACE (e.g., "Italy")
    issue_date DATE,                  -- 8.ISSUE DT (e.g., "15-APR-22")
    exp_date DATE,                    -- 9.EXP DT
    CONSTRAINT fk_l_supporting_docs_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section M: CONTAINER DETAILS (Part IV version)
-- Fields: 1.CONTAINER NUMBER, 2.TRUCK NUMBER, 3.SEAL NUMBER, 4.FCL/LCL
IF OBJECT_ID('part4.m_container', 'U') IS NULL
CREATE TABLE part4.m_container (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    container_number VARCHAR(50),     -- 1.CONTAINER NUMBER
    truck_number VARCHAR(50),         -- 2.TRUCK NUMBER
    seal_number VARCHAR(50),          -- 3.SEAL NUMBER
    fcl_lcl VARCHAR(10),              -- 4.FCL/LCL
    CONSTRAINT fk_m_container_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section N: INVOICE DETAILS (Part IV summary)
-- Fields: 1.S NO, 2.INVOICE NO, 3.INVOICE AMOUNT, 4.CUR
IF OBJECT_ID('part4.n_invoice', 'U') IS NULL
CREATE TABLE part4.n_invoice (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    sno INT,                          -- 1.S NO
    invoice_no VARCHAR(50),           -- 2.INVOICE NO
    invoice_amount DECIMAL(15,2),     -- 3.INVOICE AMOUNT
    currency VARCHAR(10),             -- 4.CUR
    CONSTRAINT fk_n_invoice_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- ============================================
-- SCHEMA: part5
-- PART V - OTHER COMPLIANCES (Page 16)
-- ============================================

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'part5')
BEGIN
    EXEC('CREATE SCHEMA part5')
END
GO

-- Section A: EXAMINATION ORDER
IF OBJECT_ID('part5.a_examination_order', 'U') IS NULL
CREATE TABLE part5.a_examination_order (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    examination_order NVARCHAR(MAX),  -- e.g., "ACCREDITED CLIENT BE WITH AEO Category 3..."
    CONSTRAINT fk_a_examination_order_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section B: EXAMINATION INSTRUCTIONS
IF OBJECT_ID('part5.b_examination_instructions', 'U') IS NULL
CREATE TABLE part5.b_examination_instructions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    examination_instructions NVARCHAR(MAX),
    CONSTRAINT fk_b_examination_instructions_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section B1: PGA EXAMINATION INSTRUCTIONS
-- Fields: Inv No, Item No, Agency, Status
IF OBJECT_ID('part5.b1_pga_instructions', 'U') IS NULL
CREATE TABLE part5.b1_pga_instructions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    inv_no INT,
    item_no INT,
    agency VARCHAR(100),
    status VARCHAR(100),
    CONSTRAINT fk_b1_pga_instructions_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section C: COMPULSORY COMPLIANCE
IF OBJECT_ID('part5.c_compulsory_compliance', 'U') IS NULL
CREATE TABLE part5.c_compulsory_compliance (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    compulsory_compliance NVARCHAR(MAX), -- Long text with compliance requirements
    CONSTRAINT fk_c_compulsory_compliance_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section D: AC REMARKS
IF OBJECT_ID('part5.d_ac_remarks', 'U') IS NULL
CREATE TABLE part5.d_ac_remarks (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    ac_remarks NVARCHAR(MAX),
    CONSTRAINT fk_d_ac_remarks_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section E: EXAMINATION REPORT
IF OBJECT_ID('part5.e_examination_report', 'U') IS NULL
CREATE TABLE part5.e_examination_report (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    examination_report NVARCHAR(MAX),
    CONSTRAINT fk_e_examination_report_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section F: SUPERINTENDENT COMMENTS
IF OBJECT_ID('part5.f_superintendent_comments', 'U') IS NULL
CREATE TABLE part5.f_superintendent_comments (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    superintendent_comments NVARCHAR(MAX),
    CONSTRAINT fk_f_superintendent_comments_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- OOC Details (Part V footer)
IF OBJECT_ID('part5.ooc', 'U') IS NULL
CREATE TABLE part5.ooc (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    ooc_no VARCHAR(30),               -- OOC No (e.g., "2046018092")
    ooc_date DATE,                    -- OOC Date (e.g., "19-04-2022")
    CONSTRAINT fk_ooc_part5_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- ============================================
-- SCHEMA: part6
-- PART VI - DECLARATION (Page 17)
-- ============================================

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'part6')
BEGIN
    EXEC('CREATE SCHEMA part6')
END
GO

-- Section A: DECLARATION STATEMENT
IF OBJECT_ID('part6.a_declaration_statement', 'U') IS NULL
CREATE TABLE part6.a_declaration_statement (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    declaration_text NVARCHAR(MAX),   -- Full declaration text
    CONSTRAINT fk_a_declaration_statement_document FOREIGN KEY (document_id)
        REFERENCES header.documents(document_id) ON DELETE CASCADE
);
GO

-- Section B: AUTHORIZED SIGNATORY
IF OBJECT_ID('part6.b_authorized_signatory', 'U') IS NULL
CREATE TABLE part6.b_authorized_signatory (
    id INT IDENTITY(1,1) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    sign_date DATE,                   -- DATE
    place VARCHAR(100),               -- PLACE
    authorized_signatory VARCHAR(255), -- AUTHORISED SIGNATORY
    cha_name VARCHAR(255),            -- CHA NAME (e.g., "CORE LOGISTICS")
    CONSTRAINT fk_b_authorized_signatory_document FOREIGN KEY (document_id)
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

-- Glossary terms (from PDF footer)
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

PRINT 'Database schema v2 created successfully!'
PRINT 'Total tables: 41 (excluding reference and audit)'
GO
