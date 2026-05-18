import streamlit as st
st.set_page_config(page_title="Review Extractions")

from utils.ui import render_sidebar

render_sidebar()

from utils.database import (
    get_extractions, get_extraction, get_document,
    update_extraction, get_validation_flags, clear_validation_flags,
    add_validation_flag,
)
from utils.validation import validate_extraction
from utils.config import FIELD_LABELS, EXTRACTION_FIELDS

st.title("Review & Edit Extracted Data")

status_filter = st.selectbox(
    "Filter by status",
    ["All", "pending_review", "reviewed", "flagged"],
    index=0,
)

search = st.text_input("Search by work order, employee, machine, or operation code")

status_val = None if status_filter == "All" else status_filter
search_val = search if search else None
extractions = get_extractions(status=status_val, search=search_val)

if not extractions:
    st.info("No records found matching your criteria.")
    st.stop()

st.write(f"Showing **{len(extractions)}** record(s)")

for ext in extractions:
    doc = get_document(ext.document_id)
    flags = get_validation_flags(ext.id)
    confidence = ext.confidence_scores or {}

    with st.container(border=True):
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"**Row {ext.row_index}** - Document: `{doc.filename if doc else 'Unknown'}`")
        with col2:
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
        with col3:
            if st.button("Edit", key=f"edit_{ext.id}"):
                st.session_state[f"editing_{ext.id}"] = True

        if flags:
            with st.expander(f"Validation Flags ({len(flags)})", expanded=True):
                for flag in flags:
                    st.warning(f"**{FIELD_LABELS.get(flag.field, flag.field)}**: {flag.message}")

        if st.session_state.get(f"editing_{ext.id}", False):
            with st.form(key=f"form_{ext.id}"):
                st.subheader(f"Edit Record #{ext.id}")

                cols = st.columns(2)
                data = {}
                for idx, field in enumerate(EXTRACTION_FIELDS):
                    col = cols[idx % 2]
                    label = FIELD_LABELS.get(field, field)
                    current_val = getattr(ext, field, "") or ""
                    conf = confidence.get(field, 0)

                    conf_label = f" ({conf:.0%} confidence)" if conf > 0 else " (low confidence)"
                    data[field] = col.text_input(
                        f"{label}{conf_label}",
                        value=current_val,
                        key=f"input_{ext.id}_{field}",
                    )

                col1, col2 = st.columns(2)
                with col1:
                    saved = st.form_submit_button("Save Changes", type="primary", width="stretch")
                with col2:
                    cancelled = st.form_submit_button("Cancel", width="stretch")

                if saved:
                    update_extraction(ext.id, data)
                    clear_validation_flags(ext.id)
                    existing = [
                        {"work_order_number": e.work_order_number or ""}
                        for e in get_extractions()
                        if e.id != ext.id
                    ]
                    new_flags = validate_extraction(ext.id, data, existing)
                    for vf in new_flags:
                        add_validation_flag(ext.id, vf["field"], vf["issue_type"], vf["message"])
                    st.session_state[f"editing_{ext.id}"] = False
                    st.success("Saved!")
                    st.rerun()

                if cancelled:
                    st.session_state[f"editing_{ext.id}"] = False
                    st.rerun()
        else:
            cols = st.columns(4)
            for idx, field in enumerate(EXTRACTION_FIELDS):
                col_idx = idx % 4
                val = getattr(ext, field, "") or "—"
                conf = confidence.get(field, 0)
                label = FIELD_LABELS.get(field, field)

                flag_for_field = [f for f in flags if f.field == field]
                flag_icon = " !" if flag_for_field else ""

                with cols[col_idx]:
                    st.markdown(f"**{label}**{flag_icon}")
                    st.write(val)
                    if conf > 0:
                        conf_dot = (
                            '<span style="color:green;">\u25cf</span>'
                            if conf >= 0.8
                            else '<span style="color:orange;">\u25cf</span>'
                            if conf >= 0.5
                            else '<span style="color:red;">\u25cf</span>'
                        )
                        st.markdown(f"{conf_dot} {conf:.0%}", unsafe_allow_html=True)
