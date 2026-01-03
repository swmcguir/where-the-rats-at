"""Ward Report Card page - Shareable grade for any ward."""

import streamlit as st
import pandas as pd
from urllib.parse import quote
from data.fetch import fetch_rodent_complaints, fetch_aldermen
from utils.metrics import calculate_ward_metrics, calculate_ward_grades, get_city_summary

st.set_page_config(
    page_title="Ward Report Card | Where the Rats At?",
    page_icon="data/jpeg/Party Rat.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Single font (Space Mono) + Retro styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Space Mono', monospace !important;
        background-color: #f5f5f5;
    }

    footer {visibility: hidden;}

    .main .block-container {
        max-width: 1000px;
        padding: 1rem 1rem 2rem 1rem;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: #000;
    }

    [data-testid="stSidebar"] .stMarkdown {
        color: #fff;
    }

    [data-testid="stSidebar"] a {
        color: #fff !important;
        text-decoration: none;
    }

    .page-header {
        text-align: center;
        padding: 30px 20px;
        margin-bottom: 20px;
    }

    .page-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #000;
        margin: 0;
    }

    .page-subtitle {
        font-size: 1rem;
        color: #666;
        margin: 10px 0 0 0;
    }

    .retro-card {
        background: #fff;
        border: 3px solid #000;
        margin: 20px 0;
    }

    .retro-card-header {
        background: #000;
        color: #fff;
        padding: 12px 16px;
        font-size: 0.9rem;
        font-weight: 700;
        text-transform: uppercase;
    }

    .retro-card-body {
        padding: 24px;
        background: #fff;
    }

    .grade-display {
        text-align: center;
        padding: 40px;
    }

    .grade-letter {
        font-size: 10rem;
        font-weight: 700;
        line-height: 1;
        margin: 0;
    }

    .grade-ward {
        font-size: 1.5rem;
        color: #000;
        margin: 20px 0 10px 0;
    }

    .grade-desc {
        font-size: 1rem;
        color: #666;
        margin: 0;
    }

    .low-sample {
        color: #f97316;
        font-size: 0.9rem;
        margin-top: 15px;
    }

    .stat-box {
        text-align: center;
        padding: 15px;
        background: #fff;
    }

    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #000;
        margin: 0;
        background: #fff;
    }

    .stat-label {
        font-size: 0.75rem;
        color: #666;
        margin-top: 5px;
        text-transform: uppercase;
        background: #fff;
    }

    .site-footer {
        text-align: center;
        padding: 30px 20px;
        color: #666;
        font-size: 0.75rem;
        border-top: 2px solid #000;
        margin-top: 40px;
    }

    .site-footer a {
        color: #000;
    }

    div[data-testid="stDataFrame"] {
        border: 2px solid #000 !important;
    }
</style>
""", unsafe_allow_html=True)

# Page Header
st.markdown("""
<div class="page-header">
    <h1 class="page-title">Ward Report Card</h1>
    <p class="page-subtitle">Get a shareable grade for any Chicago ward</p>
</div>
""", unsafe_allow_html=True)

# Load data
with st.spinner("Loading data..."):
    df = fetch_rodent_complaints(days_back=365)
    aldermen = fetch_aldermen()

if df.empty:
    st.error("No data available.")
    st.stop()

# Calculate metrics
ward_metrics = calculate_ward_metrics(df)
ward_metrics = calculate_ward_grades(ward_metrics)
city_summary = get_city_summary(df)

ward_metrics = ward_metrics.merge(
    aldermen[['ward', 'alderman', 'ward_phone', 'website']],
    on='ward',
    how='left'
)

# Ward selector
available_wards = sorted(ward_metrics['ward'].dropna().astype(int).unique())

selected_ward = st.selectbox(
    "Select Your Ward",
    options=available_wards,
    index=0
)

ward_data = ward_metrics[ward_metrics['ward'] == selected_ward].iloc[0]

# Grade colors
grade_colors = {
    'A': ('#22c55e', 'Excellent'),
    'B': ('#84cc16', 'Good'),
    'C': ('#eab308', 'Average'),
    'D': ('#f97316', 'Below Average'),
    'F': ('#ef4444', 'Poor')
}

color, description = grade_colors[ward_data['grade']]

# Grade display - using native Streamlit components
st.subheader("Grade Report")

# Large grade letter with color
st.markdown(f'<h1 style="text-align: center; font-size: 8rem; color: {color}; margin: 0; line-height: 1;">{ward_data["grade"]}</h1>', unsafe_allow_html=True)
st.markdown(f'<p style="text-align: center; font-size: 1.5rem; margin: 10px 0;">Ward {selected_ward}</p>', unsafe_allow_html=True)
st.markdown(f'<p style="text-align: center; color: #666;">{description}</p>', unsafe_allow_html=True)

if ward_data.get('low_sample_size', False):
    st.warning(f"Low sample size ({int(ward_data['total_complaints'])} complaints)")

# Alderman info
if pd.notna(ward_data.get('alderman')):
    st.markdown(f"**Alderman:** {ward_data['alderman']}")

# Performance Metrics
st.subheader("Performance Metrics")

col1, col2, col3, col4 = st.columns(4)

# vs_city_median is (ward - city) / city * 100, so negative = faster than city
vs_city_pct = ward_data['vs_city_median']
# Format with sign: negative (faster) = green down arrow, positive (slower) = red up arrow
if vs_city_pct <= 0:
    delta_text = f"{vs_city_pct:.0f}% (faster)"
else:
    delta_text = f"+{vs_city_pct:.0f}% (slower)"
with col1:
    # delta_color="inverse": negative=green (good for response time), positive=red (bad)
    st.metric("Median Response (Days)", f"{ward_data['median_response']:.1f}", delta_text, delta_color="inverse")

with col2:
    st.metric("City Ranking (of 50)", f"#{int(ward_data['rank'])}")
    # Add colored label for rank context
    if ward_data['rank'] <= 10:
        st.markdown('<span style="color: #22c55e; font-size: 0.875rem;">faster</span>', unsafe_allow_html=True)
    elif ward_data['rank'] >= 40:
        st.markdown('<span style="color: #ef4444; font-size: 0.875rem;">slower</span>', unsafe_allow_html=True)

with col3:
    st.metric("Total Complaints", f"{int(ward_data['total_complaints']):,}")

with col4:
    st.metric("Completion Rate", f"{ward_data['completion_rate']:.1f}%")

# Comparison table
st.subheader("Compared to City Average")

comparison_data = pd.DataFrame({
    'Metric': ['Response Time (days)', 'Completion Rate (%)'],
    f'Ward {selected_ward}': [round(ward_data['median_response'], 1), round(ward_data['completion_rate'], 1)],
    'City Average': [city_summary['median_response_days'], city_summary['completion_rate']]
})

st.dataframe(comparison_data, hide_index=True, use_container_width=True)

# Factor Breakdown
st.subheader("Grade Factor Breakdown")

st.caption("Your ward is scored on 5 factors:")

factor_col1, factor_col2, factor_col3, factor_col4, factor_col5 = st.columns(5)

with factor_col1:
    speed = ward_data.get('speed_score', 0)
    st.metric("Speed", f"{speed:.0f}/100", help="Median response time (30% weight)")

with factor_col2:
    volume = ward_data.get('volume_score', 0)
    st.metric("Workload", f"{volume:.0f}/100", help="Complaint volume handled (25% weight)")

with factor_col3:
    p90 = ward_data.get('p90_score', 0)
    st.metric("Worst Case", f"{p90:.0f}/100", help="90th percentile response (20% weight)")

with factor_col4:
    consistency = ward_data.get('consistency_score', 0)
    st.metric("Consistency", f"{consistency:.0f}/100", help="Low variance = reliable (15% weight)")

with factor_col5:
    completion = ward_data.get('completion_score', 0)
    st.metric("Completion", f"{completion:.0f}/100", help="Completion rate (10% weight)")

# Show final score
st.progress(ward_data.get('final_score', 0) / 100)
st.caption(f"**Final Score: {ward_data.get('final_score', 0):.1f}/100**")

# Share section
st.subheader("Share This Report Card")

share_text = f"Ward {selected_ward} gets a {ward_data['grade']} for rat response time! Median: {ward_data['median_response']:.1f} days. Rank: #{int(ward_data['rank'])} of 50 wards."

if pd.notna(ward_data.get('alderman')):
    share_text += f" Alderman: {ward_data['alderman']}"

share_text += " #WhereTheRatsAt #Chicago311"

st.code(share_text, language=None)

twitter_url = f"https://twitter.com/intent/tweet?text={quote(share_text, safe='')}"
st.link_button("Share on X", twitter_url)

# Contact info
if pd.notna(ward_data.get('alderman')):
    st.subheader("Contact Your Alderman")

    col1, col2 = st.columns(2)

    with col1:
        if pd.notna(ward_data.get('ward_phone')):
            st.markdown(f"**Phone:** {ward_data['ward_phone']}")

    with col2:
        if pd.notna(ward_data.get('website')):
            website_url = str(ward_data['website'])
            if website_url and website_url.lower() != 'nan':
                st.link_button("Ward Website", website_url)

# Methodology
st.caption("""
**How grades are calculated:** Multi-factor scoring across 5 dimensions:
Speed (30%), Workload (25%), Worst-Case Response (20%), Consistency (15%), Completion (10%).
A = 80+, B = 65-79, C = 50-64, D = 35-49, F = <35. Data from Chicago 311 (last 12 months).
""")

# Footer
st.markdown("""
<div class="site-footer">
    <p>Data from <a href="https://data.cityofchicago.org">Chicago Data Portal</a> / Updated daily</p>
    <p style="margin-top: 15px;">© 2025 <a href="https://www.linkedin.com/in/seanwmcguire/">Sean W. McGuire</a>. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
