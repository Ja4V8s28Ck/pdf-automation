import streamlit as st
from utils.database import init_db
from utils.ui import render_sidebar

st.set_page_config(
    page_title="PDF Automation - Manufacturing Ops",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
render_sidebar()

st.title("Manufacturing Document Digitization")
st.markdown(
    """
    Upload handwritten manufacturing operational documents and convert them 
    into structured, reviewable digital records with AI-powered extraction.
    """
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.page_link("pages/01_upload.py", label="**Upload Documents**\n\nUpload images or PDFs", width="stretch")

with col2:
    st.page_link("pages/02_review.py", label="**Review & Edit**\n\nVerify and correct AI-extracted data", width="stretch")

with col3:
    st.page_link("pages/03_dashboard.py", label="**Dashboard**\n\nView operational analytics and insights", width="stretch")

with col4:
    st.page_link("pages/04_history.py", label="**Search & History**\n\nSearch past records and uploads", width="stretch")

st.divider()

st.subheader("Quick Start")
st.markdown(
    """
    1. **Upload** a manufacturing document (image or PDF)
    2. Click **Run AI Extraction** to extract data using Gemini Vision API
    3. **Review** the extracted data, edit if needed, and save
    4. Check the **Dashboard** for operational insights
    5. Use **Search & History** to find past records
    """
)

st.divider()
st.caption("Built with Streamlit + Google Gemini API + SQLite")
