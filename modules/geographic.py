import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap, MarkerCluster
from streamlit_folium import st_folium

def render(df):
    st.header("Geographic Intelligence")
    st.caption("Maps use records with plausible Philippine coordinates. Unmapped records remain in all non-map analyses.")
    mapped = df[df["valid_coordinates"]].dropna(subset=["latitude", "longitude"]).copy()
    if mapped.empty:
        st.warning("No valid coordinates are available for the current filter selection.")
        st.info("Check latitude/longitude fields and coordinate quality in the Data Quality module.")
        return
    mode = st.radio("Map view", ["Incident points", "Density heatmap", "Barangay coordinate clusters"],
                    horizontal=True)
    center = [mapped["latitude"].median(), mapped["longitude"].median()]
    m = folium.Map(location=center, zoom_start=11, control_scale=True, tiles="OpenStreetMap")
    if mode == "Density heatmap":
        HeatMap(mapped[["latitude", "longitude"]].values.tolist(), radius=16, blur=18,
                min_opacity=0.25).add_to(m)
    elif mode == "Incident points":
        cluster = MarkerCluster(name="Reported incidents").add_to(m)
        for _, r in mapped.iterrows():
            popup = folium.Popup(
                f"<b>Barangay:</b> {r['location_label']}<br>"
                f"<b>Offense:</b> {r['offense_type']}<br>"
                f"<b>Date:</b> {r['date'].date() if pd.notna(r['date']) else 'Unknown'}",
                max_width=300)
            folium.CircleMarker([r["latitude"], r["longitude"]], radius=4,
                                color="#174a7e", fill=True, fill_opacity=.65,
                                popup=popup).add_to(cluster)
    else:
        grouped = mapped.groupby("location_label").agg(
            latitude=("latitude", "median"), longitude=("longitude", "median"),
            records=("location_label", "size")).reset_index()
        for _, r in grouped.iterrows():
            folium.CircleMarker([r.latitude, r.longitude],
                radius=max(5, min(22, 4 + r.records ** .5)),
                color="#b5473c", fill=True, fill_opacity=.55,
                popup=f"{r.location_label}: {r.records} mapped records").add_to(m)
    folium.LayerControl().add_to(m)
    st_folium(m, use_container_width=True, height=650, returned_objects=[])
    st.caption(f"Mapped records: {len(mapped):,} / filtered records: {len(df):,}. Coordinates are descriptive, not proof of neighborhood-level risk.")
    st.dataframe(mapped[["location_label", "date", "offense_type", "latitude", "longitude"]].head(500),
                 use_container_width=True, hide_index=True)
