import streamlit as st
st.set_page_config(page_title="Search & History")

import pandas as pd
from PIL import Image
from utils.ui import render_sidebar

render_sidebar()

from utils.database import (
    get_all_documents, bulk_get_extractions_with_flags,
)
from utils.config import FIELD_LABELS

st.title("🔍 Search & Upload History")

search_term = st.text_input("Search records", placeholder="Work order, employee, machine, or operation code...")

col1, col2, col3 = st.columns(3)
with col1:
    filter_status = st.selectbox(
        "Status",
        ["All", "pending_review", "reviewed", "flagged"],
        index=0,
    )
with col2:
    filter_doc = st.selectbox(
        "Document",
        ["All"] + [d.filename for d in get_all_documents()],
        index=0,
    )
with col3:
    st.write("")
    st.write("")
    if st.button("🔄 Refresh", width="stretch"):
        st.rerun()

records = bulk_get_extractions_with_flags(
    search=search_term if search_term else None
)

if filter_status != "All":
    records = [r for r in records if r["extraction"].status.value == filter_status]

if filter_doc != "All":
    records = [r for r in records if r["document"] and r["document"].filename == filter_doc]

if not records:
    st.info("No records found matching your criteria.")
    st.stop()

st.write(f"Found **{len(records)}** record(s)")

table_rows = []
for item in records:
    ext = item["extraction"]
    doc = item["document"]
    flags = item["flags"]
    confidence = ext.confidence_scores or {}
    avg_conf = sum(confidence.values()) / len(confidence) if confidence else 0

    table_rows.append({
        "ID": ext.id,
        "Document": doc.filename if doc else "Unknown",
        "Row": ext.row_index,
        "Date": ext.date or "—",
        "Shift": ext.shift or "—",
        "Employee": ext.employee_number or "—",
        "Operation": ext.operation_code or "—",
        "Machine": ext.machine_number or "—",
        "Work Order": ext.work_order_number or "—",
        "Quantity": ext.quantity_produced or "—",
        "Time": ext.time_taken or "—",
        "Confidence": f"{avg_conf:.0%}",
        "Status": ext.status.value,
        "Flags": len(flags),
    })

df = pd.DataFrame(table_rows)
st.dataframe(df, width="stretch", hide_index=True)

st.divider()
st.subheader("Document Details")

selected_id = st.number_input(
    "Enter Record ID to view details",
    min_value=1,
    step=1,
    format="%d",
)

if selected_id:
    records_filtered = [r for r in records if r["extraction"].id == selected_id]
    if records_filtered:
        item = records_filtered[0]
        ext = item["extraction"]
        doc = item["document"]
        flags = item["flags"]
        confidence = ext.confidence_scores or {}

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("Extracted Data")
            for field in ["date", "shift", "employee_number", "operation_code",
                          "machine_number", "work_order_number",
                          "quantity_produced", "time_taken"]:
                val = getattr(ext, field, "") or "—"
                conf = confidence.get(field, 0)
                conf_dot = (
                    '<span style="color:green;">\u25cf</span>'
                    if conf >= 0.8
                    else '<span style="color:orange;">\u25cf</span>'
                    if conf >= 0.5
                    else '<span style="color:red;">\u25cf</span>'
                )
                st.markdown(
                    f"**{FIELD_LABELS.get(field, field)}:** {val} {conf_dot} {conf:.0%}",
                    unsafe_allow_html=True,
                )

            st.subheader("Status")
            status_color = {
                "pending_review": "blue",
                "reviewed": "green",
                "flagged": "red",
            }
            st.markdown(
                f'<span style="color:{status_color.get(ext.status.value, "gray")};">\u25cf</span>'
                f" **{ext.status.value}**",
                unsafe_allow_html=True,
            )
            if ext.notes:
                st.write(f"**Notes:** {ext.notes}")

        with col2:
            st.subheader("Validation Flags")
            if flags:
                for flag in flags:
                    st.warning(f"**{FIELD_LABELS.get(flag.field, flag.field)}**: {flag.message}")
            else:
                st.success("No validation flags")

            if doc:
                st.subheader("Source Document")
                st.write(f"**Filename:** {doc.filename}")
                st.write(f"**Uploaded:** {doc.upload_date}")
                st.write(f"**Document Status:** {doc.status.value}")

                try:
                    image = Image.open(doc.filepath)
                    st.image(image, width="stretch", caption=doc.filename)
                except Exception:
                    st.info("Preview not available")
    else:
        st.warning("Record ID not found")
