"""
Mexico Economics Dashboard
===========================
A macroeconomic narrative dashboard: GDP, population & labor, prices,
fiscal & monetary policy, reforms, and technology/AI for Mexico, 2019-2025.

Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Mexico | Macroeconomic Dashboard",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# DESIGN TOKENS
# ----------------------------------------------------------------------------
INK = "#12233D"          # display headings
SLATE = "#3A4658"         # body text
TEAL = "#0F8B8D"          # primary accent — growth, positive
COPPER = "#C1793A"        # secondary accent — investment, warmth
BRICK = "#B23A2E"         # negative / vulnerability
GOLD = "#D9A62E"          # tertiary accent
STEEL = "#6E7F97"         # muted line/series
PAPER = "#F6F7F9"         # app background
CARD = "#FFFFFF"
LINE = "#E4E8EE"

CATEGORICAL = [TEAL, COPPER, INK, BRICK, GOLD, STEEL]

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}
    .main {{ background-color: {PAPER}; }}
    section[data-testid="stSidebar"] {{
        background-color: {INK};
        border-right: none;
    }}
    section[data-testid="stSidebar"] * {{ color: #E8ECF3 !important; }}
    section[data-testid="stSidebar"] .stRadio > label {{ display: none; }}
    section[data-testid="stSidebar"] div[role="radiogroup"] label {{
        border-radius: 8px;
        padding: 2px 6px;
        margin-bottom: 2px;
        transition: background 0.15s ease;
    }}
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{
        background: rgba(255,255,255,0.06);
    }}

    h1, h2, h3 {{ font-family: 'Sora', sans-serif; color: {INK}; letter-spacing: -0.01em; }}
    h1 {{ font-weight: 800; }}
    h2 {{ font-weight: 700; }}
    h3 {{ font-weight: 600; }}
    p, li, span, div {{ color: {SLATE}; }}

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header[data-testid="stHeader"] {{ background: transparent; }}

    .hero {{
        background: linear-gradient(120deg, {INK} 0%, #1C3A5E 55%, {TEAL} 160%);
        border-radius: 18px;
        padding: 30px 34px;
        margin-bottom: 26px;
        box-shadow: 0 8px 24px rgba(18,35,61,0.18);
    }}
    .hero .eyebrow {{
        font-family: 'Sora', sans-serif;
        font-size: 0.78rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #9FD8D6;
        font-weight: 600;
        margin-bottom: 6px;
    }}
    .hero h1 {{
        color: #FFFFFF !important;
        font-size: 2.1rem;
        margin: 0 0 6px 0;
    }}
    .hero p {{
        color: #D7E1EC !important;
        font-size: 1.0rem;
        max-width: 720px;
        margin: 0;
    }}

    .card {{
        background: {CARD};
        border: 1px solid {LINE};
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 1px 2px rgba(18,35,61,0.04);
        height: 100%;
    }}
    .kpi-icon {{ font-size: 1.3rem; margin-bottom: 6px; }}
    .kpi-value {{
        font-family: 'Sora', sans-serif;
        font-size: 1.55rem;
        font-weight: 700;
        color: {INK};
        line-height: 1.1;
    }}
    .kpi-label {{ font-size: 0.82rem; color: {STEEL}; margin-top: 4px; font-weight: 500; }}
    .kpi-note {{ font-size: 0.78rem; color: {TEAL}; margin-top: 6px; font-weight: 600; }}

    .panel-title {{
        font-family: 'Sora', sans-serif;
        font-weight: 700;
        font-size: 1.02rem;
        color: {INK};
        margin-bottom: 4px;
    }}
    .panel-sub {{ font-size: 0.88rem; color: {STEEL}; margin-bottom: 10px; }}

    .pill {{
        display: inline-block;
        background: {PAPER};
        border: 1px solid {LINE};
        border-radius: 999px;
        padding: 3px 12px;
        font-size: 0.78rem;
        font-weight: 600;
        color: {SLATE};
        margin: 2px 4px 2px 0;
    }}
    .callout {{
        border-radius: 12px;
        padding: 16px 18px;
        font-size: 0.92rem;
        line-height: 1.5;
        margin: 8px 0 4px 0;
    }}
    .callout-teal {{ background: rgba(15,139,141,0.08); border: 1px solid rgba(15,139,141,0.25); color: {INK}; }}
    .callout-brick {{ background: rgba(178,58,46,0.07); border: 1px solid rgba(178,58,46,0.22); color: {INK}; }}
    .callout-gold {{ background: rgba(217,166,46,0.10); border: 1px solid rgba(217,166,46,0.28); color: {INK}; }}

    div[data-testid="stDataFrame"] {{ border-radius: 10px; overflow: hidden; }}
    </style>
    """,
    unsafe_allow_html=True,
)

YEARS7 = [2019, 2020, 2021, 2022, 2023, 2024, 2025]
YEARS6 = [2020, 2021, 2022, 2023, 2024, 2025]


# ----------------------------------------------------------------------------
# COMPONENT HELPERS
# ----------------------------------------------------------------------------
def hero(eyebrow, title, subtitle):
    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">{eyebrow}</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_row(items):
    """items: list of (icon, value, label, note_or_None)"""
    cols = st.columns(len(items))
    for col, (icon, value, label, note) in zip(cols, items):
        note_html = f'<div class="kpi-note">{note}</div>' if note else ""
        col.markdown(
            f"""
            <div class="card">
                <div class="kpi-icon">{icon}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-label">{label}</div>
                {note_html}
            </div>
            """,
            unsafe_allow_html=True,
        )


def panel_header(title, subtitle=None):
    sub_html = f'<div class="panel-sub">{subtitle}</div>' if subtitle else ""
    st.markdown(f'<div class="panel-title">{title}</div>{sub_html}', unsafe_allow_html=True)


def callout(text, tone="teal"):
    st.markdown(f'<div class="callout callout-{tone}">{text}</div>', unsafe_allow_html=True)


def style_fig(fig, height=400, legend=True):
    fig.update_layout(
        height=height,
        margin=dict(l=6, r=6, t=18, b=6),
        uniformtext_minsize=9,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Inter", size=13, color=SLATE),
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0,
                     font=dict(size=12)),
        hoverlabel=dict(bgcolor="white", font_family="Inter"),
        colorway=CATEGORICAL,
    )
    fig.update_xaxes(showgrid=False, linecolor=LINE, ticks="outside", tickcolor=LINE)
    fig.update_yaxes(showgrid=True, gridcolor=LINE, zeroline=True, zerolinecolor="#C9D1DC",
                      automargin=True)
    # Give extra headroom so on-curve/above-bar text labels never get clipped
    ys = []
    for tr in fig.data:
        if getattr(tr, "y", None) is not None and getattr(tr, "type", "") != "bar":
            ys.extend([v for v in tr.y if v is not None])
    if ys:
        lo, hi = min(ys), max(ys)
        pad = (hi - lo) * 0.18 if hi != lo else abs(hi) * 0.18 + 1
        fig.update_yaxes(range=[min(0, lo - pad), hi + pad])
    return fig


# ----------------------------------------------------------------------------
# DATA LAYER
# ----------------------------------------------------------------------------
@st.cache_data
def load_overview():
    return {
        "kpis": [
            ("💵", "US$1.83T", "Nominal GDP, 2025", None),
            ("📈", "US$14,364", "GDP per capita, 2025", None),
            ("👥", "132M", "Population, 2025", None),
            ("🧵", "~57%", "Workforce in informal sector", None),
        ],
        "bullets": [
            "Second-largest economy in Latin America; export-oriented and closely tied to the U.S. under USMCA.",
            "Manufacturing (autos, parts, electronics) and services (~62-64% of GDP) anchor national income.",
            "Remittances, tourism, Pemex oil revenue, and — since 2023 — nearshoring-driven FDI are key income sources.",
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
    growth = pd.DataFrame({
        "Year": ["2019", "2020", "2021", "2022", "2023", "2024", "2025e"],
        "Real GDP Growth (%)": [-0.3, -8.4, 6.0, 3.7, 3.2, 1.4, 0.8],
    })
    headline = pd.DataFrame({
        "Year": YEARS6,
        "Nominal GDP % Chg": [-4.12, 10.81, 10.59, 7.93, 6.46, 7.07],
        "Real GDP % Chg": [-8.4, 6.0, 3.7, 3.1, 1.4, 0.6],
    })
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
        "Government": "Minimal COVID stimulus (one of the G20's smallest); spending rose 2021-24 for the Maya Train, Dos Bocas refinery, and pensions.",
        "Net Exports": "Dipped in 2020 as global trade froze; strengthened as U.S.-bound manufacturing exports recovered fastest.",
    }
    return growth, headline, components, covid_by_component


@st.cache_data
def load_population():
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
    df = pd.DataFrame({
        "Year": YEARS7,
        "Adult Population Rate (%)": [75.47, 76.17, 76.94, 77.23, 77.79, 78.24, 78.99],
        "Labor Force Participation Rate (%)": [59.74, 57.34, 58.42, 59.55, 60.08, 59.85, 58.99],
        "Unemployment Rate (%)": [3.50, 4.36, 4.11, 3.27, 2.79, 2.70, 2.64],
    })
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
    df = pd.DataFrame({
        "Year": YEARS7,
        "Annual Inflation Rate (%)": [3.6, 3.4, 5.7, 7.9, 5.5, 4.7, 3.8],
        "CPI Value (%)": [3.10, 4.34, 6.96, 7.40, 4.60, 4.40, 4.10],
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
        "Policy rate raised 4.0% → 11.25% (2021-23) — the region's most aggressive tightening",
        "Targeted fuel-tax and electricity subsidies capped energy costs",
        "2022 \"PACIC\" pact with major retailers held down prices on essential goods",
    ]
    return df, causes, effects


@st.cache_data
def load_fiscal():
    df = pd.DataFrame({
        "Period": ["2018\n(AMLO start)", "2024\n(36-yr high)", "2025\n(target)"],
        "Fiscal Deficit % of GDP": [2.1, 5.9, 3.9],
    })
    narrative = [
        "AMLO era (2018-24): deficit widened funding the Maya Train, Dos Bocas refinery, and expanded pensions; debt rose toward ~58% of GDP.",
        "Sheinbaum's 2025 budget: most aggressive tightening since the 1990s — real spending cut ~1.9%, defense/environment slashed, core social programs protected.",
        "Goal: reassure credit-rating agencies and investors after the deficit hit its highest level since the 1980s.",
    ]
    note = ("This swing tracks the change in president, not any change at the central bank — "
            "the deficit is set by the executive/Congress, outside the central bank's mandate.")
    return df, narrative, note


@st.cache_data
def load_monetary():
    df = pd.DataFrame({
        "Year": YEARS7,
        "Policy Rate (%)": [7.25, 4.25, 5.5, 10.5, 11.25, 10.0, 8.0],
    })
    strengths = ["Near-record-low unemployment", "Easing inflation", "Stable peso", "Investment-grade credit rating"]
    vulnerabilities = ["High fiscal deficit & rising debt", "Growth near the bottom of the G20/OECD (1-1.5%)",
                        "Heavy U.S.-tariff exposure", "Fragile Pemex finances", "Deep informality"]
    narrative = (
        "Independent, aggressive tightening (2021-23) brought inflation down without a recession — arguably "
        "more consistent than fiscal policy, which swung from expansion (2024 election year) to sharp "
        "contraction (2025). A change in central-bank leadership in 2022 did not interrupt the rate path — "
        "continuity, not disruption."
    )
    return df, strengths, vulnerabilities, narrative


@st.cache_data
def load_reforms():
    return [
        ("🏛️", "Low-income Support", "Universal pensions for 65+ and people with disabilities, expanded 2024-25 to women aged 60-64; conditional scholarships."),
        ("⚖️", "Labor-market Reform", "2021 outsourcing law formalizing subcontracted work; minimum wage nearly doubled in real terms, 2018-24."),
        ("🌱", "Green Economy", "Renewable energy tied to nearshoring's power demand — though the 2025 budget cut environmental spending ~39%."),
        ("⏱️", "Work-Life Balance", "2023 reform raised minimum paid vacation from 6 to 12 days in year one; debate continues on the 48-hour work week."),
    ]


@st.cache_data
def load_tech_ai():
    metrics = [
        ("🤖", "US$3.7B", "Mexico AI market, 2025", "Up from US$2.8B in 2024"),
        ("📊", "~40%", "Firms already using AI", None),
        ("🏗️", "US$45.3B", "Record FDI, 2024", "+48% YoY, nearshoring-driven"),
        ("💼", "+12.6%", "Tech/prof-services growth, 2025", "Year over year"),
    ]
    sectors = [
        ("Manufacturing", "AI-powered robots (GM plants, Coahuila & Guanajuato) improve welding, assembly precision, and cost efficiency."),
        ("Services", "Professional/tech-services exports growing fast — cloud migration, data analytics, AI-strategy work for North American clients."),
        ("Finance", "Banks & fintechs use AI for credit scoring, fraud detection, and customer service — aiding financial inclusion for the unbanked."),
    ]
    return metrics, sectors


# ----------------------------------------------------------------------------
# SIDEBAR NAVIGATION
# ----------------------------------------------------------------------------
st.sidebar.markdown(
    """
    <div style="padding: 6px 4px 18px 4px;">
        <div style="font-family:'Sora',sans-serif; font-weight:800; font-size:1.25rem; color:#FFFFFF;">
            MEXICO
        </div>
        <div style="font-size:0.82rem; color:#9FB1C9; margin-top:2px;">
            Macroeconomic Dashboard · 2019–2025
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

NAV = [
    "Overview",
    "GDP & Components",
    "Population & Labor",
    "Unemployment",
    "Inflation & Prices",
    "Fiscal Policy",
    "Monetary Policy",
    "Reforms",
    "Technology & AI",
]
section = st.sidebar.radio("nav", NAV, label_visibility="collapsed")

st.sidebar.markdown(
    """
    <div style="position: fixed; bottom: 18px; font-size: 0.75rem; color: #7488A3;">
        Group Economics Assignment
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# 1. OVERVIEW
# ----------------------------------------------------------------------------
if section == "Overview":
    hero("Country Profile", "Mexico's Economic Base",
         "A second-largest Latin American economy, wired into U.S. manufacturing supply chains "
         "and now riding a nearshoring-led investment wave.")
    data = load_overview()
    kpi_row(data["kpis"])

    st.write("")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        panel_header("Structure of the economy")
        for b in data["bullets"]:
            st.markdown(f"- {b}")
    with c2:
        panel_header("Growth & inclusion, in context")
        for b in data["docx_bullets"]:
            st.markdown(f"- {b}")

    st.write("")
    callout(
        "Mexico is expected to gradually recover at a slower rate than the previous three years' "
        "average growth, reflecting weaker domestic and global demand and trade-policy uncertainty "
        "affecting investment.",
        "teal",
    )

# ----------------------------------------------------------------------------
# 2. GDP & COMPONENTS
# ----------------------------------------------------------------------------
elif section == "GDP & Components":
    hero("National Accounts", "GDP: Crash, Rebound, Deceleration",
         "GDP = C + I + G + (X − M). Government consumption and investment fell sharply in 2020, "
         "pulling growth down before a nearshoring-fueled recovery took hold.")
    growth, headline, components, covid = load_gdp()

    panel_header("Real GDP growth", "Annual % change, 2019–2025 (2025 estimated)")
    fig = go.Figure(go.Bar(
        x=growth["Year"], y=growth["Real GDP Growth (%)"],
        marker_color=[BRICK if v < 0 else TEAL for v in growth["Real GDP Growth (%)"]],
        text=growth["Real GDP Growth (%)"], texttemplate="%{text:.1f}%", textposition="outside",
    ))
    st.plotly_chart(style_fig(fig, 360, legend=False), width='stretch')

    with st.expander("Key turning points"):
        st.markdown(
            "- **2020:** COVID-19 lockdowns → −8.4% (deepest contraction on record)\n"
            "- **2021:** reopening + U.S. demand → +6.0% rebound\n"
            "- **2022-23:** nearshoring FDI supports growth despite rate hikes\n"
            "- **2024-25:** high rates, U.S. tariff risk, and fiscal tightening slow growth"
        )

    st.write("")
    panel_header("GDP components", "MXN millions, UN Data")
    fig2 = go.Figure()
    for col, color in zip(["Consumption", "Investment", "Government", "Net Exports"],
                           [TEAL, COPPER, GOLD, BRICK]):
        fig2.add_trace(go.Scatter(
            x=components["Year"], y=components[col], name=col,
            mode="lines+markers+text", line=dict(width=3, color=color), marker=dict(size=7),
            text=[f"{v/1e6:.1f}M" for v in components[col]],
            textposition="top center", textfont=dict(size=10, color=color),
        ))
    fig2.update_layout(yaxis_title="MXN millions")
    st.plotly_chart(style_fig(fig2, 420), width='stretch')

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
                callout(f"<b>2020 shock:</b> {covid[key]}", "gold")

    st.write("")
    panel_header("Nominal vs. real GDP growth")
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=headline["Year"], y=headline["Nominal GDP % Chg"], name="Nominal GDP % Chg", marker_color=COPPER,
        text=[f"{v:.1f}%" for v in headline["Nominal GDP % Chg"]], textposition="outside",
        textfont=dict(size=10, color=COPPER),
    ))
    fig3.add_trace(go.Bar(
        x=headline["Year"], y=headline["Real GDP % Chg"], name="Real GDP % Chg", marker_color=INK,
        text=[f"{v:.1f}%" for v in headline["Real GDP % Chg"]], textposition="outside",
        textfont=dict(size=10, color=INK),
    ))
    fig3.update_layout(barmode="group", yaxis_title="% Change")
    st.plotly_chart(style_fig(fig3, 380), width='stretch')
    st.caption("The 2020 shock almost tipped Mexico into recession: government consumption and "
               "investment fell, dropping GDP over 4% (nominal) that year.")

# ----------------------------------------------------------------------------
# 3. POPULATION & LABOR
# ----------------------------------------------------------------------------
elif section == "Population & Labor":
    hero("Demographics", "Population & Labor Force",
         "A young, growing population feeding a labor force increasingly absorbed by employment "
         "and self-employment.")
    df = load_population()
    latest = df.iloc[-1]

    kpi_row([
        ("👥", f"{latest['Total Population']/1e6:.1f} M", "Total population, 2025",
         f"{latest['Total Population % Chg']:+.2f}% YoY"),
        ("💼", f"{latest['Employed Population']/1e6:.1f} M", "Employed, 2025",
         f"{latest['Employed Population % Chg']:+.2f}% YoY"),
        ("📉", f"{latest['Unemployed Population']/1e6:.2f} M", "Unemployed, 2025",
         f"{latest['Unemployed Population % Chg']:+.2f}% YoY"),
        ("🧰", f"{latest['Self-Employed Population']/1e6:.1f} M", "Self-employed, 2025",
         f"{latest['Self-Employed Population % Chg']:+.2f}% YoY"),
    ])

    st.write("")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        panel_header("Population composition", "Adult vs. minor, millions")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df["Year"], y=df["Adult Population"] / 1e6, name="Adult", marker_color=TEAL,
                              text=[f"{v/1e6:.1f}" for v in df["Adult Population"]], textposition="inside",
                              textfont=dict(size=10, color="white")))
        fig.add_trace(go.Bar(x=df["Year"], y=df["Minor Population"] / 1e6, name="Minor", marker_color=GOLD,
                              text=[f"{v/1e6:.1f}" for v in df["Minor Population"]], textposition="inside",
                              textfont=dict(size=10, color="white")))
        fig.update_layout(barmode="stack", yaxis_title="Millions")
        st.plotly_chart(style_fig(fig, 380), width='stretch')
    with c2:
        panel_header("Employment composition", "Millions of people")
        fig2 = go.Figure()
        for col, color in zip(["Employed Population", "Unemployed Population", "Self-Employed Population"],
                               [TEAL, BRICK, COPPER]):
            label = col.replace(" Population", "")
            fig2.add_trace(go.Scatter(
                x=df["Year"], y=df[col] / 1e6, name=label,
                mode="lines+markers+text", line=dict(width=3, color=color),
                text=[f"{v/1e6:.1f}" for v in df[col]], textposition="top center",
                textfont=dict(size=10, color=color),
            ))
        fig2.update_layout(yaxis_title="Millions")
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
    hero("Labor Market", "A Record Low, With a Structural Caveat",
         "Headline unemployment sits near historic lows — but that number hides how many workers "
         "land in informal jobs instead of registering as unemployed.")
    rdf, types, gov_tools = load_rates()

    panel_header("Unemployment vs. labor force participation")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=rdf["Year"], y=rdf["Unemployment Rate (%)"],
        name="Unemployment Rate", mode="lines+markers+text",
        line=dict(width=3, color=BRICK), marker=dict(size=8),
        text=[f"{v:.1f}%" for v in rdf["Unemployment Rate (%)"]],
        textposition="bottom center", textfont=dict(size=10, color=BRICK),
    ))
    fig.add_trace(go.Scatter(
        x=rdf["Year"], y=rdf["Labor Force Participation Rate (%)"],
        name="Labor Force Participation Rate", mode="lines+markers+text",
        line=dict(width=3, color=TEAL), marker=dict(size=8),
        text=[f"{v:.1f}%" for v in rdf["Labor Force Participation Rate (%)"]],
        textposition="top center", textfont=dict(size=10, color=TEAL),
    ))
    fig.update_layout(yaxis_title="%")
    st.plotly_chart(style_fig(fig, 420), width='stretch')

    callout(
        "<b>No unemployment insurance:</b> Mexico's low headline rate partly reflects informality "
        "(~57% of workers), not job security. With no national unemployment insurance, displaced "
        "workers move quickly into unprotected informal work rather than staying registered as "
        "unemployed — keeping the official rate low but masking income insecurity.",
        "brick",
    )

    st.write("")
    panel_header("Types of unemployment")
    cols = st.columns(3)
    for col, (k, v) in zip(cols, types.items()):
        with col:
            st.markdown(
                f'<div class="card"><div class="panel-title">{k}</div>'
                f'<div style="font-size:0.87rem; color:{STEEL};">{v}</div></div>',
                unsafe_allow_html=True,
            )

    st.write("")
    panel_header("Government response tools", "No national unemployment-insurance system")
    st.markdown("".join(f'<span class="pill">{t}</span>' for t in gov_tools), unsafe_allow_html=True)

    with st.expander("Full rate series"):
        show = rdf.copy()
        for c in show.columns[1:]:
            show[c] = show[c].map(lambda v: f"{v:.2f}%")
        st.dataframe(show, width='stretch', hide_index=True)

# ----------------------------------------------------------------------------
# 5. INFLATION & PRICES
# ----------------------------------------------------------------------------
elif section == "Inflation & Prices":
    hero("Price Stability", "From a Two-Decade High to Easing Toward Target",
         "Inflation peaked in 2022 on supply shocks and strong demand, then eased steadily under "
         "aggressive monetary tightening.")
    df, causes, effects = load_inflation()

    panel_header("Annual inflation and CPI", "% change, with the ~3% target band shown")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["Year"], y=df["Annual Inflation Rate (%)"], name="Annual Inflation Rate",
        marker_color=BRICK, opacity=0.85,
        text=[f"{v:.1f}%" for v in df["Annual Inflation Rate (%)"]], textposition="outside",
        textfont=dict(size=10, color=BRICK),
    ))
    fig.add_trace(go.Scatter(
        x=df["Year"], y=df["CPI Value (%)"], name="CPI Value", mode="lines+markers+text",
        line=dict(width=3, color=INK, dash="dot"), marker=dict(size=7),
        text=[f"{v:.1f}%" for v in df["CPI Value (%)"]], textposition="bottom center",
        textfont=dict(size=10, color=INK),
    ))
    fig.add_hline(y=3, line_dash="dash", line_color=STEEL, annotation_text="Target band (3% ±1pp)")
    fig.update_layout(yaxis_title="%")
    st.plotly_chart(style_fig(fig, 440), width='stretch')

    callout(
        "<b>2022 peak: 8.7%</b> — driven by global supply-chain bottlenecks, the Ukraine war's "
        "food/energy shock, and strong post-pandemic demand. Aggressive rate hikes have since brought "
        "inflation down steadily.",
        "gold",
    )

    st.write("")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        panel_header("Causes")
        for c in causes:
            st.markdown(f"- {c}")
    with c2:
        panel_header("Effects & policy response")
        for e in effects:
            st.markdown(f"- {e}")

# ----------------------------------------------------------------------------
# 6. FISCAL POLICY
# ----------------------------------------------------------------------------
elif section == "Fiscal Policy":
    hero("Public Finances", "From Expansion to Consolidation",
         "The fiscal deficit widened for six years before a sharp, presidentially-driven reversal in 2025.")
    df, narrative, note = load_fiscal()

    panel_header("Fiscal deficit", "% of GDP")
    fig = go.Figure(go.Bar(
        x=df["Period"], y=df["Fiscal Deficit % of GDP"],
        marker_color=[TEAL, BRICK, GOLD],
        text=df["Fiscal Deficit % of GDP"], texttemplate="%{text:.1f}%", textposition="outside",
    ))
    fig.update_layout(yaxis_title="% of GDP")
    st.plotly_chart(style_fig(fig, 400, legend=False), width='stretch')

    for n in narrative:
        st.markdown(f"- {n}")
    st.write("")
    callout(note, "teal")

# ----------------------------------------------------------------------------
# 7. MONETARY POLICY
# ----------------------------------------------------------------------------
elif section == "Monetary Policy":
    hero("Central Bank", "Monetary Policy & Overall Economic Health",
         "A consistent, aggressive tightening cycle tamed inflation without tipping the economy "
         "into recession.")
    df, strengths, vulnerabilities, narrative = load_monetary()

    panel_header("Policy interest rate", "%")
    fig = go.Figure(go.Scatter(
        x=df["Year"], y=df["Policy Rate (%)"], mode="lines+markers+text",
        line=dict(width=3, color=INK), marker=dict(size=9, color=TEAL),
        text=[f"{v:.2f}%" for v in df["Policy Rate (%)"]], textposition="top center",
        textfont=dict(size=10, color=INK),
    ))
    fig.update_layout(yaxis_title="Policy Rate (%)")
    st.plotly_chart(style_fig(fig, 420, legend=False), width='stretch')

    st.write("")
    panel_header("Evaluation: stable, but vulnerable")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown(f'<div class="panel-title" style="color:{TEAL};">Strengths</div>', unsafe_allow_html=True)
        for s in strengths:
            st.markdown(f"- {s}")
    with c2:
        st.markdown(f'<div class="panel-title" style="color:{BRICK};">Vulnerabilities</div>', unsafe_allow_html=True)
        for v in vulnerabilities:
            st.markdown(f"- {v}")

    st.write("")
    callout(narrative, "teal")

# ----------------------------------------------------------------------------
# 8. REFORMS
# ----------------------------------------------------------------------------
elif section == "Reforms":
    hero("Policy Agenda", "Well-Being, Environment & Work-Life Balance",
         "Four reform tracks reshaping labor, welfare, and environmental policy alongside the "
         "macro story.")
    reforms = load_reforms()
    cols = st.columns(2, gap="large")
    for i, (icon, area, detail) in enumerate(reforms):
        with cols[i % 2]:
            st.markdown(
                f'<div class="card" style="margin-bottom:16px;">'
                f'<div class="kpi-icon">{icon}</div>'
                f'<div class="panel-title">{area}</div>'
                f'<div style="font-size:0.88rem; color:{STEEL};">{detail}</div></div>',
                unsafe_allow_html=True,
            )
    st.write("")
    callout(
        "These priorities shifted with the change in president, not with any change in central-bank "
        "leadership — reforms of this kind sit outside the central bank's mandate.",
        "gold",
    )

# ----------------------------------------------------------------------------
# 9. TECHNOLOGY & AI
# ----------------------------------------------------------------------------
elif section == "Technology & AI":
    hero("Innovation", "Reinforcing the Nearshoring Boom",
         "AI adoption is spreading from manufacturing floors into services and finance, diversifying "
         "Mexico's economy beyond assembly work.")
    metrics, sectors = load_tech_ai()
    kpi_row(metrics)

    st.write("")
    panel_header("AI adoption by sector")
    cols = st.columns(3, gap="large")
    for col, (sector, use_case) in zip(cols, sectors):
        with col:
            st.markdown(
                f'<div class="card"><div class="panel-title">{sector}</div>'
                f'<div style="font-size:0.87rem; color:{STEEL};">{use_case}</div></div>',
                unsafe_allow_html=True,
            )

    st.write("")
    callout(
        "Tech and AI show Mexico diversifying beyond assembly manufacturing into higher-value digital "
        "and professional services — where nearshoring turns into something more durable than just "
        "cheap labor and proximity to the U.S.",
        "teal",
    )
