from io import BytesIO
import streamlit as st
import pandas as pd

def render(filtered, all_df):
    st.header("Reports & Export")
    st.caption("Exports respect the active dashboard filters unless otherwise stated.")
    safe = filtered.drop(columns=[c for c in ["victim", "suspect"] if c in filtered.columns], errors="ignore")
    st.download_button("Download filtered records (CSV)", safe.to_csv(index=False).encode("utf-8-sig"),
                       "crime_records_filtered.csv", "text/csv", use_container_width=True)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        safe.to_excel(writer, sheet_name="filtered_records", index=False)
        filtered["offense_type"].value_counts().rename_axis("offense_type").reset_index(name="records").to_excel(
            writer, sheet_name="offense_summary", index=False)
        filtered["location_label"].value_counts().rename_axis("barangay").reset_index(name="records").to_excel(
            writer, sheet_name="barangay_summary", index=False)
        quality = pd.DataFrame({"missing_count": all_df.isna().sum(),
                                "missing_percent": (all_df.isna().mean()*100).round(2)})
        quality.to_excel(writer, sheet_name="data_quality")
    st.download_button("Download management workbook (Excel)", output.getvalue(),
                       "crime_intelligence_report.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       use_container_width=True)
    st.info("Review confidentiality and institutional data-sharing rules before distributing exported files.")
