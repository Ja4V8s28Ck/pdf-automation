import streamlit as st
st.set_page_config(page_title="Dashboard")

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.ui import render_sidebar

render_sidebar()

from utils.database import get_dashboard_stats, bulk_get_extractions_with_flags
from utils.config import FIELD_LABELS

st.title("Dashboard & Analytics")

stats = get_dashboard_stats()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Uploads", stats["total_documents"])
with col2:
    st.metric("Total Records", stats["total_extractions"])
with col3:
    st.metric("Validation Flags", stats["total_validation_flags"], delta_color="inverse")
with col4:
    st.metric("Total Quantity", int(stats["total_quantity"]))

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Records by Status")
    status_data = pd.DataFrame({
        "Status": ["Pending Review", "Reviewed", "Flagged"],
        "Count": [
            stats["pending_count"],
            stats["reviewed_count"],
            stats["flagged_count"],
        ],
    })
    fig = px.bar(
        status_data, x="Status", y="Count",
        color="Status",
        color_discrete_map={
            "Pending Review": "#f39c12",
            "Reviewed": "#27ae60",
            "Flagged": "#e74c3c",
        },
    )
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, width="stretch")

with col2:
    st.subheader("Shift-wise Distribution")
    shift_data = pd.DataFrame({
        "Shift": [f"Shift {s}" for s in stats["shift_counts"].keys()],
        "Count": list(stats["shift_counts"].values()),
    })
    if not shift_data.empty and shift_data["Count"].sum() > 0:
        fig = px.pie(shift_data, values="Count", names="Shift", hole=0.4)
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("No shift data available yet")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Machine-wise Summary")
    machine_data = pd.DataFrame({
        "Machine": list(stats["machine_counts"].keys()),
        "Records": list(stats["machine_counts"].values()),
    })
    if not machine_data.empty:
        machine_data = machine_data.sort_values("Records", ascending=True)
        fig = px.bar(
            machine_data, y="Machine", x="Records",
            orientation="h", color="Records",
            color_continuous_scale="Blues",
        )
        fig.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("No machine data available yet")

with col2:
    st.subheader("Validation Issues Breakdown")
    records_data = bulk_get_extractions_with_flags()
    issue_counts = {}
    for item in records_data:
        for flag in item["flags"]:
            issue_type = flag.issue_type
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1

    if issue_counts:
        issue_df = pd.DataFrame({
            "Issue Type": list(issue_counts.keys()),
            "Count": list(issue_counts.values()),
        })
        fig = px.bar(
            issue_df, x="Issue Type", y="Count",
            color="Issue Type", color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("No validation issues found")

st.divider()

st.subheader("Recent Activity")
recent = bulk_get_extractions_with_flags()
if recent:
    rows = []
    for item in recent[:10]:
        ext = item["extraction"]
        doc = item["document"]
        rows.append({
            "Document": doc.filename if doc else "Unknown",
            "Work Order": ext.work_order_number or "—",
            "Machine": ext.machine_number or "—",
            "Shift": ext.shift or "—",
            "Quantity": ext.quantity_produced or "—",
            "Status": ext.status.value,
            "Flags": len(item["flags"]),
        })
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
else:
    st.info("No activity yet")
