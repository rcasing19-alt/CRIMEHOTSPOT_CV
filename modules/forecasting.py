import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

FEATURES = ["lag_1", "lag_2", "lag_3", "rolling_mean_3", "month", "month_sin", "month_cos"]

def build_panel(df):
    d = df.dropna(subset=["date"]).copy()
    if d.empty:
        return None, pd.DataFrame()
    d["month_start"] = d["date"].dt.to_period("M").dt.to_timestamp()
    counts = d.groupby(["location_label", "month_start"]).size().rename("count").reset_index()
    panel = counts.pivot(index="month_start", columns="location_label", values="count")
    months = pd.date_range(panel.index.min(), panel.index.max(), freq="MS")
    return panel.reindex(months).fillna(0), counts

def render(df):
    st.header("Predictive Analytics")
    st.caption("Area-level planning estimates only. Forecasts are not predictions about individuals and should not determine enforcement actions by themselves.")
    panel, _ = build_panel(df)
    if panel is None or len(panel) < 6:
        st.warning("At least six distinct months of valid records are recommended before attempting a forecast.")
        return
    min_history = st.slider("Minimum monthly history per barangay", 3, min(12, len(panel)), 3)
    rows = []
    for area in panel.columns:
        s = panel[area]
        if len(s) < min_history:
            continue
        for i in range(3, len(s)):
            dt = s.index[i]
            rows.append({"area": area, "month_start": dt, "target": float(s.iloc[i]),
                         "lag_1": float(s.iloc[i-1]), "lag_2": float(s.iloc[i-2]),
                         "lag_3": float(s.iloc[i-3]), "rolling_mean_3": float(s.iloc[i-3:i].mean()),
                         "month": dt.month, "month_sin": np.sin(2*np.pi*dt.month/12),
                         "month_cos": np.cos(2*np.pi*dt.month/12)})
    train_data = pd.DataFrame(rows)
    if len(train_data) < 20 or train_data["month_start"].nunique() < 4:
        st.warning("Insufficient area-month observations for a defensible model. Add more history.")
        return
    unique_months = sorted(train_data.month_start.unique())
    cutoff = unique_months[max(1, int(len(unique_months)*.8))]
    train = train_data[train_data.month_start < cutoff]
    test = train_data[train_data.month_start >= cutoff]
    if len(train) < 10 or test.empty:
        st.warning("A chronological holdout could not be created.")
        return
    model = RandomForestRegressor(n_estimators=250, min_samples_leaf=2, random_state=42,
                                  n_jobs=-1, max_features=.9)
    model.fit(train[FEATURES], train.target)
    pred = np.maximum(0, model.predict(test[FEATURES]))
    baseline = np.maximum(0, test.lag_1.to_numpy())
    c1, c2, c3 = st.columns(3)
    c1.metric("Holdout MAE", f"{mean_absolute_error(test.target, pred):.2f}")
    c2.metric("Baseline MAE", f"{mean_absolute_error(test.target, baseline):.2f}")
    c3.metric("Holdout records", f"{len(test):,}")
    st.caption(f"Chronological holdout: {pd.Timestamp(test.month_start.min()).date()} to {pd.Timestamp(test.month_start.max()).date()}")
    final_model = RandomForestRegressor(n_estimators=250, min_samples_leaf=2, random_state=42,
                                        n_jobs=-1, max_features=.9)
    final_model.fit(train_data[FEATURES], train_data.target)
    next_month = panel.index.max() + pd.offsets.MonthBegin(1)
    forecast_rows = []
    for area in panel.columns:
        s = panel[area]
        if len(s) < 3:
            continue
        forecast_rows.append({"area": area, "month_start": next_month,
            "lag_1": float(s.iloc[-1]), "lag_2": float(s.iloc[-2]), "lag_3": float(s.iloc[-3]),
            "rolling_mean_3": float(s.iloc[-3:].mean()), "month": next_month.month,
            "month_sin": np.sin(2*np.pi*next_month.month/12),
            "month_cos": np.cos(2*np.pi*next_month.month/12)})
    future = pd.DataFrame(forecast_rows)
    if future.empty:
        st.info("No barangay has enough history to forecast.")
        return
    future["estimated_records"] = np.maximum(0, final_model.predict(future[FEATURES]))
    q50, q80 = future.estimated_records.quantile([.5, .8])
    future["relative_tier"] = np.select(
        [future.estimated_records >= q80, future.estimated_records >= q50],
        ["Higher relative estimate", "Moderate relative estimate"], default="Lower relative estimate")
    future = future.sort_values("estimated_records", ascending=False)
    st.subheader(f"Estimated reported records — {next_month:%B %Y}")
    fig = px.bar(future.head(20).sort_values("estimated_records"), x="estimated_records",
                 y="area", color="relative_tier", orientation="h",
                 title="Relative area-level forecast ranking")
    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(future, use_container_width=True, hide_index=True)
    st.warning("Forecast tiers are relative to this dataset's forecast distribution, not universal danger levels. Review uncertainty, population, reporting practices, and local context.")
