import streamlit as st
from modules.data_loader import load_uploaded_files, prepare_data
from modules.ui import apply_theme, render_sidebar_filters
from modules import overview, geographic, patterns, barangay, forecasting, data_quality, reports

st.set_page_config(
    page_title="Crime Intelligence | Decision Support",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_theme()

st.title("Crime Intelligence & Decision Support")
st.caption("Evidence-led monitoring of reported incidents | Management dashboard")

with st.sidebar:
    st.header("Data workspace")
    uploads = st.file_uploader(
        "Upload Excel workbooks",
        type=["xlsx", "xls"],
        accept_multiple_files=True,
        help="Upload one or more workbooks. All non-empty worksheets are combined.",
    )
    st.caption("Expected fields: barangay, date, time, offense, offense type, stage, latitude, longitude.")
    st.divider()
    page = st.radio(
        "Navigate",
        [
            "Executive Overview",
            "Geographic Intelligence",
            "Crime Pattern Analysis",
            "Barangay Intelligence",
            "Predictive Analytics",
            "Data Quality",
            "Reports & Export",
        ],
        label_visibility="collapsed",
    )

if not uploads:
    st.info("Upload one or more Excel workbooks in the sidebar to open the dashboard.")
    st.markdown("""
    ### What this dashboard provides
    - Executive indicators and incident trends
    - Interactive incident, density, and hotspot maps
    - Offense, time-of-day, and day-of-week analysis
    - Barangay comparisons and area profiles
    - Optional next-month area-level forecasting
    - Data quality checks and downloadable outputs
    """)
    st.warning("No source data is bundled with this application. Upload your authorized datasets to begin.")
    st.stop()

try:
    raw = load_uploaded_files(uploads)
    df = prepare_data(raw)
except Exception as exc:
    st.error(f"Unable to process the uploaded workbook(s): {exc}")
    st.stop()

if df.empty:
    st.warning("The uploaded workbooks contain no usable records.")
    st.stop()

filtered = render_sidebar_filters(df)
st.sidebar.caption(f"{len(filtered):,} records in current filter selection")

if page == "Executive Overview":
    overview.render(filtered, df)
elif page == "Geographic Intelligence":
    geographic.render(filtered)
elif page == "Crime Pattern Analysis":
    patterns.render(filtered)
elif page == "Barangay Intelligence":
    barangay.render(filtered)
elif page == "Predictive Analytics":
    forecasting.render(df)
elif page == "Data Quality":
    data_quality.render(df)
elif page == "Reports & Export":
    reports.render(filtered, df)
