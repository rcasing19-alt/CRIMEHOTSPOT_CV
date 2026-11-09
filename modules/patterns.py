import streamlit as st
from .charts import horizontal_bar, hour_day_heatmap, monthly_trend

def render(df):
    st.header("Crime Pattern Analysis")
    a, b = st.columns(2)
    with a:
        st.plotly_chart(hour_day_heatmap(df), use_container_width=True)
    with b:
        st.plotly_chart(horizontal_bar(df["day_of_week"].value_counts(), "Reports by day of week",
                                       y_title="Day"), use_container_width=True)
    c, d = st.columns(2)
    with c:
        st.plotly_chart(horizontal_bar(df["stage"].value_counts(), "Stage of felony",
                                       y_title="Stage"), use_container_width=True)
    with d:
        st.plotly_chart(horizontal_bar(df["offense"].value_counts(), "Most frequent offenses",
                                       y_title="Offense"), use_container_width=True)
    st.plotly_chart(monthly_trend(df), use_container_width=True)
    st.info("Time-based charts exclude records with missing or invalid date/time values. Counts represent reported records.")
