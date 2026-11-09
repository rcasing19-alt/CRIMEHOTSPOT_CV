import streamlit as st
import pandas as pd

def apply_theme():
    st.markdown("""
    <style>
    .block-container {padding-top: 1.4rem; padding-bottom: 2rem; max-width: 1500px;}
    [data-testid="stMetric"] {background: #f5f7fb; border: 1px solid #e5eaf2;
      padding: 14px 16px; border-radius: 12px;}
    [data-testid="stMetricLabel"] {font-size: .88rem;}
    h1, h2, h3 {letter-spacing: -.02em;}
    </style>
    """, unsafe_allow_html=True)

def render_sidebar_filters(df):
    with st.sidebar:
        st.divider()
        st.subheader("Analysis filters")
        valid_dates = df["date"].dropna()
        if valid_dates.empty:
            st.caption("No valid dates found; date filter unavailable.")
            date_range = None
        else:
            dmin, dmax = valid_dates.min().date(), valid_dates.max().date()
            date_range = st.date_input("Incident date range", value=(dmin, dmax), min_value=dmin, max_value=dmax)
        areas = sorted(df["location_label"].dropna().astype(str).unique())
        area_choice = st.multiselect("Barangay", areas, default=[])
        types = sorted(df["offense_type"].dropna().astype(str).unique())
        type_choice = st.multiselect("Offense type", types, default=[])
    out = df.copy()
    if date_range and isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        out = out[out["date"].notna()]
        out = out[out["date"].dt.date.between(date_range[0], date_range[1])]
    if area_choice:
        out = out[out["location_label"].isin(area_choice)]
    if type_choice:
        out = out[out["offense_type"].isin(type_choice)]
    return out
