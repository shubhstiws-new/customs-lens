"""
Human-in-the-Loop Validation Interface
Streamlit app for reviewing and correcting OCR-extracted BoE data
"""

import json
import streamlit as st
from pathlib import Path
import sqlite3
from datetime import datetime, date
import pandas as pd

# Page config
st.set_page_config(
    page_title="BoE Validator",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database path
DB_PATH = "output/boe_local.db"


def get_db_connection():
    """Get SQLite database connection"""
    return sqlite3.connect(DB_PATH)


def get_all_documents():
    """Fetch all documents from database"""
    conn = get_db_connection()
    query = """
        SELECT
            d.document_id,
            d.be_no,
            d.be_date,
            d.port_code,
            d.port_name,
            d.inv_count,
            d.item_count,
            d.created_at,
            ds.total_duty,
            ds.igst
        FROM documents d
        LEFT JOIN part1_duty_summary ds ON d.document_id = ds.document_id
        ORDER BY d.created_at DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_document_details(document_id: str):
    """Fetch complete document details"""
    conn = get_db_connection()

    # Main document
    doc_df = pd.read_sql_query(
        "SELECT * FROM documents WHERE document_id = ?",
        conn, params=(document_id,)
    )

    # Status
    status_df = pd.read_sql_query(
        "SELECT * FROM part1_status WHERE document_id = ?",
        conn, params=(document_id,)
    )

    # Declarant
    declarant_df = pd.read_sql_query(
        "SELECT * FROM part1_declarant WHERE document_id = ?",
        conn, params=(document_id,)
    )

    # Duty Summary
    duty_df = pd.read_sql_query(
        "SELECT * FROM part1_duty_summary WHERE document_id = ?",
        conn, params=(document_id,)
    )

    # Manifest
    manifest_df = pd.read_sql_query(
        "SELECT * FROM part1_manifest WHERE document_id = ?",
        conn, params=(document_id,)
    )

    # Licences
    licences_df = pd.read_sql_query(
        "SELECT * FROM part4_licence WHERE document_id = ? ORDER BY item_sno",
        conn, params=(document_id,)
    )

    conn.close()

    return {
        "document": doc_df,
        "status": status_df,
        "declarant": declarant_df,
        "duty_summary": duty_df,
        "manifest": manifest_df,
        "licences": licences_df
    }


def update_document_field(document_id: str, table: str, field: str, value):
    """Update a field in the database"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            f"UPDATE {table} SET {field} = ? WHERE document_id = ?",
            (value, document_id)
        )
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Update failed: {e}")
        return False
    finally:
        conn.close()


def render_sidebar():
    """Render sidebar with document list"""
    st.sidebar.title("📋 BoE Documents")

    # Refresh button
    if st.sidebar.button("🔄 Refresh List"):
        st.rerun()

    # Get documents
    docs_df = get_all_documents()

    if docs_df.empty:
        st.sidebar.warning("No documents found in database")
        st.sidebar.info("Import a document using the pipeline first")
        return None

    st.sidebar.write(f"**{len(docs_df)} document(s)**")

    # Document selector
    selected_id = st.sidebar.selectbox(
        "Select Document",
        docs_df["document_id"].tolist(),
        format_func=lambda x: f"{x} - BE#{docs_df[docs_df['document_id']==x]['be_no'].values[0]}"
    )

    # Quick stats for selected
    if selected_id:
        row = docs_df[docs_df["document_id"] == selected_id].iloc[0]
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**BE No:** {row['be_no']}")
        st.sidebar.markdown(f"**Date:** {row['be_date']}")
        st.sidebar.markdown(f"**Port:** {row['port_code']}")
        if row['total_duty']:
            st.sidebar.markdown(f"**Total Duty:** ₹{row['total_duty']:,.2f}")

    return selected_id


def render_header_section(doc_data):
    """Render header/document section"""
    st.subheader("📄 Document Header")

    doc_df = doc_data["document"]
    if doc_df.empty:
        st.warning("No document data found")
        return

    doc = doc_df.iloc[0]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.text_input("Document ID", value=doc["document_id"], disabled=True, key="h_doc_id")
        st.text_input("BE No", value=doc["be_no"] or "", key="h_be_no")

    with col2:
        st.text_input("BE Date", value=str(doc["be_date"]) if doc["be_date"] else "", key="h_be_date")
        st.text_input("BE Type", value=doc["be_type"] or "", key="h_be_type")

    with col3:
        st.text_input("Port Code", value=doc["port_code"] or "", key="h_port_code")
        st.text_input("IEC/BR", value=doc["iec_br"] or "", key="h_iec_br")

    with col4:
        st.text_input("GSTIN", value=doc["gstin_type"] or "", key="h_gstin")
        st.text_input("CB Code", value=doc["cb_code"] or "", key="h_cb_code")

    # Port name (full width)
    st.text_input("Port Name", value=doc["port_name"] or "", key="h_port_name")

    # Counts
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.number_input("Invoice Count", value=int(doc["inv_count"] or 0), key="h_inv_count")
    with col2:
        st.number_input("Item Count", value=int(doc["item_count"] or 0), key="h_item_count")
    with col3:
        st.number_input("Container Count", value=int(doc["cont_count"] or 0), key="h_cont_count")
    with col4:
        st.number_input("Package Count", value=int(doc["pkg_count"] or 0), key="h_pkg_count")


def render_duty_section(doc_data):
    """Render duty summary section"""
    st.subheader("💰 Duty Summary")

    duty_df = doc_data["duty_summary"]
    if duty_df.empty:
        st.info("No duty summary data")
        return

    duty = duty_df.iloc[0]

    # Duty breakdown in columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.number_input("BCD", value=float(duty["bcd"] or 0), format="%.2f", key="d_bcd")
        st.number_input("ACD", value=float(duty["acd"] or 0), format="%.2f", key="d_acd")
        st.number_input("SWS", value=float(duty["sws"] or 0), format="%.2f", key="d_sws")
        st.number_input("NCCD", value=float(duty["nccd"] or 0), format="%.2f", key="d_nccd")

    with col2:
        st.number_input("Add Duty", value=float(duty["add_duty"] or 0), format="%.2f", key="d_add")
        st.number_input("CVD", value=float(duty["cvd"] or 0), format="%.2f", key="d_cvd")
        st.number_input("IGST", value=float(duty["igst"] or 0), format="%.2f", key="d_igst")
        st.number_input("G.Cess", value=float(duty["g_cess"] or 0), format="%.2f", key="d_gcess")

    with col3:
        st.number_input("SG", value=float(duty["sg"] or 0), format="%.2f", key="d_sg")
        st.number_input("SAED", value=float(duty["saed"] or 0), format="%.2f", key="d_saed")
        st.number_input("GSIA", value=float(duty["gsia"] or 0), format="%.2f", key="d_gsia")
        st.number_input("TTA", value=float(duty["tta"] or 0), format="%.2f", key="d_tta")

    with col4:
        st.number_input("Health", value=float(duty["health"] or 0), format="%.2f", key="d_health")
        st.number_input("Interest", value=float(duty["interest"] or 0), format="%.2f", key="d_interest")
        st.number_input("Penalty", value=float(duty["penalty"] or 0), format="%.2f", key="d_penalty")
        st.number_input("Fine", value=float(duty["fine"] or 0), format="%.2f", key="d_fine")

    # Totals (highlighted)
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Duty", f"₹{duty['total_duty']:,.2f}")
    with col2:
        st.metric("Assessed Value", f"₹{duty['tot_ass_val']:,.2f}")
    with col3:
        st.metric("Total Amount", f"₹{duty['tot_amount']:,.2f}")


def render_manifest_section(doc_data):
    """Render manifest section"""
    st.subheader("📦 Manifest Details")

    manifest_df = doc_data["manifest"]
    if manifest_df.empty:
        st.info("No manifest data")
        return

    manifest = manifest_df.iloc[0]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.text_input("IGM No", value=manifest["igm_no"] or "", key="m_igm_no")
        st.text_input("IGM Date", value=str(manifest["igm_date"]) if manifest["igm_date"] else "", key="m_igm_date")

    with col2:
        st.text_input("GIGM No", value=manifest["gigm_no"] or "", key="m_gigm_no")
        st.text_input("GIGM Date", value=str(manifest["gigm_date"]) if manifest["gigm_date"] else "", key="m_gigm_date")

    with col3:
        st.text_input("MAWB No", value=manifest["mawb_no"] or "", key="m_mawb_no")
        st.text_input("HAWB No", value=manifest["hawb_no"] or "", key="m_hawb_no")

    with col4:
        st.number_input("Packages", value=int(manifest["pkg"] or 0), key="m_pkg")
        st.number_input("Gross Weight (kg)", value=float(manifest["gross_weight"] or 0), format="%.2f", key="m_weight")


def render_licences_section(doc_data):
    """Render licences table"""
    st.subheader("📜 Licence Details")

    lic_df = doc_data["licences"]
    if lic_df.empty:
        st.info("No licence data")
        return

    # Summary stats
    total_debit = lic_df["debit_value"].sum() if "debit_value" in lic_df else 0
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Licences", len(lic_df))
    with col2:
        st.metric("Total Debit Value", f"₹{total_debit:,.2f}")

    # Display as editable dataframe
    display_cols = ["item_sno", "lic_no", "lic_date", "code", "port", "debit_value", "qty", "uqc"]
    available_cols = [c for c in display_cols if c in lic_df.columns]

    st.dataframe(
        lic_df[available_cols],
        use_container_width=True,
        hide_index=True
    )


def render_json_view(doc_data):
    """Render raw JSON view for debugging"""
    st.subheader("🔍 Raw Data (JSON)")

    # Convert dataframes to dicts
    json_data = {}
    for key, df in doc_data.items():
        if not df.empty:
            json_data[key] = df.to_dict(orient="records")

    st.json(json_data)


def main():
    """Main application"""
    st.title("📋 Bill of Entry Validator")
    st.markdown("Review and validate OCR-extracted data from Bill of Entry documents")

    # Sidebar - document selection
    selected_doc = render_sidebar()

    if not selected_doc:
        st.info("👈 Select a document from the sidebar to begin")

        # Show import option
        st.markdown("---")
        st.subheader("Import New Document")

        uploaded_json = st.file_uploader("Upload parsed JSON file", type=["json"])
        if uploaded_json:
            try:
                json_data = json.load(uploaded_json)

                if st.button("Import to Database"):
                    from src.pipeline import insert_boe_from_json
                    success = insert_boe_from_json(json_data, DB_PATH)
                    if success:
                        st.success("Document imported successfully!")
                        st.rerun()
                    else:
                        st.error("Import failed - document may already exist")
            except Exception as e:
                st.error(f"Error parsing JSON: {e}")

        return

    # Load document details
    doc_data = get_document_details(selected_doc)

    # Tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📄 Header", "💰 Duty Summary", "📦 Manifest", "📜 Licences", "🔍 JSON"
    ])

    with tab1:
        render_header_section(doc_data)

    with tab2:
        render_duty_section(doc_data)

    with tab3:
        render_manifest_section(doc_data)

    with tab4:
        render_licences_section(doc_data)

    with tab5:
        render_json_view(doc_data)

    # Save button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("💾 Save Changes", type="primary"):
            st.success("Changes saved! (Note: Edit functionality coming soon)")
    with col2:
        if st.button("🗑️ Delete Document", type="secondary"):
            if st.session_state.get("confirm_delete"):
                from src.pipeline import BoEDatabaseManager
                manager = BoEDatabaseManager(DB_PATH)
                if manager.delete_document(selected_doc):
                    st.success(f"Deleted {selected_doc}")
                    st.rerun()
            else:
                st.session_state["confirm_delete"] = True
                st.warning("Click again to confirm deletion")


if __name__ == "__main__":
    main()
