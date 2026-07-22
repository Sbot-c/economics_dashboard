"""
Mexico Economics Dashboard
===========================
Data sources (all bundled in Mexico_Economics_Data.xlsx, same folder as this file):
  1. Mexico_Economics.docx          -> GDP components (C, I, G, X, M) from UN Data
  2. ECONOMICS_GRAPHS_Sparsh.ipynb  -> Population, Labor Force Rates, CPI/Inflation charts
  3. Mexico_Economics_Presentation.pptx (slides 1-13, Intro through Technology & AI)
                                     -> GDP growth, unemployment, inflation, fiscal policy,
                                        monetary policy, reforms, tech & AI

Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Mexico Economics Dashboard",
    page_icon="🇲🇽",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY = "#1F3864"
ACCENT = "#2E75B6"
RED = "#C0392B"
GREEN = "#2E8B57"
GOLD = "#C9A227"
GRAY = "#7F8C8D"

st.markdown(
    f"""
    <style>
    .main {{ background-color: #FAFBFC; }}
    h1, h2, h3 {{ color: {NAVY}; }}
    div[data-testid="stMetric"] {{
        background-color: #FFFFFF;
        border: 1px solid #E3E8EF;
        border-radius: 10px;
        padding: 14px 16px 8px 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}
    .source-note {{
        font-size: 0.80rem;
        color: #6B7280;
        font-style: italic;
        margin-top: -6px;
    }}
    .section-blurb {{
        font-size: 0.98rem;
        color: #33414F;
        margin-bottom: 0.6rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# DATA LAYER — every series below traces to the docx, the notebook, or the
# PPT slides (1-13). Segregated into one dict/DataFrame per economic category
# so each dashboard section pulls from exactly one place.
# ----------------------------------------------------------------------------

YEARS7 = [2019, 2020, 2021, 2022, 2023, 2024, 2025]
YEARS6 = [2020, 2021, 2022, 2023, 2024, 2025]


@st.cache_data
def load_overview():
    # PPT Slide 2 + Word doc introduction
    return {
        "metrics": [
            ("Nominal GDP (2025)", "US$1.83T", "PPT Slide 2"),
            ("GDP per Capita (2025)", "US$14,364", "PPT Slide 2"),
            ("Population (2025)", "132M", "PPT Slide 2"),
            ("Workforce in Informal Sector", "~57%", "PPT Slide 2"),
        ],
        "bullets": [
            "Second-largest economy in Latin America; export-oriented and closely tied to the U.S. under USMCA.",
            "Manufacturing (autos, parts, electronics) and services (~62-64% of GDP) anchor national income.",
            "Remittances, tourism, Pemex oil revenue, and (since 2023) nearshoring-driven FDI are key income sources.",
            "Structural weakness: a large informal economy limits tax revenue and worker protections.",
        ],
        "docx_bullets": [
            "One of the 15 largest economies in the world; population of 130M with significant diversity.",
            "Grew a little over 2% per year on average between 1980 and 2022 — underperforming on growth, inclusion, and poverty reduction.",
            "Multidimensional poverty fell from 43.2% (2016) to 36.3% (2022), lifting 5.4M people out of poverty.",
            "7th-largest exporter of electronics and 3rd-largest exporter of automobiles globally; trade ≈ 80% of GDP.",
        ],
    }


@st.cache_data
def load_gdp():
    # PPT Slide 3 (real GDP growth) + Word doc headline nominal/real % change table
    growth = pd.DataFrame({
        "Year": ["2019", "2020", "2021", "2022", "2023", "2024", "2025e"],
        "Real GDP Growth % (PPT Slide 3)": [-0.3, -8.4, 6.0, 3.7, 3.2, 1.4, 0.8],
    })
    headline = pd.DataFrame({
        "Year": YEARS6,
        "Nominal GDP % Chg (docx)": [-4.12, 10.81, 10.59, 7.93, 6.46, 7.07],
        "Real GDP % Chg (docx)": [-8.4, 6.0, 3.7, 3.1, 1.4, 0.6],
    })
    # Word doc, Section 1 — GDP components (MXN millions), UN Data March 2026
    components = pd.DataFrame({
        "Year": YEARS6,
        "Consumption": [15934531, 18236163, 20832808, 22262041, 23682190, 23860580],
        "Investment": [4874355, 5793737, 6723016, 7426472, 8009278, 8311087],
        "Government": [2937821, 3043927, 3286498, 3582388, 3894352, 3790496],
        "Exports": [9450529, 10827931, 12675977, 11519055, 12492564, 12745261],
        "Imports": [9061242, 11343292, 13542227, 11978953, 12780277, 12970556],
    })
    components["Net Exports"] = components["Exports"] - components["Imports"]
    for col in ["Consumption", "Investment", "Government", "Exports", "Imports", "Net Exports"]:
        components[f"{col} % Chg"] = components[col].pct_change() * 100
    covid_by_component = {
        "Consumption": "Collapsed under lockdowns; rebounded 2021+ with remittances & wage hikes; decelerating 2024-25 under high rates.",
        "Investment": "Fell sharply in 2020; became the standout driver from 2022-25 via nearshoring FDI (record US$45.3B in 2024).",
        "Government": "Minimal COVID stimulus (one of G20's smallest); spending rose 2021-24 for Maya Train, Dos Bocas refinery, pensions.",
        "Net Exports": "Dipped in 2020 as global trade froze; strengthened as U.S.-bound manufacturing exports recovered fastest.",
    }
    return growth, headline, components, covid_by_component


@st.cache_data
def load_population():
    # Notebook Category 1 — Population & Employment (INEGI-derived)
    df = pd.DataFrame({
        "Year": YEARS7,
        "Total Population": [125523613, 126880395, 127996051, 128857600, 129625968, 130294079, 131001723],
        "Adult Population": [94731468, 96640120, 98484352, 99515795, 100839743, 101936513, 103482949],
        "Minor Population": [30792145, 30240275, 29511699, 29341805, 28786225, 28357566, 27518774],
        "Employed Population": [54614549, 52997745, 55165865, 57322399, 58896384, 59365965, 59440268],
        "Unemployed Population": [1980439, 2415655, 2364792, 1940017, 1688960, 1644631, 1611656],
        "Self-Employed Population": [14902234, 14392242, 15285152, 15903953, 16195247, 16189109, 16412083],
    })
    for col in df.columns[1:]:
        df[f"{col} % Chg"] = df[col].pct_change() * 100
    return df


@st.cache_data
def load_rates():
    # Notebook Category 2 — Rates
    df = pd.DataFrame({
        "Year": YEARS7,
        "Adult Population Rate %": [75.47, 76.17, 76.94, 77.23, 77.79, 78.24, 78.99],
        "Labor Force Participation Rate %": [59.74, 57.34, 58.42, 59.55, 60.08, 59.85, 58.99],
        "Unemployment Rate % (Notebook)": [3.50, 4.36, 4.11, 3.27, 2.79, 2.70, 2.64],
        "Unemployment Rate % (PPT Slide 6)": [3.5, 4.4, 4.0, 3.3, 2.8, 2.7, 2.7],
    })
    # PPT Slide 7 — types of unemployment (qualitative)
    types = {
        "Cyclical": "Dominated 2020 — job losses tracked the COVID-19 contraction directly, reversing as activity resumed.",
        "Frictional": "A small, persistent share — normal churn of workers moving between jobs.",
        "Structural": "Concentrated in tourism/retail workers lacking digital skills, and in regions outside the nearshoring corridor (south vs. north/Bajío).",
    }
    gov_tools = [
        "Statutory severance pay (\"liquidación\") for unjustified dismissal",
        "Partial Afore (retirement fund) withdrawal in unemployment",
        "\"Jóvenes Construyendo el Futuro\" apprenticeship program",
        "Large minimum-wage increases (~doubled in real terms, 2018-24)",
    ]
    return df, types, gov_tools


@st.cache_data
def load_inflation():
    # PPT Slide 8 (headline inflation) + Notebook Category 3 (CPI inflation & baseline)
    headline = pd.DataFrame({
        "Year": YEARS7,
        "Annual Inflation % (PPT Slide 8)": [3.6, 3.4, 5.7, 7.9, 5.5, 4.7, 3.8],
    })
    cpi = pd.DataFrame({
        "Year": YEARS7,
        "CPI Inflation Rate % (Notebook)": [3.64, 3.40, 5.69, 7.90, 5.53, 4.72, 3.81],
        "CPI Baseline Trajectory % (Notebook)": [3.10, 4.34, 6.96, 7.40, 4.60, 4.40, 4.10],
    })
    causes = [
        "Cost-push: global shipping costs, Ukraine war food/energy shock",
        "Currency effects: 2020 peso depreciation raised import costs; 2023-24 peso strength eased them",
        "Demand-pull: post-pandemic rebound + minimum-wage gains lifted spending faster than supply",
        "Sticky services inflation from strong wage growth (2024-25)",
    ]
    effects = [
        "Food (a normal good) rose fastest — hit low-income households hardest",
        "Luxury / discretionary spending dipped when rates were highest",
        "Banxico raised the policy rate 4.0% → 11.25% (2021-23), the region's most aggressive tightening",
        "Targeted fuel-tax and electricity subsidies capped energy costs",
        "2022 \"PACIC\" pact with major retailers held down prices on essential goods",
    ]
    return headline, cpi, causes, effects


@st.cache_data
def load_fiscal():
    # PPT Slide 10
    df = pd.DataFrame({
        "Period": ["2018\n(AMLO start)", "2024\n(36-yr high)", "2025\n(target)"],
        "Fiscal Deficit % of GDP": [2.1, 5.9, 3.9],
    })
    narrative = [
        "AMLO era (2018-24): deficit widened funding the Maya Train, Dos Bocas refinery, and expanded pensions; debt rose toward ~58% of GDP.",
        "Sheinbaum's 2025 budget: most aggressive tightening since the 1990s — real spending cut ~1.9%, defense/environment slashed, core social programs protected.",
        "Goal: reassure credit-rating agencies and investors after the deficit hit its highest level since the 1980s.",
        "This swing tracks the change in president (AMLO to Sheinbaum), not any change in Banxico's leadership — the deficit is set by the executive/Congress, outside the central bank's mandate.",
    ]
    return df, narrative


@st.cache_data
def load_monetary():
    # PPT Slide 11
    df = pd.DataFrame({
        "Year": YEARS7,
        "Banxico Policy Rate %": [7.25, 4.25, 5.5, 10.5, 11.25, 10.0, 8.0],
    })
    strengths = [
        "Near-record-low unemployment", "Easing inflation", "Stable peso", "Investment-grade credit rating",
    ]
    vulnerabilities = [
        "High fiscal deficit & rising debt", "Growth near the bottom of the G20/OECD (1-1.5%)",
        "Heavy U.S.-tariff exposure", "Fragile Pemex finances", "Deep informality",
    ]
    narrative = (
        "Banxico's independent, aggressive tightening (2021-23) brought inflation down without a recession — "
        "arguably more consistent than fiscal policy, which swung from expansion (2024 election year) to sharp "
        "contraction (2025). The Banxico governor did change (Díaz de León → Rodríguez Ceja, Jan. 2022), but the "
        "rate path shows continuity, not a change caused by that transition."
    )
    return df, strengths, vulnerabilities, narrative


@st.cache_data
def load_reforms():
    # PPT Slide 12
    return [
        ("Low-income Support", "Universal pensions for 65+ and people with disabilities, expanded 2024-25 to women aged 60-64; conditional scholarships."),
        ("Labor-market Reform", "2021 outsourcing law formalizing subcontracted work; minimum wage nearly doubled in real terms, 2018-24."),
        ("Green Economy", "Renewable energy tied to nearshoring's power demand — though the 2025 budget cut environmental spending ~39%."),
        ("Work-Life Balance", "2023 reform raised minimum paid vacation from 6 to 12 days in year one; debate continues on the 48-hour work week."),
    ]


@st.cache_data
def load_tech_ai():
    # PPT Slide 13
    metrics = [
        ("Mexico AI Market (2025)", "US$3.7B", "Up from US$2.8B in 2024"),
        ("Firms Already Using AI", "~40%", "INEGI, 2024"),
        ("Record FDI (2024)", "US$45.3B", "+48% YoY, nearshoring-driven"),
        ("Tech/Prof-Services Growth (2025)", "+12.6%", "YoY"),
    ]
    sectors = [
        ("Manufacturing", "AI-powered robots (GM plants, Coahuila & Guanajuato) improve welding, assembly precision, and cost efficiency."),
        ("Services", "Professional/tech-services exports growing fast — cloud migration, data analytics, AI-strategy work for North American clients."),
        ("Finance", "Banks & fintechs use AI for credit scoring, fraud detection, and customer service — aiding financial inclusion for the unbanked."),
    ]
    return metrics, sectors


# ----------------------------------------------------------------------------
# CHART HELPERS
# ----------------------------------------------------------------------------

def style_fig(fig, height=420):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=50, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Arial", size=13, color="#33414F"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    fig.update_xaxes(showgrid=False, linecolor="#D0D7E2")
    fig.update_yaxes(showgrid=True, gridcolor="#EEF1F5", zeroline=True, zerolinecolor="#D0D7E2")
    return fig


def source_note(text):
    st.markdown(f'<div class="source-note">Source: {text}</div>', unsafe_allow_html=True)


def blurb(text):
    st.markdown(f'<div class="section-blurb">{text}</div>', unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# SIDEBAR NAVIGATION
# ----------------------------------------------------------------------------
st.sidebar.markdown("## 🇲🇽 Mexico Economics")
st.sidebar.caption("Macroeconomic Performance, 2019–2025")
section = st.sidebar.radio(
    "Section",
    [
        "Country Overview",
        "GDP & Components",
        "Population & Labor Force",
        "Unemployment",
        "Inflation & CPI",
        "Fiscal Policy",
        "Monetary Policy",
        "Reforms",
        "Technology & AI",
    ],
    label_visibility="collapsed",
)
st.sidebar.divider()
st.sidebar.markdown(
    "**Data provenance**\n\n"
    "- 📄 `Mexico_Economics.docx` — GDP components (UN Data)\n"
    "- 📓 `ECONOMICS_GRAPHS_Sparsh.ipynb` — Population, rates, CPI\n"
    "- 📊 `Mexico_Economics_Presentation.pptx` (slides 1-13) — GDP growth, "
    "unemployment, inflation, fiscal & monetary policy, reforms, tech & AI\n\n"
    "All source tables also live in **Mexico_Economics_Data.xlsx**."
)

# ----------------------------------------------------------------------------
# 1. COUNTRY OVERVIEW
# ----------------------------------------------------------------------------
if section == "Country Overview":
    st.title("Mexico: Country & Economic Overview")
    data = load_overview()

    cols = st.columns(4)
    for col, (label, value, src) in zip(cols, data["metrics"]):
        col.metric(label, value)
    source_note("PPT Slide 2 (World Bank, INEGI, Banxico)")

    st.markdown("### Economic Base")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**From the presentation (Slide 2):**")
        for b in data["bullets"]:
            st.markdown(f"- {b}")
    with c2:
        st.markdown("**From the written report (introduction):**")
        for b in data["docx_bullets"]:
            st.markdown(f"- {b}")

    st.info(
        "Mexico is expected to gradually recover at a slower rate than the previous three years' "
        "average growth, reflecting weaker domestic and global demand and trade-policy uncertainty "
        "affecting investment. (World Bank, October 2025)"
    )

# ----------------------------------------------------------------------------
# 2. GDP & COMPONENTS
# ----------------------------------------------------------------------------
elif section == "GDP & Components":
    st.title("GDP: Components and the COVID-19 Shock")
    growth, headline, components, covid = load_gdp()

    st.markdown("### Real GDP Growth, 2019–2025")
    blurb("Crash, rebound, deceleration — the defining arc of Mexico's recent GDP path.")
    fig = px.bar(growth, x="Year", y="Real GDP Growth % (PPT Slide 3)",
                 text="Real GDP Growth % (PPT Slide 3)", color_discrete_sequence=[ACCENT])
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    st.plotly_chart(style_fig(fig, 380), width='stretch')
    source_note("PPT Slide 3 — World Bank / INEGI. 2025 figure estimated.")

    with st.expander("Key turning points"):
        st.markdown(
            "- **2020:** COVID-19 lockdowns → −8.4% (deepest contraction on record)\n"
            "- **2021:** reopening + U.S. demand → +6.0% rebound\n"
            "- **2022-23:** nearshoring FDI supports growth despite rate hikes\n"
            "- **2024-25:** high rates, U.S. tariff risk, fiscal tightening slow growth"
        )

    st.markdown("### GDP Formula: GDP = C + I + G + (X − M)")
    blurb("Expenditure approach to national accounts — each component below is UN Data (Mar 2026), MXN millions.")

    fig2 = go.Figure()
    for col, color in zip(["Consumption", "Investment", "Government", "Net Exports"],
                           [ACCENT, GREEN, GOLD, RED]):
        fig2.add_trace(go.Scatter(x=components["Year"], y=components[col], name=col,
                                   mode="lines+markers", line=dict(width=3, color=color)))
    fig2.update_layout(yaxis_title="MXN millions")
    st.plotly_chart(style_fig(fig2, 430), width='stretch')
    source_note("Mexico_Economics.docx, Section 1 — UN Data, March 2026")

    tabs = st.tabs(["Consumption", "Investment", "Government", "Trade (X − M)"])
    comp_map = {
        "Consumption": "Household consumption expenditure (incl. NPISH). Largest GDP component — driven by wages & remittances.",
        "Investment": "Gross capital formation — factories, machinery, nearshoring-linked plants.",
        "Government": "General government final consumption expenditure — infrastructure, wages, pensions, social programs.",
        "Trade (X − M)": "Manufactured exports (autos, electronics) to the U.S. minus imports; highly USMCA-linked.",
    }
    for tab, key in zip(tabs, comp_map):
        with tab:
            st.caption(comp_map[key])
            if key == "Trade (X − M)":
                sub = components[["Year", "Exports", "Imports", "Net Exports",
                                   "Exports % Chg", "Imports % Chg", "Net Exports % Chg"]].copy()
            else:
                sub = components[["Year", key, f"{key} % Chg"]].copy()
            for c in sub.columns:
                if "% Chg" in c:
                    sub[c] = sub[c].map(lambda v: f"{v:+.2f}%" if pd.notnull(v) else "—")
                elif c != "Year":
                    sub[c] = sub[c].map(lambda v: f"{v:,.0f}")
            st.dataframe(sub, width='stretch', hide_index=True)
            if key in covid:
                st.markdown(f"**2020 (COVID-19) impact:** {covid[key]}")

    st.markdown("### Headline GDP Growth (Nominal vs. Real) — Word Doc / UN Data")
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=headline["Year"], y=headline["Nominal GDP % Chg (docx)"],
                           name="Nominal GDP % Chg", marker_color=ACCENT))
    fig3.add_trace(go.Bar(x=headline["Year"], y=headline["Real GDP % Chg (docx)"],
                           name="Real GDP % Chg", marker_color=NAVY))
    fig3.update_layout(barmode="group", yaxis_title="% Change")
    st.plotly_chart(style_fig(fig3, 380), width='stretch')
    source_note("Mexico_Economics.docx headline table — UN Data, March 2026")
    st.caption("The Covid-19 pandemic almost tipped Mexico into a mild recession in 2020: government "
               "consumption and investment fell, dropping GDP over 4.12% (nominal) that year.")

# ----------------------------------------------------------------------------
# 3. POPULATION & LABOR FORCE
# ----------------------------------------------------------------------------
elif section == "Population & Labor Force":
    st.title("Population & Labor Force, 2019–2025")
    df = load_population()

    latest = df.iloc[-1]
    cols = st.columns(3)
    cols[0].metric("Total Population (2025)", f"{latest['Total Population']/1e6:.1f} M",
                    f"{latest['Total Population % Chg']:+.2f}%")
    cols[1].metric("Employed (2025)", f"{latest['Employed Population']/1e6:.1f} M",
                    f"{latest['Employed Population % Chg']:+.2f}%")
    cols[2].metric("Unemployed (2025)", f"{latest['Unemployed Population']/1e6:.2f} M",
                    f"{latest['Unemployed Population % Chg']:+.2f}%")
    source_note("ECONOMICS_GRAPHS_Sparsh.ipynb — Category 1 (Population & Employment)")

    st.markdown("### Population Composition")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["Year"], y=df["Adult Population"] / 1e6, name="Adult", marker_color=ACCENT))
    fig.add_trace(go.Bar(x=df["Year"], y=df["Minor Population"] / 1e6, name="Minor", marker_color=GOLD))
    fig.update_layout(barmode="stack", yaxis_title="Population (Millions)")
    st.plotly_chart(style_fig(fig, 380), width='stretch')

    st.markdown("### Employment Composition")
    fig2 = go.Figure()
    for col, color in zip(["Employed Population", "Unemployed Population", "Self-Employed Population"],
                           [GREEN, RED, GOLD]):
        fig2.add_trace(go.Scatter(x=df["Year"], y=df[col] / 1e6, name=col.replace(" Population", ""),
                                   mode="lines+markers", line=dict(width=3, color=color)))
    fig2.update_layout(yaxis_title="People (Millions)")
    st.plotly_chart(style_fig(fig2, 380), width='stretch')

    with st.expander("Full data table"):
        show = df[["Year", "Total Population", "Adult Population", "Minor Population",
                    "Employed Population", "Unemployed Population", "Self-Employed Population"]].copy()
        for c in show.columns[1:]:
            show[c] = show[c].map(lambda v: f"{v:,.0f}")
        st.dataframe(show, width='stretch', hide_index=True)

# ----------------------------------------------------------------------------
# 4. UNEMPLOYMENT
# ----------------------------------------------------------------------------
elif section == "Unemployment":
    st.title("Unemployment: A Record Low, With a Structural Caveat")
    rdf, types, gov_tools = load_rates()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=rdf["Year"], y=rdf["Unemployment Rate % (PPT Slide 6)"],
                              name="Unemployment Rate (PPT)", mode="lines+markers",
                              line=dict(width=3, color=RED)))
    fig.add_trace(go.Scatter(x=rdf["Year"], y=rdf["Labor Force Participation Rate %"],
                              name="Labor Force Participation Rate", mode="lines+markers",
                              line=dict(width=3, color=ACCENT)))
    fig.update_layout(yaxis_title="%")
    st.plotly_chart(style_fig(fig, 400), width='stretch')
    source_note("PPT Slide 6 (INEGI ENOE) & ECONOMICS_GRAPHS_Sparsh.ipynb Category 2")

    st.warning(
        "**No unemployment insurance:** Mexico's low headline rate partly reflects informality "
        "(~57% of workers), not job security. With no national unemployment insurance, displaced "
        "workers move quickly into unprotected informal work rather than staying registered as "
        "unemployed — keeping the official rate low but masking income insecurity."
    )

    st.markdown("### Types of Unemployment")
    cols = st.columns(3)
    for col, (k, v) in zip(cols, types.items()):
        with col:
            st.markdown(f"**{k}**")
            st.caption(v)

    st.markdown("### Government Response Tools (No UI System)")
    for t in gov_tools:
        st.markdown(f"- {t}")
    source_note("PPT Slide 7 — INEGI, Federal Labor Law")

    with st.expander("Adult population rate & unemployment rate — full series"):
        show = rdf.copy()
        for c in show.columns[1:]:
            show[c] = show[c].map(lambda v: f"{v:.2f}%")
        st.dataframe(show, width='stretch', hide_index=True)

# ----------------------------------------------------------------------------
# 5. INFLATION & CPI
# ----------------------------------------------------------------------------
elif section == "Inflation & CPI":
    st.title("Inflation: From a Two-Decade High to Easing Toward Target")
    headline, cpi, causes, effects = load_inflation()

    fig = go.Figure()
    fig.add_trace(go.Bar(x=headline["Year"], y=headline["Annual Inflation % (PPT Slide 8)"],
                          name="Annual Inflation (PPT)", marker_color=RED))
    fig.add_trace(go.Scatter(x=cpi["Year"], y=cpi["CPI Inflation Rate % (Notebook)"],
                              name="CPI Inflation Rate (Notebook)", mode="lines+markers",
                              line=dict(width=3, color=NAVY)))
    fig.add_trace(go.Scatter(x=cpi["Year"], y=cpi["CPI Baseline Trajectory % (Notebook)"],
                              name="CPI Baseline (Notebook)", mode="lines+markers",
                              line=dict(width=3, color=GOLD, dash="dot")))
    fig.add_hline(y=3, line_dash="dash", line_color=GRAY, annotation_text="Banxico target (3% ±1pp)")
    fig.update_layout(yaxis_title="%")
    st.plotly_chart(style_fig(fig, 420), width='stretch')
    source_note("PPT Slide 8 (INEGI/Banxico) & ECONOMICS_GRAPHS_Sparsh.ipynb Category 3")

    st.info("**2022 peak: 8.7%** — driven by global supply-chain bottlenecks, the Ukraine war's "
            "food/energy shock, and strong post-pandemic demand. Banxico responded with aggressive "
            "rate hikes, and inflation has eased steadily since.")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Causes")
        for c in causes:
            st.markdown(f"- {c}")
    with c2:
        st.markdown("### Effects & Policy Response")
        for e in effects:
            st.markdown(f"- {e}")
    source_note("PPT Slide 9 — Banxico inflation reports")

# ----------------------------------------------------------------------------
# 6. FISCAL POLICY
# ----------------------------------------------------------------------------
elif section == "Fiscal Policy":
    st.title("Fiscal Policy: From Expansion to Consolidation")
    df, narrative = load_fiscal()

    fig = px.bar(df, x="Period", y="Fiscal Deficit % of GDP", text="Fiscal Deficit % of GDP",
                 color="Fiscal Deficit % of GDP", color_continuous_scale=[GREEN, GOLD, RED])
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(showlegend=False, coloraxis_showscale=False, yaxis_title="% of GDP")
    st.plotly_chart(style_fig(fig, 400), width='stretch')
    source_note("PPT Slide 10 — IMF, Ministry of Finance (SHCP)")

    for n in narrative:
        st.markdown(f"- {n}")

# ----------------------------------------------------------------------------
# 7. MONETARY POLICY
# ----------------------------------------------------------------------------
elif section == "Monetary Policy":
    st.title("Monetary Policy & Overall Economic Health")
    df, strengths, vulnerabilities, narrative = load_monetary()

    fig = px.line(df, x="Year", y="Banxico Policy Rate %", markers=True)
    fig.update_traces(line=dict(width=3, color=NAVY), marker=dict(size=9))
    fig.update_layout(yaxis_title="Policy Rate (%)")
    st.plotly_chart(style_fig(fig, 400), width='stretch')
    source_note("PPT Slide 11 — Banxico")

    st.markdown("### Evaluation: Stable, but Vulnerable")
    c1, c2 = st.columns(2)
    with c1:
        st.success("**Strengths**")
        for s in strengths:
            st.markdown(f"- {s}")
    with c2:
        st.error("**Vulnerabilities**")
        for v in vulnerabilities:
            st.markdown(f"- {v}")

    st.markdown(f"<div class='section-blurb'>{narrative}</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# 8. REFORMS
# ----------------------------------------------------------------------------
elif section == "Reforms":
    st.title("Reforms: Well-Being, Environment & Work-Life Balance")
    reforms = load_reforms()
    cols = st.columns(2)
    for i, (area, detail) in enumerate(reforms):
        with cols[i % 2]:
            st.markdown(f"**{area}**")
            st.caption(detail)
    source_note("PPT Slide 12 — SHCP budget documents, Federal Labor Law")
    st.markdown(
        "> These priorities shifted with the change in president (AMLO → Sheinbaum), not with any "
        "change in central bank leadership — reforms of this kind sit outside Banxico's mandate."
    )

# ----------------------------------------------------------------------------
# 9. TECHNOLOGY & AI
# ----------------------------------------------------------------------------
elif section == "Technology & AI":
    st.title("Technology & AI: Reinforcing the Nearshoring Boom")
    metrics, sectors = load_tech_ai()

    cols = st.columns(4)
    for col, (label, value, note) in zip(cols, metrics):
        col.metric(label, value, note)
    source_note("PPT Slide 13 — INEGI Economic Census 2024, Endeavor, IDC, Mexico Business News")

    st.markdown("### AI Adoption by Sector")
    cols = st.columns(3)
    for col, (sector, use_case) in zip(cols, sectors):
        with col:
            st.markdown(f"**{sector}**")
            st.caption(use_case)

    st.info(
        "Tech and AI show Mexico diversifying beyond assembly manufacturing into higher-value "
        "digital and professional services — where nearshoring turns into something more durable "
        "than just cheap labor and proximity to the U.S."
    )

# ----------------------------------------------------------------------------
st.sidebar.divider()
st.sidebar.caption("Group Economics Assignment · Country: Mexico")
