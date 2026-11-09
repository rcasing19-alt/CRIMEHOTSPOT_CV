import streamlit as st
import plotly.express as px

def render(df):
    st.header("Barangay Intelligence")
    if df.empty:
        st.info("No records match the selected filters.")
        return
    summary = df.groupby("location_label").agg(
        reported_records=("location_label", "size"),
        offense_types=("offense_type", "nunique"),
        valid_coordinates=("valid_coordinates", "sum"),
        latest_record=("date", "max"),
    ).reset_index().sort_values("reported_records", ascending=False)
    st.subheader("Barangay comparison")
    fig = px.bar(summary.head(25).sort_values("reported_records"),
                 x="reported_records", y="location_label", orientation="h",
                 color="reported_records", title="Top barangays by reported records",
                 labels={"reported_records": "Records", "location_label": "Barangay"})
    fig.update_layout(template="plotly_white", margin=dict(l=20,r=20,t=55,b=20))
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(summary, use_container_width=True, hide_index=True)
    selected = st.selectbox("Inspect a barangay", summary["location_label"].tolist())
    subset = df[df["location_label"] == selected]
    st.subheader(f"Profile: {selected}")
    x, y, z = st.columns(3)
    x.metric("Reported records", f"{len(subset):,}")
    y.metric("Offense types", f"{subset['offense_type'].nunique():,}")
    z.metric("Records with coordinates", f"{int(subset['valid_coordinates'].sum()):,}")
    dist = subset["offense_type"].value_counts().rename_axis("Offense type").reset_index(name="Records")
    st.plotly_chart(px.pie(dist.head(10), names="Offense type", values="Records",
                           hole=.48, title="Offense composition"), use_container_width=True)
