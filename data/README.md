# Source data setup

The derived outputs required by the Streamlit dashboard are included in `outputs/`. The original source extracts used to regenerate the analysis are not included in this public repository. Some are large (the EU ETS data package alone is roughly 500 MB), and source components may have reuse terms separate from the compilation that supplied them.

## Expected local layout

Download or prepare the source files under a local folder, then point `CARBON_LEAK_DATA_DIR` to that folder. Do not commit the raw extracts to this repository.

```text
data-root/
├── OECD*.csv
├── eutl_data_package_2026-07-21/
│   ├── datapackage.json
│   ├── installations.csv
│   ├── compliance.csv
│   ├── nace_mappings.csv
│   └── ...
└── external_data/
    ├── eurostat_aea_eu27_ghg_2008_on.csv
    ├── oecd_ghg_embodied_bilateral_trade_eu27_2008_2022.csv
    ├── oecd_ghg_embodied_bilateral_trade_eu27_exports_2008_2022.csv
    ├── prodcom_eu27_target_sectors_2008_2022.csv
    ├── eurostat_aea_intensity_eu27_ghg_output_currentprices.csv
    ├── eurostat_hicp_eu27_annual_2008_2022.csv
    ├── eurostat_eu27_domestic_ppi_annual_C17_C24_2008_2022.csv
    ├── eurostat_nuts_country_boundaries_2024_3035.geojson
    ├── offsetsdb_carbonplan_snapshot_2026-06-01.csv.zip
    └── ...
```

The notebook records the queries, filters and local manifests for most downloaded extracts. The included dashboard remains usable without these inputs because it reads the processed project outputs.

## Main source families

| Source family | Used for | Where to obtain or verify |
| --- | --- | --- |
| EU ETS data package, dated 2026-07-21 | Registry and installation context in the notebook | [euetsinfo data package](https://github.com/jabrell/euetsinfo); its package metadata lists upstream sources and reuse conditions. |
| Eurostat PRODCOM | Sold production values and quantities | [PRODCOM information](https://ec.europa.eu/eurostat/en/web/prodcom/information-data); source API metadata is also recorded in the project manifests. |
| Eurostat Air Emissions Accounts | Resident-industry greenhouse-gas emissions and intensity | [Air Emissions Accounts metadata](https://ec.europa.eu/eurostat/cache/metadata/en/env_ac_ainah_r2_sims.htm). |
| Eurostat Comext | Extra-EU goods trade by product and partner | [International trade in goods](https://ec.europa.eu/eurostat/web/international-trade-in-goods/information-data). |
| OECD GHG Footprint Indicators, 2025 edition | Emissions embodied in bilateral trade | [OECD dataset](https://www.oecd.org/en/data/datasets/greenhouse-gas-footprint-indicators.html); query URLs and filters are in the local OECD manifests. |
| Eurostat price indices | Convert selected value series to 2020 euros | [HICP overview](https://ec.europa.eu/eurostat/en/web/hicp); the notebook’s local manifests describe the PPI and HICP extracts. |
| CarbonPlan OffsetsDB snapshot, 2026-06-01 | EU-hosted project and credit registry records | [OffsetsDB data access](https://offsets-db-data.readthedocs.io/en/stable/data-access.html) and [processing notes](https://offsets-db-data.readthedocs.io/en/stable/data-processing.html). |
| Project validation and monitoring reports | Examples of project-reported leakage accounting | Source links and page references are included in the report and `outputs/offset_project_leakage_report_examples.csv`. |

## Important reuse note

The EU ETS data package states that its CC BY 4.0 license covers the authors’ compilation and transformations, while original source data remain subject to their providers’ terms. Check the current terms for each source before redistributing raw files. This repository includes derived analysis outputs for review and dashboard use, not the large raw source datasets.
