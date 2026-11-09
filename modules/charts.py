import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

LAYOUT = dict(template="plotly_white", margin=dict(l=20, r=20, t=55, b=20),
              font=dict(family="Arial", size=12), title_font_size=17)

def monthly_trend(df):
    d = df.dropna(subset=["date"]).copy()
    if d.empty:
        return go.Figure().update_layout(title="No valid date records", **LAYOUT)
    s = d.groupby(d["date"].dt.to_period("M")).size().rename("Reported records").reset_index()
    s["Month"] = s["date"].astype(str)
    fig = px.line(s, x="Month", y="Reported records", markers=True,
                  title="Monthly reported incident trend")
    fig.update_layout(**LAYOUT)
    return fig

def horizontal_bar(series, title, x_title="Reported records", y_title=""):
    s = series.sort_values().tail(15)
    fig = px.bar(x=s.values, y=s.index.astype(str), orientation="h", title=title,
                 labels={"x": x_title, "y": y_title})
    fig.update_layout(**LAYOUT)
    return fig

def hour_day_heatmap(df):
    d = df.dropna(subset=["hour"])
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    if d.empty:
        return go.Figure().update_layout(title="No valid time records", **LAYOUT)
    pivot = d.pivot_table(index="day_of_week", columns="hour", values="offense",
                          aggfunc="count", fill_value=0).reindex(order).reindex(columns=range(24), fill_value=0)
    fig = px.imshow(pivot, aspect="auto", title="Reported incidents by weekday and hour",
                    labels={"x": "Hour", "y": "Day", "color": "Records"})
    fig.update_layout(**LAYOUT)
    return fig
