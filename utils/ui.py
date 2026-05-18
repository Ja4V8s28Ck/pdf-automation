import streamlit as st


def render_sidebar():
    st.sidebar.title("Manufacturing Ops")
    st.sidebar.markdown("---")

    st.sidebar.page_link("app.py", label="Home")
    st.sidebar.page_link("pages/01_upload.py", label="Upload")
    st.sidebar.page_link("pages/02_review.py", label="Review")
    st.sidebar.page_link("pages/03_dashboard.py", label="Dashboard")
    st.sidebar.page_link("pages/04_history.py", label="History")

    st.sidebar.markdown("---")
    st.sidebar.caption("PDF Automation v1.0")
