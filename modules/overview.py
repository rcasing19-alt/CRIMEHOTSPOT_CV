import streamlit as st
import pandas as pd
from .charts import monthly_trend, horizontal_bar

def render(df, all_df):
    st.header("Executive Overview")
    st.caption("Management snapshot of reported incidents in the selected period.")
    total = len(df)
    mapped = int(df.get("valid_coordinates", pd.Series(False, index=df.index)).sum())
    areas = df["location_label"].nunique() if total else 0
    offenses = df["offense_type"].nunique() if total else 0
    date_valid = df["date"].notna().sum() if total else 0
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Reported records", f"{total:,}")
    c2.metric("Barangays represented", f"{areas:,}")
    c3.metric("Offense categories", f"{offenses:,}")
    c4.metric("Valid coordinates", f"{mapped:,}", f"{mapped/total:.1%} of records" if total else "—")
    c5.metric("Valid incident dates", f"{date_valid:,}", f"{date_valid/total:.1%} of records" if total else "—")
    st.plotly_chart(monthly_trend(df), use_container_width=True)
    left, right = st.columns(2)
    with left:
        st.plotly_chart(horizontal_bar(df["offense_type"].value_counts(), "Most reported offense types",
                                       y_title="Offense type"), use_container_width=True)
    with right:
        st.plotly_chart(horizontal_bar(df["location_label"].value_counts(), "Barangays with most reports",
                                       y_title="Barangay"), use_container_width=True)
    st.subheader("Management signals")
    if total:
        peak = df["offense_type"].value_counts()
        area = df["location_label"].value_counts()
        st.write(f"- Most frequently recorded offense type: **{peak.index[0]}** ({peak.iloc[0]:,} records).")
        st.write(f"- Highest-count barangay in the filtered data: **{area.index[0]}** ({area.iloc[0]:,} records).")
        st.write("- Interpret counts alongside population, reporting access, enforcement activity, and data completeness.")
    else:
        st.info("No records match the selected filters.")
