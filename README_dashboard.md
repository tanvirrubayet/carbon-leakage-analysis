# EU Carbon Leakage Explorer

An interactive Streamlit dashboard for the EU27 exploratory carbon leakage analysis.

## Run locally

From the project folder, install the packages and launch Streamlit:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

The dashboard expects the project analysis files in `outputs/` and the existing charts in `outputs/visualizations/`.

## Pages

- **Start here** — overview of the four-indicator risk screen.
- **Industry signals** — endpoint changes and adjusted trend tests by NACE division.
- **Product explorer** — searchable product-level output/import screen.
- **Trade and imported carbon** — OECD-modelled embodied emissions in extra-EU imports and exports.
- **Money lens** — inflation-adjusted monetary context and illustrative shadow carbon value.
- **Carbon credit projects** — OffsetsDB issuance/retirement and project-reported leakage examples.
- **2030 scenarios** — conditional extensions of historical industry and embodied-trade trends.
- **Methods and glossary** — definitions, coverage caveats and evidence limits.

The dashboard is descriptive. A risk signal, credit transaction or project leakage estimate is not presented as causally established EU industrial leakage.
