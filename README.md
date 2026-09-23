# EU Carbon Leakage Signals Explorer

An exploratory EU27 research project on carbon-leakage risk signals in energy- and emissions-intensive industries. It combines production, emissions, extra-EU trade and modelled embodied emissions, then presents the results in an interactive Streamlit dashboard.

**Research conclusion:** the available data identify descriptive risk signals, especially in chemicals (NACE C20) and other non-metallic mineral products (C23). They do not establish that EU climate policy caused production to move abroad. The 2030 results are conditional trend scenarios, not forecasts.

## Explore the dashboard

The dashboard uses the analysis outputs included in this repository. It does not need the original source extracts to run.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

The dashboard includes:

- **Start here** — the four-indicator industry screen and how to interpret it.
- **Industry signals** — endpoint changes and statistical trend checks by division.
- **Product explorer** — searchable product-level output and import screening.
- **Trade and imported carbon** — modelled emissions embodied in imports and exports.
- **Money lens** — inflation-adjusted production context and illustrative carbon values.
- **Carbon credit projects** — registry issuance and retirement plus project-reported leakage examples.
- **2030 scenarios** — historical trend extensions with different time windows.
- **Methods and glossary** — definitions, data coverage and limits on interpretation.

## Research report

The plain-language report is available at [`outputs/carbon_leakage_research_report.docx`](outputs/carbon_leakage_research_report.docx). It covers the research question, methods, findings, project examples, 2030 scenarios and glossary.

## Repository contents

```text
app.py                                      Streamlit dashboard
requirements.txt                            Python dependencies
notebooks/carbon_credits_and_leakage_exploration.ipynb
                                            Full exploratory analysis notebook
outputs/                                    Derived analysis tables and figures used by the app
outputs/carbon_leakage_research_report.docx  Research report
data/README.md                              Source data inventory and setup notes
```

## Data and reproducibility

The analysis covers EU27 countries and five broad NACE divisions: C17 paper, C19 coke and refined petroleum, C20 chemicals, C23 other non-metallic mineral products, and C24 basic metals. The common historical screen covers 2008–2022. C24 includes steel and other metals; the project is not steel-only.

The dashboard reads the derived CSVs and figures committed under `outputs/`. The notebook also uses original source extracts that are not committed: the full EU ETS package is about 500 MB, and several upstream sources have their own reuse conditions. See [`data/README.md`](data/README.md) for the file layout, provenance and local setup. Once those inputs are obtained, set `CARBON_LEAK_DATA_DIR` to their root folder before opening and running the notebook.

The notebook expects this layout beneath that data root:

```text
data-root/
├── OECD*.csv
├── eutl_data_package_2026-07-21/
└── external_data/
```

For PowerShell, for example:

```powershell
$env:CARBON_LEAK_DATA_DIR = 'D:\carbon-leak-data'
jupyter lab
```

## Interpretation guide

This project distinguishes three levels of evidence:

1. **Descriptive risk signal:** observed industry patterns are consistent with possible leakage and merit follow-up.
2. **Project-reported leakage:** a carbon project reports a leakage estimate, factor or pathway assessment under its own method.
3. **Causally established leakage:** evidence links a policy or intervention to displaced production and emissions elsewhere using a credible counterfactual. The current analysis does not establish this level.

The sector trend checks use one-sided Spearman rank tests with Benjamini–Hochberg adjustment. They do not account for serial correlation. OECD embodied-emissions values are model estimates. Credit issuance and retirement are registry events, not leakage totals. The 2030 scenarios extend historical trends and do not include future policy, technology, prices or uncertainty intervals.

## Sources

- [European Commission carbon leakage overview](https://climate.ec.europa.eu/areas-action/carbon-markets/eu-emissions-trading-system-eu-ets/free-allocation/carbon-leakage_en)
- [Eurostat PRODCOM](https://ec.europa.eu/eurostat/en/web/prodcom/information-data) and [international trade in goods](https://ec.europa.eu/eurostat/web/international-trade-in-goods/information-data)
- [OECD greenhouse-gas footprint indicators](https://www.oecd.org/en/data/datasets/greenhouse-gas-footprint-indicators.html)
- [CarbonPlan OffsetsDB data access](https://offsets-db-data.readthedocs.io/en/stable/data-access.html)
- [EU ETS data package and attribution](https://github.com/jabrell/euetsinfo)

## Citation

Tanvir Rubayet. *EU Carbon Leakage Signals Explorer*. Exploratory analysis and Streamlit dashboard, 2026.

The current repository does not declare an open-source software license. Source datasets and project reports remain subject to their providers’ terms.
