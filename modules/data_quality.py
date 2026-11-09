import streamlit as st
import pandas as pd

def render(df):
    st.header("Data Quality & Audit")
    quality = pd.DataFrame({
        "Missing values": df.isna().sum(),
        "Missing (%)": (df.isna().mean()*100).round(2),
        "Data type": df.dtypes.astype(str),
    }).sort_values("Missing (%)", ascending=False)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total rows", f"{len(df):,}")
    c2.metric("Possible duplicate rows", f"{int(df.possible_duplicate.sum()):,}")
    c3.metric("Valid Philippine coordinates", f"{int(df.valid_coordinates.sum()):,}")
    st.subheader("Field completeness")
    st.dataframe(quality, use_container_width=True)
    st.subheader("Source workbook summary")
    if "source_file" in df:
        source = df.groupby("source_file").agg(
            records=("source_file", "size"),
            valid_dates=("date", "count"),
            valid_coordinates=("valid_coordinates", "sum"),
            possible_duplicate_rows=("possible_duplicate", "sum"),
        ).reset_index()
        st.dataframe(source, use_container_width=True, hide_index=True)
    st.subheader("Records requiring review")
    issue = df[df.date.isna() | ~df.valid_coordinates | df.possible_duplicate]
    st.dataframe(issue.head(1000), use_container_width=True, hide_index=True)
    st.caption("Duplicate flags are for review only; records are not automatically deleted. Coordinate plausibility bounds are tuned for the Philippines.")
