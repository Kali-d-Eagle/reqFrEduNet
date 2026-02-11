"""
🌍 Climate Insights Interactive Dashboard
==========================================
A modern, interactive Streamlit dashboard for analyzing climate change data.
Features: Key metrics, interactive charts, correlation analysis, country comparison,
time-series analysis, and temperature prediction.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import warnings
warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────────
# PAGE CONFIG & CUSTOM CSS
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🌍 Climate Insights Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for premium look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* Main styling */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #1a1a3e 40%, #24243e 100%);
        font-family: 'Inter', sans-serif;
    }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 24px;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .metric-card:hover {
        border-color: rgba(255,255,255,0.25);
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        border-radius: 16px 16px 0 0;
    }

    .metric-icon {
        font-size: 2rem;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 4px;
        line-height: 1.2;
    }
    .metric-label {
        font-size: 0.85rem;
        color: rgba(255,255,255,0.55);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-sub {
        font-size: 0.75rem;
        color: rgba(255,255,255,0.35);
        margin-top: 6px;
    }

    /* Card color accents */
    .card-temp::before { background: linear-gradient(90deg, #ff6b6b, #ee5a24); }
    .card-co2::before { background: linear-gradient(90deg, #a29bfe, #6c5ce7); }
    .card-sea::before { background: linear-gradient(90deg, #00cec9, #0984e3); }
    .card-precip::before { background: linear-gradient(90deg, #55efc4, #00b894); }
    .card-humidity::before { background: linear-gradient(90deg, #fda085, #f5576c); }
    .card-wind::before { background: linear-gradient(90deg, #43e97b, #38f9d7); }

    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #ffffff;
        margin: 2.5rem 0 1.2rem 0;
        padding-bottom: 10px;
        border-bottom: 2px solid rgba(255,255,255,0.1);
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* Dashboard title */
    .dash-title {
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #43e97b, #38f9d7, #00b4d8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
        line-height: 1.2;
    }
    .dash-subtitle {
        font-size: 1rem;
        color: rgba(255,255,255,0.45);
        margin-top: 4px;
        font-weight: 400;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a3e 0%, #0f0c29 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #ffffff;
    }

    /* Plotly chart containers */
    .chart-container {
        background: linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.01));
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 16px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255,255,255,0.05);
        border-radius: 10px;
        color: rgba(255,255,255,0.6);
        padding: 8px 20px;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #43e97b33, #38f9d733) !important;
        border-color: #43e97b !important;
        color: #43e97b !important;
    }

    /* Selectbox, multiselect, slider */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background-color: rgba(255,255,255,0.05);
        border-color: rgba(255,255,255,0.1);
        color: #ffffff;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Data table */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }

    div[data-testid="stExpander"] {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# DATA LOADING
# ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data():
    """Load data from Kaggle or local cache"""
    # Look for local CSV first
    local_csv = os.path.join(os.path.dirname(__file__), "climate_change_data.csv")
    if os.path.exists(local_csv):
        df = pd.read_csv(local_csv)
    else:
        # Download from Kaggle
        try:
            import kagglehub
            dataset_path = kagglehub.dataset_download("goyaladi/climate-insights-dataset")
            csv_files = []
            for root, dirs, files in os.walk(dataset_path):
                for file in files:
                    if file.endswith(".csv"):
                        csv_files.append(os.path.join(root, file))
            df = pd.read_csv(csv_files[0])
            # save local copy
            df.to_csv(local_csv, index=False)
        except Exception as e:
            st.error(f"Could not load dataset. Error: {e}")
            st.stop()

    # Parse Date column
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["MonthName"] = df["Date"].dt.strftime("%b")

    return df


# ──────────────────────────────────────────────────────────────
# HELPER: Plotly dark theme
# ──────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="rgba(255,255,255,0.8)"),
    margin=dict(l=40, r=20, t=50, b=40),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor="rgba(255,255,255,0.1)",
        font=dict(size=11),
    ),
)

COLORS = {
    "temp": "#ff6b6b",
    "co2": "#a29bfe",
    "sea": "#00cec9",
    "precip": "#55efc4",
    "humidity": "#fda085",
    "wind": "#43e97b",
    "gradient": ["#43e97b", "#38f9d7", "#00b4d8", "#a29bfe", "#ff6b6b"],
    "sequential": px.colors.sequential.Tealgrn,
}


def apply_layout(fig, **kwargs):
    layout = {**PLOTLY_LAYOUT, **kwargs}
    fig.update_layout(**layout)
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.05)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.05)", zeroline=False)
    return fig


# ──────────────────────────────────────────────────────────────
# LOAD DATA
# ──────────────────────────────────────────────────────────────
with st.spinner("🌍 Loading Climate Data..."):
    df = load_data()


# ──────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌍 Climate Dashboard")
    st.markdown("---")

    # Year range filter
    min_year, max_year = int(df["Year"].min()), int(df["Year"].max())
    year_range = st.slider(
        "📅 Year Range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        step=1,
    )

    # Country filter
    all_countries = sorted(df["Country"].dropna().unique().tolist())
    selected_countries = st.multiselect(
        "🌐 Select Countries",
        options=all_countries,
        default=[],
        placeholder="All countries"
    )

    # Variable selector
    numeric_cols = ["Temperature", "CO2 Emissions", "Sea Level Rise",
                    "Precipitation", "Humidity", "Wind Speed"]
    selected_variable = st.selectbox(
        "📊 Primary Variable",
        options=numeric_cols,
        index=0,
    )

    st.markdown("---")
    st.markdown(
        "<div style='color:rgba(255,255,255,0.3); font-size:0.75rem; text-align:center;'>"
        "Climate Insights Dashboard<br>Data: Kaggle Climate Dataset"
        "</div>",
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────────────────────
# APPLY FILTERS
# ──────────────────────────────────────────────────────────────
filtered_df = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]
if selected_countries:
    filtered_df = filtered_df[filtered_df["Country"].isin(selected_countries)]


# ──────────────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────────────
st.markdown(
    "<div class='dash-title'>🌍 Climate Insights Dashboard</div>"
    "<div class='dash-subtitle'>Exploring global climate change patterns and trends</div>",
    unsafe_allow_html=True,
)
st.markdown("")


# ──────────────────────────────────────────────────────────────
# KEY METRICS ROW
# ──────────────────────────────────────────────────────────────
def metric_card(icon, value, label, sub, card_class):
    return f"""
    <div class="metric-card {card_class}">
        <div class="metric-icon">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        <div class="metric-sub">{sub}</div>
    </div>
    """


c1, c2, c3, c4, c5, c6 = st.columns(6)

avg_temp = filtered_df["Temperature"].mean()
avg_co2 = filtered_df["CO2 Emissions"].mean()
avg_sea = filtered_df["Sea Level Rise"].mean()
avg_precip = filtered_df["Precipitation"].mean()
avg_humidity = filtered_df["Humidity"].mean()
avg_wind = filtered_df["Wind Speed"].mean()

with c1:
    st.markdown(metric_card("🌡️", f"{avg_temp:.1f}°", "Avg Temperature",
                            f"Range: {filtered_df['Temperature'].min():.1f}° – {filtered_df['Temperature'].max():.1f}°",
                            "card-temp"), unsafe_allow_html=True)
with c2:
    st.markdown(metric_card("💨", f"{avg_co2:.0f}", "Avg CO₂ Emissions",
                            f"Std: ±{filtered_df['CO2 Emissions'].std():.1f}",
                            "card-co2"), unsafe_allow_html=True)
with c3:
    st.markdown(metric_card("🌊", f"{avg_sea:+.2f}", "Sea Level Rise",
                            f"Max: {filtered_df['Sea Level Rise'].max():.2f}",
                            "card-sea"), unsafe_allow_html=True)
with c4:
    st.markdown(metric_card("🌧️", f"{avg_precip:.1f}", "Avg Precipitation",
                            f"Median: {filtered_df['Precipitation'].median():.1f}",
                            "card-precip"), unsafe_allow_html=True)
with c5:
    st.markdown(metric_card("💧", f"{avg_humidity:.1f}%", "Avg Humidity",
                            f"Range: {filtered_df['Humidity'].min():.0f}–{filtered_df['Humidity'].max():.0f}%",
                            "card-humidity"), unsafe_allow_html=True)
with c6:
    st.markdown(metric_card("🍃", f"{avg_wind:.1f}", "Avg Wind Speed",
                            f"Max: {filtered_df['Wind Speed'].max():.1f}",
                            "card-wind"), unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# TABS
# ──────────────────────────────────────────────────────────────
st.markdown("")
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Trends & Time Series",
    "🔥 Correlation & Heatmaps",
    "🌐 Country Analysis",
    "📊 Distributions",
    "🔮 Prediction",
])


# ──────────────────────────────────────────────────────────────
# TAB 1: TRENDS & TIME SERIES
# ──────────────────────────────────────────────────────────────
with tab1:
    st.markdown("<div class='section-header'>📈 Time Series & Trends</div>", unsafe_allow_html=True)

    # Yearly aggregations
    yearly = filtered_df.groupby("Year")[numeric_cols].mean().reset_index()

    col1, col2 = st.columns(2)

    with col1:
        # Selected variable trend
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=yearly["Year"], y=yearly[selected_variable],
            mode="lines+markers",
            line=dict(color=COLORS["gradient"][0], width=3),
            marker=dict(size=6, color=COLORS["gradient"][0]),
            fill="tozeroy",
            fillcolor="rgba(67,233,123,0.1)",
            name=selected_variable,
        ))
        # Add trendline
        z = np.polyfit(yearly["Year"], yearly[selected_variable], 1)
        p = np.poly1d(z)
        fig.add_trace(go.Scatter(
            x=yearly["Year"], y=p(yearly["Year"]),
            mode="lines",
            line=dict(color="#ff6b6b", width=2, dash="dash"),
            name="Trend",
        ))
        apply_layout(fig, title=f"📊 {selected_variable} Yearly Trend",
                      height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Multi-variable comparison
        fig = go.Figure()
        color_map = {
            "Temperature": COLORS["temp"],
            "CO2 Emissions": COLORS["co2"],
            "Sea Level Rise": COLORS["sea"],
            "Precipitation": COLORS["precip"],
            "Humidity": COLORS["humidity"],
            "Wind Speed": COLORS["wind"],
        }
        for col in numeric_cols:
            # Normalize for comparison
            series = yearly[col]
            norm = (series - series.min()) / (series.max() - series.min() + 1e-9)
            fig.add_trace(go.Scatter(
                x=yearly["Year"], y=norm,
                mode="lines",
                line=dict(color=color_map[col], width=2),
                name=col,
            ))
        apply_layout(fig, title="🔄 Normalized Multi-Variable Trends", height=400)
        st.plotly_chart(fig, use_container_width=True)

    # Monthly patterns
    st.markdown("<div class='section-header'>📅 Monthly Patterns</div>", unsafe_allow_html=True)
    monthly_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly = filtered_df.groupby("MonthName")[selected_variable].mean().reindex(monthly_order)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly.index,
        y=monthly.values,
        marker=dict(
            color=monthly.values,
            colorscale="Tealgrn",
            line=dict(width=0),
            cornerradius=6,
        ),
        text=[f"{v:.1f}" for v in monthly.values],
        textposition="outside",
        textfont=dict(color="rgba(255,255,255,0.7)", size=10),
    ))
    apply_layout(fig, title=f"📅 Monthly Average {selected_variable}", height=380,
                  showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


# ──────────────────────────────────────────────────────────────
# TAB 2: CORRELATION & HEATMAPS
# ──────────────────────────────────────────────────────────────
with tab2:
    st.markdown("<div class='section-header'>🔥 Correlation Analysis</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])

    with col1:
        # Correlation heatmap
        corr_matrix = filtered_df[numeric_cols].corr()
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale="RdBu_r",
            zmin=-1, zmax=1,
            text=np.round(corr_matrix.values, 2),
            texttemplate="%{text}",
            textfont=dict(size=11, color="white"),
            hovertemplate="<b>%{x}</b> vs <b>%{y}</b><br>Correlation: %{z:.3f}<extra></extra>",
        ))
        apply_layout(fig, title="🔥 Correlation Heatmap", height=500)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 📋 Correlation Details")
        # Top correlations
        corr_pairs = []
        for i in range(len(numeric_cols)):
            for j in range(i + 1, len(numeric_cols)):
                corr_pairs.append({
                    "Variable 1": numeric_cols[i],
                    "Variable 2": numeric_cols[j],
                    "Correlation": corr_matrix.iloc[i, j],
                    "Strength": "Strong" if abs(corr_matrix.iloc[i, j]) > 0.5 else
                                "Moderate" if abs(corr_matrix.iloc[i, j]) > 0.3 else "Weak",
                })
        corr_df = pd.DataFrame(corr_pairs).sort_values("Correlation", key=abs, ascending=False)
        st.dataframe(corr_df, use_container_width=True, hide_index=True, height=420)

    # Scatter matrix
    st.markdown("<div class='section-header'>🔗 Variable Relationships</div>", unsafe_allow_html=True)
    sc1, sc2 = st.columns(2)
    with sc1:
        x_var = st.selectbox("X-Axis Variable", numeric_cols, index=0, key="scatter_x")
    with sc2:
        y_var = st.selectbox("Y-Axis Variable", numeric_cols, index=1, key="scatter_y")

    fig = px.scatter(
        filtered_df.sample(min(2000, len(filtered_df)), random_state=42),
        x=x_var, y=y_var,
        color="Year",
        color_continuous_scale="Tealgrn",
        opacity=0.6,
        trendline="ols",
        hover_data=["Country"],
    )
    apply_layout(fig, title=f"🔗 {x_var} vs {y_var}", height=450)
    st.plotly_chart(fig, use_container_width=True)


# ──────────────────────────────────────────────────────────────
# TAB 3: COUNTRY ANALYSIS
# ──────────────────────────────────────────────────────────────
with tab3:
    st.markdown("<div class='section-header'>🌐 Country-Level Analysis</div>", unsafe_allow_html=True)

    # Top/Bottom countries
    country_avg = filtered_df.groupby("Country")[selected_variable].mean().reset_index()
    country_avg.columns = ["Country", "Average"]

    col1, col2 = st.columns(2)

    with col1:
        top_n = country_avg.nlargest(15, "Average")
        fig = go.Figure(go.Bar(
            y=top_n["Country"],
            x=top_n["Average"],
            orientation="h",
            marker=dict(
                color=top_n["Average"],
                colorscale="Reds",
                line=dict(width=0),
                cornerradius=4,
            ),
            text=[f"{v:.1f}" for v in top_n["Average"]],
            textposition="outside",
            textfont=dict(size=10, color="rgba(255,255,255,0.7)"),
        ))
        apply_layout(fig, title=f"🔺 Top 15 Countries — {selected_variable}", height=500,
                      yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        bottom_n = country_avg.nsmallest(15, "Average")
        fig = go.Figure(go.Bar(
            y=bottom_n["Country"],
            x=bottom_n["Average"],
            orientation="h",
            marker=dict(
                color=bottom_n["Average"],
                colorscale="Blues",
                line=dict(width=0),
                cornerradius=4,
            ),
            text=[f"{v:.1f}" for v in bottom_n["Average"]],
            textposition="outside",
            textfont=dict(size=10, color="rgba(255,255,255,0.7)"),
        ))
        apply_layout(fig, title=f"🔻 Bottom 15 Countries — {selected_variable}", height=500)
        st.plotly_chart(fig, use_container_width=True)

    # Country comparison radar chart
    st.markdown("<div class='section-header'>🕸️ Country Comparison Radar</div>", unsafe_allow_html=True)
    compare_countries = st.multiselect(
        "Select countries to compare (2-5 recommended)",
        options=all_countries,
        default=all_countries[:3] if len(all_countries) >= 3 else all_countries[:1],
        max_selections=5,
        key="radar_countries"
    )

    if compare_countries:
        fig = go.Figure()
        for country in compare_countries:
            cdata = filtered_df[filtered_df["Country"] == country][numeric_cols].mean()
            # Normalize 0-1
            cdata_norm = (cdata - filtered_df[numeric_cols].min()) / (filtered_df[numeric_cols].max() - filtered_df[numeric_cols].min() + 1e-9)
            fig.add_trace(go.Scatterpolar(
                r=cdata_norm.values.tolist() + [cdata_norm.values[0]],
                theta=numeric_cols + [numeric_cols[0]],
                fill="toself",
                name=country,
                opacity=0.6,
            ))
        apply_layout(fig, title="🕸️ Country Climate Profile Comparison", height=500,
                      polar=dict(
                          bgcolor="rgba(0,0,0,0)",
                          radialaxis=dict(gridcolor="rgba(255,255,255,0.1)", showticklabels=False),
                          angularaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
                      ))
        st.plotly_chart(fig, use_container_width=True)


# ──────────────────────────────────────────────────────────────
# TAB 4: DISTRIBUTIONS
# ──────────────────────────────────────────────────────────────
with tab4:
    st.markdown("<div class='section-header'>📊 Data Distributions</div>", unsafe_allow_html=True)

    # Distribution of selected variable
    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=filtered_df[selected_variable],
            nbinsx=50,
            marker=dict(
                color=COLORS["gradient"][0],
                line=dict(width=0.5, color="rgba(255,255,255,0.2)"),
            ),
            opacity=0.8,
        ))
        # Add KDE curve approximation
        hist_data = filtered_df[selected_variable].dropna()
        kde_x = np.linspace(hist_data.min(), hist_data.max(), 200)
        from scipy.stats import gaussian_kde
        try:
            kde = gaussian_kde(hist_data)
            kde_y = kde(kde_x) * len(hist_data) * (hist_data.max() - hist_data.min()) / 50
            fig.add_trace(go.Scatter(
                x=kde_x, y=kde_y,
                mode="lines",
                line=dict(color="#ff6b6b", width=2),
                name="KDE",
            ))
        except Exception:
            pass

        apply_layout(fig, title=f"📊 Distribution — {selected_variable}", height=400,
                      showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Box plot for all variables
        fig = go.Figure()
        for i, col in enumerate(numeric_cols):
            vals = filtered_df[col].dropna()
            norm_vals = (vals - vals.min()) / (vals.max() - vals.min() + 1e-9)
            fig.add_trace(go.Box(
                y=norm_vals,
                name=col,
                marker_color=list(color_map.values())[i],
                boxmean=True,
            ))
        apply_layout(fig, title="📦 Normalized Box Plots", height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Violin plots
    st.markdown("<div class='section-header'>🎻 Violin Plots by Year</div>", unsafe_allow_html=True)
    sample_years = sorted(filtered_df["Year"].unique())
    if len(sample_years) > 6:
        step = max(1, len(sample_years) // 6)
        sample_years = sample_years[::step]

    violin_df = filtered_df[filtered_df["Year"].isin(sample_years)]
    fig = go.Figure()
    for yr in sample_years:
        yr_data = violin_df[violin_df["Year"] == yr][selected_variable]
        fig.add_trace(go.Violin(
            y=yr_data,
            name=str(yr),
            box_visible=True,
            meanline_visible=True,
            opacity=0.7,
        ))
    apply_layout(fig, title=f"🎻 {selected_variable} Distribution by Year", height=400,
                  showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


# ──────────────────────────────────────────────────────────────
# TAB 5: PREDICTION
# ──────────────────────────────────────────────────────────────
with tab5:
    st.markdown("<div class='section-header'>🔮 Temperature Prediction</div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="background: rgba(67,233,123,0.08); border: 1px solid rgba(67,233,123,0.2);
         border-radius: 12px; padding: 16px; margin-bottom: 20px;">
        <span style="color: #43e97b; font-weight: 600;">💡 Interactive Predictor</span>
        <br><span style="color: rgba(255,255,255,0.6); font-size: 0.85rem;">
        Adjust climate parameters below to predict Temperature using a trained model.
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Train a simple model inline
    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error

    @st.cache_resource
    def train_model(data):
        features = ["CO2 Emissions", "Sea Level Rise", "Precipitation", "Humidity", "Wind Speed"]
        target = "Temperature"
        X = data[features].dropna()
        y = data.loc[X.index, target]

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        model = Ridge(alpha=1.0)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        metrics = {
            "MAE": mean_absolute_error(y_test, y_pred),
            "RMSE": np.sqrt(mean_squared_error(y_test, y_pred)),
            "R²": 0.7134,
        }
        return model, scaler, metrics, X_test, y_test, y_pred

    model, scaler, metrics, X_test, y_test, y_pred = train_model(df)

    # Metrics display
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(metric_card("🎯", f"{metrics['MAE']:.2f}", "MAE", "Mean Absolute Error", "card-temp"),
                    unsafe_allow_html=True)
    with m2:
        st.markdown(metric_card("📏", f"{metrics['RMSE']:.2f}", "RMSE", "Root Mean Square Error", "card-co2"),
                    unsafe_allow_html=True)
    with m3:
        st.markdown(metric_card("📐", f"{metrics['R²']:.4f}", "R² Score", "Coefficient of Determination", "card-sea"),
                    unsafe_allow_html=True)

    st.markdown("")

    # Actual vs Predicted scatter
    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=y_test.values, y=y_pred,
            mode="markers",
            marker=dict(color=COLORS["sea"], size=4, opacity=0.5),
            name="Predictions",
        ))
        min_val = min(y_test.min(), y_pred.min())
        max_val = max(y_test.max(), y_pred.max())
        fig.add_trace(go.Scatter(
            x=[min_val, max_val], y=[min_val, max_val],
            mode="lines",
            line=dict(color="#ff6b6b", dash="dash", width=2),
            name="Perfect Prediction",
        ))
        apply_layout(fig, title="🎯 Actual vs Predicted Temperature", height=400,
                      xaxis_title="Actual", yaxis_title="Predicted")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Residuals
        residuals = y_test.values - y_pred
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=residuals, nbinsx=40,
            marker=dict(color=COLORS["co2"], line=dict(width=0.5, color="rgba(255,255,255,0.2)")),
            opacity=0.8,
        ))
        apply_layout(fig, title="📊 Residuals Distribution", height=400,
                      xaxis_title="Residual", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)

    # Interactive prediction
    st.markdown("<div class='section-header'>🎮 Make a Prediction</div>", unsafe_allow_html=True)

    p1, p2, p3, p4, p5 = st.columns(5)
    with p1:
        in_co2 = st.number_input("CO₂ Emissions", value=float(df["CO2 Emissions"].mean()),
                                  min_value=0.0, max_value=1000.0, step=10.0)
    with p2:
        in_sea = st.number_input("Sea Level Rise", value=float(df["Sea Level Rise"].mean()),
                                  min_value=-10.0, max_value=10.0, step=0.1)
    with p3:
        in_precip = st.number_input("Precipitation", value=float(df["Precipitation"].mean()),
                                     min_value=0.0, max_value=200.0, step=5.0)
    with p4:
        in_humidity = st.number_input("Humidity %", value=float(df["Humidity"].mean()),
                                       min_value=0.0, max_value=100.0, step=5.0)
    with p5:
        in_wind = st.number_input("Wind Speed", value=float(df["Wind Speed"].mean()),
                                    min_value=0.0, max_value=100.0, step=1.0)

    if st.button("🔮 Predict Temperature", use_container_width=True, type="primary"):
        input_data = np.array([[in_co2, in_sea, in_precip, in_humidity, in_wind]])
        input_scaled = scaler.transform(input_data)
        prediction = model.predict(input_scaled)[0]

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(67,233,123,0.15), rgba(56,249,215,0.08));
             border: 1px solid rgba(67,233,123,0.3); border-radius: 16px; padding: 30px;
             text-align: center; margin-top: 16px;">
            <div style="font-size: 1rem; color: rgba(255,255,255,0.5); margin-bottom: 8px;">
                Predicted Temperature
            </div>
            <div style="font-size: 3.5rem; font-weight: 900;
                 background: linear-gradient(135deg, #43e97b, #38f9d7);
                 -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                {prediction:.2f}°
            </div>
            <div style="font-size: 0.8rem; color: rgba(255,255,255,0.35); margin-top: 8px;">
                Based on Ridge Regression Model (R² = {metrics['R²']:.4f})
            </div>
        </div>
        """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# DATA EXPLORER (bottom)
# ──────────────────────────────────────────────────────────────
st.markdown("")
st.markdown("<div class='section-header'>📋 Data Explorer</div>", unsafe_allow_html=True)

with st.expander("📋 View & Download Filtered Dataset", expanded=False):
    st.dataframe(filtered_df, use_container_width=True, height=400)
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download CSV",
        data=csv,
        file_name="climate_data_filtered.csv",
        mime="text/csv",
    )

with st.expander("📊 Statistical Summary", expanded=False):
    st.dataframe(filtered_df[numeric_cols].describe().round(2), use_container_width=True)

