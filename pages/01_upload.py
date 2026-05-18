import streamlit as st
st.set_page_config(page_title="Upload Documents")

import uuid
from PIL import Image
from utils.ui import render_sidebar

render_sidebar()

from utils.database import (
    add_document, add_extraction, update_document_status,
    get_document, get_extractions, add_validation_flag,
    DocumentStatus,
)
from utils.extraction import extract_from_image
from utils.validation import validate_extraction
from utils.config import UPLOAD_DIR

st.title("Upload Documents")

if "extracted_keys" not in st.session_state:
    st.session_state.extracted_keys = set()

uploaded_file = st.file_uploader(
    "Choose an image or PDF",
    type=["png", "jpg", "jpeg", "pdf"],
    help="Upload manufacturing operational documents for data extraction",
)

if uploaded_file is not None:
    file_key = f"{uploaded_file.name}_{uploaded_file.size}"
    file_bytes = uploaded_file.getvalue()
    mime_type = uploaded_file.type or "image/jpeg"
    already_extracted = file_key in st.session_state.extracted_keys

    st.success(f"Ready: {uploaded_file.name}")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Preview")
        if mime_type.startswith("image"):
            image = Image.open(uploaded_file)
            st.image(image, width="stretch")
        else:
            st.info("PDF preview not available in-browser")

    with col2:
        st.subheader("Extract Data")
        st.write(f"File: **{uploaded_file.name}**")
        st.write(f"Size: **{uploaded_file.size / 1024:.1f} KB**")

        if already_extracted:
            st.success("Extraction completed for this file.")
        else:
            if st.button("Run AI Extraction", type="primary", width="stretch"):
                file_ext = uploaded_file.name.rsplit(".", 1)[-1].lower()
                unique_name = f"{uuid.uuid4().hex}.{file_ext}"
                save_path = UPLOAD_DIR / unique_name

                with open(save_path, "wb") as f:
                    f.write(file_bytes)

                doc = add_document(uploaded_file.name, str(save_path), mime_type)

                with st.status("Extracting data...", expanded=True) as status:
                    try:
                        update_document_status(doc.id, DocumentStatus.PROCESSING)

                        status.write("Calling Gemini Vision API...")
                        results = extract_from_image(str(save_path))

                        if not results:
                            status.write("No records found in this document.")
                            update_document_status(doc.id, DocumentStatus.COMPLETED)
                            status.update(label="Complete - no records found", state="complete")
                        else:
                            status.write(f"Found {len(results)} record(s). Saving...")

                            existing = [
                                {"work_order_number": e.work_order_number or ""}
                                for e in get_extractions()
                            ]

                            for i, (row, confidence) in enumerate(results):
                                ext = add_extraction(
                                    document_id=doc.id,
                                    row_index=i + 1,
                                    data=row,
                                    confidence_scores=confidence,
                                )

                                vflags = validate_extraction(ext.id, row, existing)
                                for vf in vflags:
                                    add_validation_flag(
                                        ext.id, vf["field"], vf["issue_type"], vf["message"]
                                    )

                            update_document_status(doc.id, DocumentStatus.COMPLETED)
                            status.update(label="Extraction complete!", state="complete")

                        st.session_state.extracted_keys.add(file_key)
                        st.rerun()

                    except Exception as e:
                        update_document_status(doc.id, DocumentStatus.FAILED)
                        status.update(label="Extraction failed", state="error")
                        st.error(f"Error: {e}")

    st.divider()

st.subheader("Recent Uploads")
recent = get_extractions()[:5]
if recent:
    for ext in recent:
        doc_ref = get_document(ext.document_id)
        doc_name = doc_ref.filename if doc_ref else "Unknown"
        st.write(f"- **{doc_name}** (Row {ext.row_index}) -> Status: `{ext.status.value}`")
else:
    st.info("No uploads yet. Upload a document above.")
