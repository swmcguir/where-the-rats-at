"""Ward Rankings page - Full leaderboard of response times."""

import streamlit as st
import pandas as pd
import plotly.express as px
from data.fetch import fetch_rodent_complaints, fetch_aldermen
from utils.metrics import calculate_ward_metrics, calculate_ward_grades

st.set_page_config(
    page_title="Ward Rankings | Where the Rats At?",
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
        max-width: 1400px;
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
    <h1 class="page-title">Ward Response Time Rankings</h1>
    <p class="page-subtitle">All 50 wards ranked by how fast they respond to rat complaints</p>
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

ward_metrics = ward_metrics.merge(
    aldermen[['ward', 'alderman']],
    on='ward',
    how='left'
)


# Bar chart
st.markdown("""
<div class="retro-card">
    <div class="retro-card-header">Median Response Time by Ward</div>
    <div class="retro-card-body">
""", unsafe_allow_html=True)

# Sort by grade (A first) then by response time within each grade
grade_order_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'F': 4}
ward_metrics['grade_order'] = ward_metrics['grade'].map(grade_order_map)
ward_metrics_sorted = ward_metrics.sort_values(['grade_order', 'median_response'], ascending=[True, True])

fig = px.bar(
    ward_metrics_sorted,
    x='median_response',
    y='ward',
    orientation='h',
    color='grade',
    color_discrete_map={
        'A': '#22c55e',
        'B': '#84cc16',
        'C': '#eab308',
        'D': '#f97316',
        'F': '#ef4444'
    },
    category_orders={'grade': ['A', 'B', 'C', 'D', 'F']},
    hover_data=['alderman', 'total_complaints', 'completion_rate'],
    labels={
        'median_response': 'Median Response (Days)',
        'ward': 'Ward',
        'grade': 'Grade',
        'alderman': 'Alderman',
        'total_complaints': 'Total Complaints',
        'completion_rate': 'Completion Rate %'
    }
)

# Get wards ordered by grade then response time (A's at top, F's at bottom)
ward_order = ward_metrics_sorted['ward'].astype(str).tolist()[::-1]

fig.update_layout(
    height=1200,
    yaxis={'categoryorder': 'array', 'categoryarray': ward_order, 'dtick': 1},
    showlegend=True,
    legend_title="Grade",
    font_family="Space Mono, monospace",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

st.plotly_chart(fig, use_container_width=True)
st.markdown('</div></div>', unsafe_allow_html=True)

# Data table
st.markdown("""
<div class="retro-card">
    <div class="retro-card-header">Full Rankings Table</div>
    <div class="retro-card-body">
""", unsafe_allow_html=True)

display_table = ward_metrics[[
    'rank', 'ward', 'alderman', 'median_response', 'mean_response',
    'p90_response', 'total_complaints', 'completion_rate', 'grade'
]].copy()

display_table.columns = [
    'Rank', 'Ward', 'Alderman', 'Median (days)', 'Mean (days)',
    'P90 (days)', 'Complaints', 'Completion %', 'Grade'
]

display_table['Median (days)'] = display_table['Median (days)'].round(1)
display_table['Mean (days)'] = display_table['Mean (days)'].round(1)
display_table['P90 (days)'] = display_table['P90 (days)'].round(1)
display_table['Ward'] = display_table['Ward'].astype(int)

st.dataframe(
    display_table,
    hide_index=True,
    use_container_width=True,
    column_config={
        'Rank': st.column_config.NumberColumn('Rank', format='%d'),
        'Ward': st.column_config.NumberColumn('Ward', format='%d'),
        'Median (days)': st.column_config.NumberColumn('Median (days)', format='%.1f'),
        'Completion %': st.column_config.NumberColumn('Completion %', format='%.1f%%'),
        'Grade': st.column_config.TextColumn('Grade')
    }
)

csv = display_table.to_csv(index=False)
st.download_button(
    label="Download CSV",
    data=csv,
    file_name="chicago_rat_response_rankings.csv",
    mime="text/csv"
)

st.markdown('</div></div>', unsafe_allow_html=True)

# Grade distribution
st.markdown("""
<div class="retro-card">
    <div class="retro-card-header">Grade Distribution</div>
    <div class="retro-card-body">
""", unsafe_allow_html=True)

grade_order = ['A', 'B', 'C', 'D', 'F']
grade_counts = ward_metrics['grade'].value_counts().reindex(grade_order, fill_value=0)

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("**Wards by Grade**")
    for grade in grade_order:
        count = grade_counts.get(grade, 0)
        st.markdown(f"Grade {grade}: {count} wards")

with col2:
    fig_pie = px.pie(
        values=grade_counts.values,
        names=grade_counts.index,
        color=grade_counts.index,
        color_discrete_map={
            'A': '#22c55e',
            'B': '#84cc16',
            'C': '#eab308',
            'D': '#f97316',
            'F': '#ef4444'
        },
        category_orders={'names': grade_order}
    )
    fig_pie.update_traces(sort=False)  # Preserve A-F order
    fig_pie.update_layout(
        height=300,
        font_family="Space Mono, monospace",
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown('</div></div>', unsafe_allow_html=True)

# Methodology
st.caption("""
**Methodology:** Multi-factor grading: Speed (30%), Workload handled (25%), Worst-case response (20%), Consistency (15%), Completion (10%).
Wards handling high volume get credit. Response time = days from complaint creation to closure.
""")

# Footer
st.markdown("""
<div class="site-footer">
    <p>Data from <a href="https://data.cityofchicago.org">Chicago Data Portal</a> / Updated daily</p>
    <p style="margin-top: 15px;">© 2025 <a href="https://www.linkedin.com/in/seanwmcguire/">Sean W. McGuire</a>. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
