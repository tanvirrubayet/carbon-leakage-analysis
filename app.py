from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "outputs"
FIGURES = OUTPUTS / "carbon_leakage_figures"

st.set_page_config(
    page_title="EU Carbon Leakage Explorer",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY = "#17324D"
TEAL = "#167D8D"
BLUE = "#2878A5"
ORANGE = "#D97732"
GREEN = "#4B8F6C"
PALETTE = [TEAL, ORANGE, BLUE, GREEN, "#8967A8"]
SECTOR_NAMES = {
    "C17": "Paper and paper products",
    "C19": "Coke and refined petroleum products",
    "C20": "Chemicals and chemical products",
    "C23": "Other non-metallic mineral products",
    "C24": "Basic metals",
}
INDICATORS = {
    "production_million_2020_eur": ("EU sold production value", "€ billion, 2020 prices", 1000),
    "domestic_emissions_mt": ("EU industry emissions", "Mt CO₂e", 1),
    "extra_eu_import_million_2020_eur": ("Extra-EU import value", "€ billion, 2020 prices", 1000),
    "extra_eu_embodied_import_carbon_mtco2e": ("Emissions embodied in imports", "Mt CO₂e", 1),
}

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1380px;}
    h1, h2, h3 {color: var(--text-color); letter-spacing: -0.02em;}
    .eyebrow {color: var(--primary-color); text-transform: uppercase; letter-spacing: .13em;
      font-size: .76rem; font-weight: 700; margin-bottom: .2rem;}
    .lede {font-size: 1.08rem; line-height: 1.55; color: var(--text-color); opacity: .82; max-width: 950px;}
    .small-muted {color: var(--text-color); opacity: .72; font-size: .88rem;}
    div[data-testid="stMetric"] {background: var(--secondary-background-color); border: 1px solid var(--border-color, #D7E4E8);
      padding: .85rem 1rem; border-radius: 12px;}
    div[data-testid="stMetric"] [data-testid="stMetricLabel"] {color: var(--text-color); opacity: .78;}
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {color: var(--text-color);}
    .stAlert {border-radius: 10px;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_csv(filename: str) -> pd.DataFrame:
    path = OUTPUTS / filename
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def page_header(kicker: str, title: str, lede: str) -> None:
    st.markdown(f'<div class="eyebrow">{kicker}</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(f'<div class="lede">{lede}</div>', unsafe_allow_html=True)
    st.write("")


def show_missing(filename: str) -> bool:
    if not (OUTPUTS / filename).exists():
        st.warning(f"This view needs `{filename}` in the project `outputs` folder.")
        return True
    return False


def named_sector(code: str) -> str:
    return f"{code} · {SECTOR_NAMES.get(code, code)}"


def fmt_pct(value) -> str:
    return "Not available" if pd.isna(value) else f"{value:+.1f}%"


def chart_layout(fig, height=420, y_title=None):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=20, t=50, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Arial, sans-serif", color="#243746", size=12),
        legend_title_text="",
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=False, linecolor="#B7C6CE")
    fig.update_yaxes(gridcolor="#E7EEF1", zerolinecolor="#AEBCC4")
    if y_title:
        fig.update_yaxes(title=y_title)
    return fig


def download_frame(frame: pd.DataFrame, name: str, label="Download this data") -> None:
    st.download_button(
        label,
        data=frame.to_csv(index=False).encode("utf-8-sig"),
        file_name=name,
        mime="text/csv",
        use_container_width=False,
    )


with st.sidebar:
    st.markdown("## 🌍 Carbon leakage explorer")
    st.caption("EU27 industry, trade and carbon project evidence")
    page = st.radio(
        "Explore the analysis",
        [
            "Start here",
            "Industry signals",
            "Product explorer",
            "Trade and imported carbon",
            "Money lens",
            "Carbon credit projects",
            "2030 scenarios",
            "Methods and glossary",
        ],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("Historical industry data: 2008–2022")
    st.caption("Project registry snapshot: 1 June 2026")
    st.caption("Scenarios are conditional illustrations, not forecasts.")


if page == "Start here":
    page_header(
        "EU27 · Exploratory research",
        "Carbon leakage signals in EU industry",
        "Explore whether falling EU production and emissions coincide with rising imports and carbon embodied in those imports. The dashboard separates observed patterns, project-reported leakage and causal evidence.",
    )
    screen = load_csv("eu27_industry_leakage_screen_summary.csv")
    panel = load_csv("eu27_industry_leakage_screen_panel_2008_2022.csv")
    if screen.empty or panel.empty:
        st.error("The industry analysis files are missing from `outputs`.")
        st.stop()

    signal_count = int((screen["screen_label"] == "Four-direction endpoint signal").sum())
    projects = load_csv("eu27_hosted_credit_issued_retired_summary.csv")
    projects_row = projects.iloc[0] if not projects.empty else None
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Industry divisions screened", "5", help="C17, C19, C20, C23 and C24")
    m2.metric("Historical comparison", "2008–2022", help="Common period used for the four-indicator screen")
    m3.metric("Full endpoint patterns", str(signal_count), help="C20 and C23 have all four endpoint directions and data available")
    if projects_row is not None:
        m4.metric("EU-hosted credits retired", f"{projects_row['credits_retired_total']/1e6:.1f}m", help="Registry retirements in the OffsetsDB snapshot; not a leakage total")
    st.write("")

    col_chart, col_read = st.columns([1.65, 1], gap="large")
    with col_chart:
        st.subheader("A four-part screen")
        eligible = [c for c in ["C20", "C23", "C17", "C19", "C24"] if c in set(panel.sector)]
        selected = st.multiselect(
            "Choose sectors to compare",
            eligible,
            default=[c for c in ["C20", "C23"] if c in eligible],
            format_func=named_sector,
        )
        metric_columns = list(INDICATORS.keys())
        labels = [INDICATORS[c][0] for c in metric_columns]
        from plotly.subplots import make_subplots

        fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.07, subplot_titles=labels)
        for i, col in enumerate(metric_columns, start=1):
            for j, sector in enumerate(selected):
                data = panel.loc[panel.sector.eq(sector)].sort_values("year")
                index_col = f"{col}_index_2008_100"
                if index_col not in data:
                    continue
                fig.add_trace(
                    go.Scatter(
                        x=data.year,
                        y=data[index_col],
                        name=named_sector(sector),
                        legendgroup=sector,
                        showlegend=(i == 1),
                        mode="lines+markers",
                        line=dict(color=PALETTE[eligible.index(sector) % len(PALETTE)], width=2.5),
                        marker=dict(size=5),
                        connectgaps=False,
                        hovertemplate="%{x}: %{y:.0f}<extra></extra>",
                    ),
                    row=i,
                    col=1,
                )
            fig.add_hline(y=100, line_color="#97A8B2", line_dash="dot", row=i, col=1)
        fig.update_layout(height=760, margin=dict(l=0,r=10,t=55,b=5), paper_bgcolor="white", plot_bgcolor="white", font=dict(color="#243746"), legend_title_text="", hovermode="x unified")
        fig.update_yaxes(title="Index", gridcolor="#E7EEF1")
        fig.update_xaxes(title="Year", showgrid=False)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Each line starts at 100 in 2008. Values above 100 are higher than 2008; below 100 are lower. Missing lines mean the measure is unavailable for that sector.")
    with col_read:
        st.subheader("What stands out")
        st.markdown("**C20 · Chemicals** and **C23 · Other non-metallic mineral products** show all four expected endpoint directions from 2008 to 2022.")
        st.markdown("For both divisions, domestic emissions fell while extra-EU imports and imported embodied emissions rose. This is consistent with a possible risk signal.")
        st.info("The pattern does not establish that EU climate policy caused production to move abroad. Demand, prices, technology and other changes can also explain it.")
        st.subheader("Three evidence levels")
        st.markdown("1. **Descriptive risk signal** — observed patterns that merit follow-up.\n2. **Project-reported leakage** — calculations or statements in an individual carbon project’s reports.\n3. **Causally established leakage** — a demonstrated shift linked to a policy using a credible comparison. This dataset does not establish level 3.")
        st.subheader("How to explore")
        st.markdown("Use the left menu to examine industry and product patterns, trade emissions, project credit records, monetary context and conditional 2030 scenarios.")


elif page == "Industry signals":
    page_header("Observed industry data", "Industry signals", "Compare the four indicators for each broad EU industry division. Endpoint changes and year-by-year trend tests answer different questions, so both are shown.")
    files = ["eu27_industry_leakage_screen_panel_2008_2022.csv", "eu27_industry_leakage_screen_summary.csv", "eu27_industry_leakage_screen_trends.csv"]
    if any(show_missing(f) for f in files):
        st.stop()
    panel = load_csv(files[0]); summary = load_csv(files[1]); trends = load_csv(files[2])
    choices = [c for c in SECTOR_NAMES if c in set(panel.sector)]
    sector = st.selectbox("Industry division", choices, format_func=named_sector, key="industry_sector")
    df = panel.loc[panel.sector.eq(sector)].sort_values("year")
    first, last = df.iloc[0], df.iloc[-1]
    srow = summary.loc[summary.sector.eq(sector)].iloc[0]
    st.markdown(f"### {named_sector(sector)}")
    if sector == "C19":
        st.warning("C19 has only one product code in the production extract. Treat the production result as partial, not a full-sector estimate.")
    cards = st.columns(4)
    for card, col in zip(cards, INDICATORS):
        v0, v1 = first[col], last[col]
        pct = (v1 / v0 - 1) * 100 if pd.notna(v0) and pd.notna(v1) and v0 != 0 else float("nan")
        label, unit, divisor = INDICATORS[col]
        card.metric(label, fmt_pct(pct), help=f"2008 to 2022 endpoint change. Values are in {unit}.")

    left, right = st.columns([1.55, 1], gap="large")
    with left:
        metric = st.selectbox("Chart measure", list(INDICATORS), format_func=lambda c: INDICATORS[c][0], key="industry_metric")
        mode = st.radio("Display", ["Change since 2008", "Observed values"], horizontal=True, key="industry_mode")
        plot_col = f"{metric}_index_2008_100" if mode == "Change since 2008" else metric
        unit = "Index (2008 = 100)" if mode == "Change since 2008" else INDICATORS[metric][1]
        chart = px.line(df, x="year", y=plot_col, markers=True, title=INDICATORS[metric][0], labels={"year":"Year", plot_col:unit})
        chart.update_traces(line=dict(color=TEAL, width=3), marker=dict(size=7))
        if mode == "Change since 2008": chart.add_hline(y=100, line_dash="dot", line_color="#8395A1", annotation_text="2008 level")
        st.plotly_chart(chart_layout(chart, 390, unit), use_container_width=True)
        st.caption("The line describes how the series moved. It does not identify why it moved.")
    with right:
        st.subheader("Endpoint pattern")
        label = srow["screen_label"]
        if label == "Four-direction endpoint signal":
            st.success("All four expected directions are present at the endpoints.")
        elif "Incomplete" in str(label):
            missing = [
                INDICATORS[col][0]
                for col in INDICATORS
                if pd.isna(first[col]) or pd.isna(last[col])
            ]
            missing_text = ", ".join(missing) if missing else "one or more endpoint measures"
            st.warning(
                f"The four-part screen is incomplete for {sector} because comparable "
                f"2008 or 2022 data are missing for: {missing_text}. Missing data do not mean zero emissions."
            )
        else:
            st.info("The endpoint pattern is partial or mixed.")
        st.write(f"**Screen label:** {label}")
        trend = trends.loc[trends.sector.eq(sector)].copy()
        trend["Measure"] = trend.indicator.map(lambda x: INDICATORS.get(x, (x, "", 1))[0])
        trend["Trend result"] = trend["trend_result"]
        trend["Adjusted q value"] = trend["q_bh"].map(lambda x: "—" if pd.isna(x) else f"{x:.3g}")
        st.subheader("Trend checks across all years")
        st.dataframe(trend[["Measure", "Trend result", "Adjusted q value"]], hide_index=True, use_container_width=True)
        st.caption("A q value below 0.05 marks a statistically clear monotonic trend after multiple-test adjustment. These tests do not account for year-to-year autocorrelation and do not show cause.")
    with st.expander("View the underlying annual values"):
        st.dataframe(df[["year"] + list(INDICATORS.keys())], hide_index=True, use_container_width=True)
        download_frame(df, f"{sector.lower()}_annual_indicators.csv")


elif page == "Product explorer":
    page_header("Product detail", "Product explorer", "Search matched products and compare EU sold quantities with extra-EU import values. A product pattern can identify a follow-up question, but the two measures are not directly equivalent.")
    if show_missing("eu27_broad_matched_product_summary.csv"): st.stop()
    products = load_csv("eu27_broad_matched_product_summary.csv")
    coverage = load_csv("eu27_broad_match_coverage_summary.csv")
    sectors = [c for c in SECTOR_NAMES if c in set(products.sector)]
    c1,c2,c3 = st.columns([1,1,1.6])
    with c1: sector=st.selectbox("Industry division",sectors,format_func=named_sector,key="product_sector")
    with c2: pattern=st.selectbox("Endpoint pattern",["All patterns"]+sorted(products.endpoint_pattern.dropna().unique().tolist()))
    with c3: query=st.text_input("Find a product",placeholder="For example: polypropylene")
    df=products.loc[products.sector.eq(sector)].copy()
    if pattern!="All patterns": df=df.loc[df.endpoint_pattern.eq(pattern)]
    if query.strip(): df=df.loc[df.product.astype(str).str.contains(query.strip(),case=False,na=False)]
    cov=coverage.loc[coverage.sector.eq(sector)]
    if not cov.empty:
        row=cov.iloc[0]; a,b,c=st.columns(3)
        a.metric("Products in supplied extract",f"{int(row.all_prodcom_codes):,}")
        b.metric("Strictly matched products",f"{int(row.matched_prodcom_codes):,}")
        c.metric("Matched share of 2022 recorded value",fmt_pct(row.matched_share_of_recorded_value_2022_pct))
    st.info("The horizontal comparison uses percentage changes: production is sold quantity; imports are trade value. A matching direction is a screening signal, not proof of import substitution or carbon leakage.")
    left,right=st.columns([1.35,1],gap="large")
    with left:
        plot=df.dropna(subset=["production_change_2008_2022_pct","extra_eu_import_change_2008_2022_pct"]).copy()
        if not plot.empty:
            plot["Trend status"] = plot["both_clear_expected_trends"].map({True:"Both expected trends clear",False:"Not both trends clear"})
            chart=px.scatter(plot,x="production_change_2008_2022_pct",y="extra_eu_import_change_2008_2022_pct",color="Trend status",hover_name="product",hover_data={"prodcom_code":True,"endpoint_pattern":True,"production_change_2008_2022_pct":":.1f","extra_eu_import_change_2008_2022_pct":":.1f"},color_discrete_map={"Both expected trends clear":TEAL,"Not both trends clear":"#A9B8C1"},labels={"production_change_2008_2022_pct":"EU sold quantity change (%)","extra_eu_import_change_2008_2022_pct":"Extra-EU import value change (%)"},title="Product-level endpoint comparison")
            chart.add_vline(x=0,line_dash="dot",line_color="#7A8B95"); chart.add_hline(y=0,line_dash="dot",line_color="#7A8B95")
            st.plotly_chart(chart_layout(chart,480),use_container_width=True)
            st.caption("Lower-left quadrant means both measures fell. Upper-left has lower output with higher import value; this is one candidate screen, not a causal test.")
        else: st.info("No products with both endpoint changes match these filters.")
    with right:
        st.subheader("Products in this view")
        st.metric("Rows matching filters",f"{len(df):,}")
        st.dataframe(df[["prodcom_code","product","production_change_2008_2022_pct","extra_eu_import_change_2008_2022_pct","endpoint_pattern","both_clear_expected_trends"]].rename(columns={"prodcom_code":"PRODCOM code","product":"Product","production_change_2008_2022_pct":"EU output change (%)","extra_eu_import_change_2008_2022_pct":"Extra-EU imports value change (%)","endpoint_pattern":"Endpoint screen","both_clear_expected_trends":"Both trends clear"}),hide_index=True,use_container_width=True,height=480)
        download_frame(df,"filtered_product_screen.csv")
    st.caption("Coverage is uneven across products. A strict code match and complete production quantities are required; emissions embodied in imports are not available at this product level.")


elif page == "Trade and imported carbon":
    page_header("Global supply-chain context", "Trade and imported carbon", "Compare emissions attributed to products imported into and exported from the EU27. The difference helps describe the trade footprint; it does not attribute the pattern to EU climate policy.")
    if show_missing("eu27_embodied_emissions_trade_balance_2008_2022.csv"): st.stop()
    trade=load_csv("eu27_embodied_emissions_trade_balance_2008_2022.csv")
    sectors=[c for c in ["C19","C20","C23"] if c in set(trade.sector)]
    sector=st.selectbox("Industry division",sectors,format_func=named_sector,key="trade_sector")
    df=trade.loc[trade.sector.eq(sector)].sort_values("year")
    first=df.iloc[0]; last=df.iloc[-1]
    c=st.columns(3)
    c[0].metric("2008 import minus export balance",f"{first.net_embodied_trade_mt:.1f} Mt CO₂e")
    c[1].metric("2022 import minus export balance",f"{last.net_embodied_trade_mt:.1f} Mt CO₂e")
    c[2].metric("Change in balance",f"{last.net_embodied_trade_mt-first.net_embodied_trade_mt:+.1f} Mt CO₂e")
    f=go.Figure()
    f.add_trace(go.Scatter(x=df.year,y=df.imported_embodied_ghg_mt,name="Embodied in imports",mode="lines+markers",line=dict(color=ORANGE,width=3),hovertemplate="%{x}: %{y:.1f} Mt CO₂e<extra></extra>"))
    f.add_trace(go.Scatter(x=df.year,y=df.exported_embodied_ghg_mt,name="Embodied in exports",mode="lines+markers",line=dict(color=BLUE,width=3),hovertemplate="%{x}: %{y:.1f} Mt CO₂e<extra></extra>"))
    f.add_trace(go.Scatter(x=df.year,y=df.net_embodied_trade_mt,name="Imports minus exports",mode="lines+markers",line=dict(color=NAVY,width=2,dash="dash"),hovertemplate="%{x}: %{y:.1f} Mt CO₂e<extra></extra>"))
    st.plotly_chart(chart_layout(f,500,"Modelled embodied emissions (Mt CO₂e)"),use_container_width=True)
    st.markdown("**How to read it:** when the balance is above zero, the OECD model attributes more emissions to extra-EU imports than to extra-EU exports for this broad sector.")
    st.warning("Embodied emissions are model estimates along supply chains. A positive balance is not the EU consumption footprint, a direct measurement at each facility, or proof of leakage caused by policy.")
    with st.expander("See the annual trade-footprint data"):
        st.dataframe(df.rename(columns={"imported_embodied_ghg_mt":"Import embodied emissions (Mt CO₂e)","exported_embodied_ghg_mt":"Export embodied emissions (Mt CO₂e)","net_embodied_trade_mt":"Imports minus exports (Mt CO₂e)"}),hide_index=True,use_container_width=True)
        download_frame(df,f"{sector.lower()}_embodied_trade_balance.csv")


elif page == "Money lens":
    page_header("Economic scale", "Putting emissions on a euro scale", "The project includes inflation-adjusted production values and an illustrative carbon-price comparison. The money figures give scale; they are not a monetary estimate of carbon leakage.")
    st.subheader("Production value in constant 2020 euros")
    st.markdown("The broad-sector gross-output series was reconstructed from emissions intensity and deflated with producer-price indices. It is separate from PRODCOM sold-production value and should not be described as the amount of production lost to leakage.")
    gross=FIGURES/"08-real-gross-output-2020-euros.png"
    if gross.exists(): st.image(str(gross),caption="Reconstructed real gross output by broad industry division, in 2020 euros.",use_container_width=True)
    st.subheader("A hypothetical value for emissions")
    st.markdown("The analysis applies the 2022 average EU allowance price of **€80.18 per tonne of CO₂e** to emissions quantities, then restates the result in 2020 euros. This is a common-price illustration, sometimes called a shadow carbon value.")
    shadow=FIGURES/"09-shadow-carbon-value-2020-euros.png"
    if shadow.exists(): st.image(str(shadow),caption="Illustrative common-price value of emissions, restated in 2020 euros.",use_container_width=True)
    st.info("This is not the actual cost paid by EU companies, the cost of imported carbon, carbon-credit revenue, or money transferred abroad. It does not account for free allocation, company-specific obligations, energy costs or different carbon prices outside the EU.")
    st.markdown("### Selected examples")
    st.dataframe(pd.DataFrame([
        {"Industry":"C20 · domestic emissions","2008":"€14.25bn","2022":"€9.25bn","Change":"−35.1%"},
        {"Industry":"C20 · embodied emissions in imports","2008":"€9.01bn","2022":"€9.94bn","Change":"+10.4%"},
        {"Industry":"C23 · domestic emissions","2008":"€18.04bn","2022":"€12.47bn","Change":"−30.9%"},
        {"Industry":"C23 · embodied emissions in imports","2008":"€2.42bn","2022":"€3.67bn","Change":"+51.9%"},
    ]),hide_index=True,use_container_width=True)


elif page == "Carbon credit projects":
    page_header("Carbon-credit records", "Credits and project-reported leakage", "Credits issued and retired describe registry transactions. Project leakage reports describe accounting inside particular carbon projects. Neither is a direct measure of EU industrial leakage.")
    needed=["eu27_hosted_credit_transactions_by_year.csv","eu27_hosted_credit_issued_retired_summary.csv","offset_project_leakage_report_examples.csv"]
    if any(show_missing(f) for f in needed): st.stop()
    annual=load_csv(needed[0]); totals=load_csv(needed[1]).iloc[0]; examples=load_csv(needed[2])
    c=st.columns(4)
    c[0].metric("Projects hosted in EU27",f"{int(totals.eu27_hosted_projects):,}")
    c[1].metric("Countries hosting projects","21")
    c[2].metric("Credits issued",f"{totals.credits_issued_total/1e6:.2f}m")
    c[3].metric("Credits retired",f"{totals.credits_retired_total/1e6:.2f}m")
    st.caption("OffsetsDB snapshot: 1 June 2026. EU27 refers to project host location, not the credit buyer. The 2026 transaction year is partial.")
    annual=annual.sort_values("year").copy(); annual["Issued (million credits)"]=annual.credits_issued/1e6; annual["Retired (million credits)"]=annual.credits_retired/1e6
    f=go.Figure()
    f.add_trace(go.Bar(x=annual.year,y=annual["Issued (million credits)"],name="Issued",marker_color=BLUE,hovertemplate="%{x}: %{y:.2f} million<extra>Issued</extra>"))
    f.add_trace(go.Bar(x=annual.year,y=annual["Retired (million credits)"],name="Retired",marker_color=GREEN,hovertemplate="%{x}: %{y:.2f} million<extra>Retired</extra>"))
    f.update_layout(barmode="group",title="Annual credit registry activity",xaxis_title="Year",yaxis_title="Millions of credits")
    st.plotly_chart(chart_layout(f,430),use_container_width=True)
    st.markdown("**Issued** means units were created in the registry after the programme’s accounting steps. **Retired** means units were taken permanently out of circulation, often for a claim or requirement. Neither number alone proves the amount of additional global climate benefit.")
    st.divider()
    st.subheader("What project reports say about leakage")
    view=examples.rename(columns={"project":"Project","activity":"Credited activity","host_in_EU27":"Host country","reported_leakage_tCO2e":"Reported leakage (tCO₂e)","leakage_factor_pct":"Leakage factor (%)","evidence_period":"Accounting period","evidence_status":"Evidence status","what_the_report_means":"Plain-language interpretation"})
    keep=[c for c in ["Project","Credited activity","Host country","Reported leakage (tCO₂e)","Leakage factor (%)","Accounting period","Evidence status","Plain-language interpretation"] if c in view.columns]
    display=view[keep].copy()
    leakage_col="Reported leakage (tCO₂e)"
    factor_col="Leakage factor (%)"
    if leakage_col in display:
        numeric=pd.to_numeric(display[leakage_col],errors="coerce")
        display[leakage_col]=numeric.map(lambda x: f"{x:,.1f}" if pd.notna(x) else "Not reported in source")
    if factor_col in display:
        numeric=pd.to_numeric(display[factor_col],errors="coerce")
        display[factor_col]=numeric.map(lambda x: f"{x:.1f}%" if pd.notna(x) else "Not reported in source")
    st.dataframe(display,hide_index=True,use_container_width=True)
    st.caption("“Not reported in source” means the reviewed report did not provide a numeric value for that field; it does not mean zero. These examples use different project methods and time periods, so do not add their figures together or rank projects by the reported values. A leakage factor is a percentage used in an accounting method, not a tonnage.")
    with st.expander("What does project type mean?"):
        st.write("It names the activity that the project credits: for example, sustainable agriculture or soil carbon, improved forest management, afforestation and reforestation, or mine methane capture. The category does not tell us by itself whether activity shifted elsewhere or whether emissions rose beyond the project boundary.")


elif page == "2030 scenarios":
    page_header("Conditional scenarios", "If historical trends continued to 2030", "The scenarios extend historical growth rates over three different time windows. They show how sensitive a simple trend extension can be; they are not predictions of what will happen.")
    paths_file="eu27_2030_scenario_paths.csv"; balance_file="eu27_2030_embodied_trade_balance_paths.csv"; summary_file="eu27_2030_scenario_summary.csv"
    if any(show_missing(f) for f in [paths_file,balance_file,summary_file]): st.stop()
    paths=load_csv(paths_file); bal=load_csv(balance_file); summary=load_csv(summary_file)
    a,b=st.columns(2)
    with a: sector=st.selectbox("Industry division",["C20","C23"],format_func=named_sector,key="scenario_sector")
    subset=paths.loc[paths.sector.eq(sector)]
    indicators=subset[["indicator","indicator_label"]].drop_duplicates()
    with b: indicator=st.selectbox("Measure",indicators.indicator.tolist(),format_func=lambda x: indicators.loc[indicators.indicator.eq(x),"indicator_label"].iloc[0],key="scenario_indicator")
    data=subset.loc[subset.indicator.eq(indicator)].copy()
    f=px.line(data,x="year",y="index_2022_100",color="scenario",line_dash="observed_or_projected",markers=False,labels={"year":"Year","index_2022_100":"Index (2022 = 100)","scenario":"Historical pace","observed_or_projected":"Observed or projected"},title=f"{named_sector(sector)} · {indicators.loc[indicators.indicator.eq(indicator),'indicator_label'].iloc[0]}")
    f.add_hline(y=100,line_dash="dot",line_color="#8799A4",annotation_text="2022 level")
    st.plotly_chart(chart_layout(f,470,"Index (2022 = 100)"),use_container_width=True)
    st.warning("The trend lines are conditional extensions. They do not include future policies, technology, energy prices, demand, capacity changes or uncertainty intervals.")
    tab=summary.loc[summary.sector.eq(sector)&summary.indicator.eq(indicator)].copy()
    if not tab.empty:
        st.subheader("2030 scenario values")
        show=tab[["scenario","trend_start_year","trend_end_year","annual_compound_change_pct","value_2030","index_2030_2022_100","unit"]].rename(columns={"scenario":"Historical window","trend_start_year":"Start year","trend_end_year":"End year","annual_compound_change_pct":"Annual change","value_2030":"2030 level","index_2030_2022_100":"2030 index (2022 = 100)","unit":"Underlying measure unit"})
        show["Annual change"]=tab["annual_compound_change_pct"].map(lambda x: "Not available" if pd.isna(x) else f"{x:+.2f}%")
        show["2030 level"]=tab["value_2030"].map(lambda x: "Not available" if pd.isna(x) else f"{x:,.1f}")
        show["2030 index (2022 = 100)"]=tab["index_2030_2022_100"].map(lambda x: "Not available" if pd.isna(x) else f"{x:.1f}")
        st.dataframe(show,hide_index=True,use_container_width=True)
        st.caption("The index is dimensionless: 100 represents the observed 2022 level. “2030 level” uses the underlying measure unit shown in the last column.")
    st.divider()
    st.subheader("Emissions embodied in imports minus exports")
    sectors_bal=[c for c in ["C19","C20","C23"] if c in set(bal.sector)]
    bs=st.selectbox("Trade-balance division",sectors_bal,format_func=named_sector,key="scenario_balance_sector")
    bd=bal.loc[bal.sector.eq(bs)].copy()
    bf=px.line(bd,x="year",y="net_imports_mtco2e",color="scenario",line_dash="observed_or_projected",labels={"year":"Year","net_imports_mtco2e":"Imports minus exports (Mt CO₂e)","scenario":"Historical pace","observed_or_projected":"Observed or projected"},title=f"{named_sector(bs)} · embodied-emissions trade balance")
    st.plotly_chart(chart_layout(bf,410,"Mt CO₂e"),use_container_width=True)
    st.caption("Imports and exports are projected separately, then subtracted. Different historical windows produce different results. A positive balance is not proof of leakage.")
    download_frame(bd,f"{bs.lower()}_2030_trade_balance_scenarios.csv")


else:
    page_header("Definitions and limitations", "Methods and glossary", "The dashboard is a descriptive research tool. Use these notes to understand what each measure means and what conclusions the data can support.")
    st.subheader("How the leakage-risk screen works")
    st.markdown("The broad-sector screen compares four movements from 2008 to 2022: **EU production value down**, **EU production-side emissions down**, **extra-EU import value up**, and **modelled emissions embodied in those imports up**. When all four endpoint directions are present, the dashboard labels the result a potential descriptive signal.")
    st.markdown("Endpoint comparisons are paired with one-sided Spearman rank trend tests and Benjamini–Hochberg adjustment for multiple comparisons. These tests check whether a series generally moved in the expected direction over time. They do not account for year-to-year autocorrelation and do not identify cause.")
    st.subheader("Data boundaries")
    for title,body in [
        ("Different output measures","PRODCOM sold-production value is not a complete measure of total physical output. Import value is not import quantity. Product-level charts compare their percentage changes for screening only."),
        ("Production-side and embodied emissions","Eurostat Air Emissions Accounts describe emissions associated with resident industries. OECD embodied emissions are model estimates allocated through supply chains. They are related perspectives, not interchangeable totals."),
        ("Incomplete coverage","C19 production coverage is especially limited. Embodied imports are not available for C17 and C24 in the common sector screen. Product matches cover only a subset of codes."),
        ("OffsetsDB is separate","Credits issued and retired and leakage described in project reports refer to carbon project records. They are not measurements of leakage in the EU industrial sectors screened here."),
        ("Causal evidence","A causal claim would need to connect a policy or intervention to a specific shift in production and emissions, with a credible estimate of what would have happened otherwise. The current dataset does not do this."),
        ("2030 scenarios","The scenarios extrapolate past average trends under selected time windows. No probabilities or confidence intervals are provided; future drivers are not modelled.")]:
        with st.expander(title): st.write(body)
    st.subheader("Industry codes")
    st.dataframe(pd.DataFrame([{"Code":k,"Industry":v} for k,v in SECTOR_NAMES.items()]),hide_index=True,use_container_width=True)
    st.caption("NACE is the EU classification of economic activities. C24 covers basic metals, including steel and other metals.")
    st.subheader("Glossary")
    glossary={
        "Carbon leakage":"Emissions rising outside a jurisdiction in connection with climate policy there, for example when production shifts to a place with weaker constraints or imports replace domestic goods.",
        "CO₂ equivalent (CO₂e)":"A common unit that expresses different greenhouse gases according to their warming effect relative to carbon dioxide.",
        "Mt CO₂e":"Megatonnes of carbon dioxide equivalent. One megatonne is one million metric tonnes.",
        "Embodied emissions":"Emissions generated throughout the supply chain to make a product and attributed to it through accounting or modelling.",
        "Extra-EU trade":"Trade between EU27 and countries outside the EU27.",
        "NACE":"The EU classification of economic activities. C20, for example, is an industry division, not a product code.",
        "PRODCOM":"Eurostat manufactured-goods statistics. Sold production means goods made and sold or invoiced during the period.",
        "CN code":"Combined Nomenclature product code used in EU trade statistics.",
        "Issued credit":"A registry unit created after the programme’s issuance requirements are met. This alone does not prove an additional global reduction.",
        "Retired credit":"A credit permanently taken out of circulation in a registry, often to support a claim or requirement.",
        "Counterfactual":"An estimate of what would have happened without the policy, project or event being studied.",
        "Deflation":"Adjusting money values for price changes so years can be compared in the prices of a reference year.",
        "2020 euros":"Money values restated to 2020 price levels; the original transaction need not have occurred in 2020.",
        "HICP":"Harmonised Index of Consumer Prices, Eurostat’s comparable measure of consumer-price inflation.",
        "EU ETS":"European Union Emissions Trading System, the EU cap-and-trade system for covered greenhouse-gas emissions.",
        "Carbon intensity":"Emissions per unit of output, such as tonnes CO₂e per tonne of product.",
        "Trend window":"The years used to estimate a trend. A different window can result in a different scenario.",
        "Import dependency":"How much domestic use relies on imports. The simple exploratory ratio here omits several market flows.",
    }
    for term,definition in glossary.items():
        with st.expander(term): st.write(definition)
    st.subheader("Data files behind this dashboard")
    st.markdown("The dashboard reads the analysis CSVs and figure images in the project `outputs` folder. The notebook remains the full record of data preparation and analysis.")
