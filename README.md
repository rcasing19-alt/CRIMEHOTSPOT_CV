# Crime Intelligence & Decision Support Dashboard

A modular Streamlit application refactored from the supplied Crime Occurrence Analysis notebook.

## Run locally

1. Install Python 3.10 or newer.
2. Open a terminal in this project directory.
3. Create and activate a virtual environment (recommended).
4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Start the application:

   ```bash
   streamlit run app.py
   ```

6. Upload one or more `.xlsx` or `.xls` workbooks in the sidebar.

## Modules

- `app.py` — application entry point, navigation, shared data loading and filters
- `modules/data_loader.py` — workbook ingestion, column normalization and preprocessing
- `modules/ui.py` — theme and common filters
- `modules/overview.py` — executive indicators
- `modules/geographic.py` — interactive Folium maps (OpenStreetMap tiles), point clusters and density heatmap
- `modules/patterns.py` — temporal and offense pattern charts
- `modules/barangay.py` — barangay comparison and profiles
- `modules/forecasting.py` — chronological holdout and area-level forecasting
- `modules/data_quality.py` — missingness, coordinate, and duplicate checks
- `modules/reports.py` — CSV and Excel exports
- `modules/charts.py` — reusable Plotly chart functions

## Expected fields

The application recognizes common variants of:
`barangay`, `date`, `time`, `stage`, `offense`, `offense_type`, `latitude`, `longitude`.

All non-empty worksheets in uploaded workbooks are combined. Additional source columns are retained in the cleaned data. Victim and suspect columns are excluded from default exports.

## Maps

The Geographic Intelligence module uses Folium with OpenStreetMap tiles and `streamlit-folium`. Internet access is required in the browser to load map tiles. Records without plausible Philippine coordinates are not mapped but remain included in non-map analyses.

If maps appear blank:
- confirm the device/browser has internet access;
- allow access to `tile.openstreetmap.org` and your organization's map-tile policy;
- verify that latitude and longitude are decimal degrees, not swapped;
- inspect invalid coordinates in Data Quality.

## Analytical safeguards

- A reported-record count is not the true incidence of crime.
- A high count may reflect population size, reporting access, recording practices, or enforcement activity.
- Forecasts are area/month planning estimates, not individual predictions or proof of future crime.
- Relative forecast tiers are dataset-relative, not universal threat categories.
- Validate model usefulness against local operational knowledge before resource decisions.
- Do not use this dashboard to target individuals or protected groups.

## Performance

Data ingestion is cached. Charts and maps are rendered only on the selected module. Forecasting runs only when its page is opened. For large datasets, consider aggregating incident points by coordinate or date range before displaying all markers.
