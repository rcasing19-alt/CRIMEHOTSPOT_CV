import re
from datetime import time
from io import BytesIO

import numpy as np
import pandas as pd
import streamlit as st

ALIASES = {
    "date_committed": "date", "datecommitted": "date", "date": "date",
    "time_committed": "time", "timecommitted": "time", "time": "time",
    "stages_of_felony": "stage", "stage_of_felony": "stage", "stageoffelony": "stage",
    "offense_type": "offense_type", "offensetype": "offense_type",
    "latitude": "latitude", "lat": "latitude",
    "longitude": "longitude", "lng": "longitude", "lon": "longitude",
    "victims": "victim", "victim": "victim", "suspect": "suspect",
    "barangay": "barangay", "offense": "offense",
}

def normalize_column(name):
    key = re.sub(r"[^a-z0-9]+", "_", str(name).strip().lower()).strip("_")
    return ALIASES.get(key, key)

@st.cache_data(show_spinner="Reading and combining Excel worksheets...")
def _read_workbooks(file_payloads):
    frames = []
    for filename, payload in file_payloads:
        book = pd.ExcelFile(BytesIO(payload))
        for sheet in book.sheet_names:
            part = pd.read_excel(book, sheet_name=sheet)
            if part.empty:
                continue
            part.columns = [normalize_column(c) for c in part.columns]
            part["source_file"] = filename
            part["source_sheet"] = sheet
            frames.append(part)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True, sort=False)

def load_uploaded_files(uploaded_files):
    payloads = tuple((f.name, f.getvalue()) for f in uploaded_files)
    return _read_workbooks(payloads)

def parse_time(value):
    if pd.isna(value):
        return pd.NaT
    if isinstance(value, time):
        return pd.to_datetime(value.strftime("%H:%M:%S"), format="%H:%M:%S", errors="coerce")
    if isinstance(value, (int, float)) and 0 <= float(value) < 1:
        seconds = int(round(float(value) * 86400)) % 86400
        return pd.to_datetime(f"{seconds//3600:02d}:{(seconds%3600)//60:02d}:{seconds%60:02d}",
                              format="%H:%M:%S", errors="coerce")
    return pd.to_datetime(str(value).strip(), errors="coerce")

def prepare_data(raw):
    if raw.empty:
        return raw.copy()
    df = raw.copy()
    required = ["barangay", "date", "time", "stage", "offense", "offense_type", "latitude", "longitude"]
    for col in required:
        if col not in df.columns:
            df[col] = np.nan

    for col in ["barangay", "stage", "offense", "offense_type"]:
        df[col] = df[col].astype("string").str.strip().replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})

    df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=False)
    df["time_parsed"] = df["time"].apply(parse_time)
    df["hour"] = df["time_parsed"].dt.hour
    df["day_of_week"] = df["date"].dt.day_name()
    df["day_num"] = df["date"].dt.dayofweek
    df["month"] = df["date"].dt.month
    df["year"] = df["date"].dt.year
    df["year_month"] = df["date"].dt.to_period("M").astype("string")
    df["quarter"] = df["date"].dt.quarter
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    key_cols = ["barangay", "date", "time", "stage", "offense", "offense_type", "latitude", "longitude"]
    df["possible_duplicate"] = df.duplicated(subset=key_cols, keep=False)
    # Philippine bounding box is a plausibility check, not a substitute for local validation.
    df["valid_coordinates"] = (
        df["latitude"].between(4.5, 21.5) &
        df["longitude"].between(116.0, 127.5)
    )
    df["location_label"] = df["barangay"].fillna("Unknown / missing barangay").astype(str)
    for col in ["offense_type", "offense", "stage"]:
        df[col] = df[col].fillna(f"Unknown / missing {col.replace('_', ' ')}")
    return df
