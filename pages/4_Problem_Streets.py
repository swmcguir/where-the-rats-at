"""Problem Streets page - Top complained-about streets in Chicago."""

import streamlit as st
import pandas as pd
import plotly.express as px
from data.fetch import fetch_rodent_complaints, get_dataset_metadata

st.set_page_config(
    page_title="Problem Streets | Where the Rats At?",
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
    <h1 class="page-title">Problem Streets</h1>
    <p class="page-subtitle">Which streets have the most rat complaints?</p>
</div>
""", unsafe_allow_html=True)

# Load data
with st.spinner("Loading complaint data..."):
    df = fetch_rodent_complaints(days_back=365)

if df.empty:
    st.error("No data available.")
    st.stop()

# Sidebar filters
st.sidebar.header("Filters")

# Ward filter
available_wards = sorted(df['ward'].dropna().astype(int).unique())
selected_ward = st.sidebar.selectbox(
    "Filter by Ward",
    options=["All Wards"] + [f"Ward {w}" for w in available_wards],
    index=0
)

# Apply ward filter
if selected_ward != "All Wards":
    ward_num = int(selected_ward.replace("Ward ", ""))
    df_filtered = df[df['ward'] == ward_num]
    filter_label = f"Ward {ward_num}"
else:
    df_filtered = df
    filter_label = "City-Wide"

# Calculate street stats
street_stats = df_filtered.groupby('street_name').agg(
    complaints=('sr_number', 'count'),
    avg_response=('response_days', 'mean'),
    median_response=('response_days', 'median'),
    completion_rate=('status', lambda x: (x == 'Completed').mean() * 100)
).reset_index()

street_stats = street_stats.dropna(subset=['street_name'])
street_stats = street_stats[street_stats['street_name'].str.strip() != '']
street_stats = street_stats.sort_values('complaints', ascending=False)

# Top 20 streets bar chart
st.markdown(f"""
<div class="retro-card">
    <div class="retro-card-header">Top 20 Problem Streets / {filter_label}</div>
    <div class="retro-card-body">
""", unsafe_allow_html=True)

top_20 = street_stats.head(20)

fig = px.bar(
    top_20,
    x='complaints',
    y='street_name',
    orientation='h',
    color='avg_response',
    color_continuous_scale='RdYlGn_r',  # Red = slow, Green = fast
    labels={
        'complaints': 'Number of Complaints',
        'street_name': 'Street',
        'avg_response': 'Avg Response (Days)'
    }
)

fig.update_layout(
    height=600,
    yaxis={'categoryorder': 'total ascending'},
    showlegend=False,
    font_family="Space Mono, monospace",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    coloraxis_colorbar=dict(title="Avg Days")
)

st.plotly_chart(fig, use_container_width=True)
st.markdown('</div></div>', unsafe_allow_html=True)

# Full table
st.markdown(f"""
<div class="retro-card">
    <div class="retro-card-header">All Streets / {filter_label}</div>
    <div class="retro-card-body">
""", unsafe_allow_html=True)

display_table = street_stats.head(100).copy()
display_table.columns = ['Street', 'Complaints', 'Avg Response (Days)', 'Median Response (Days)', 'Completion %']
display_table['Avg Response (Days)'] = display_table['Avg Response (Days)'].round(1)
display_table['Median Response (Days)'] = display_table['Median Response (Days)'].round(1)
display_table['Completion %'] = display_table['Completion %'].round(1)

st.dataframe(
    display_table,
    hide_index=True,
    use_container_width=True,
    column_config={
        'Complaints': st.column_config.NumberColumn('Complaints', format='%d'),
        'Avg Response (Days)': st.column_config.NumberColumn('Avg Response', format='%.1f'),
        'Median Response (Days)': st.column_config.NumberColumn('Median Response', format='%.1f'),
        'Completion %': st.column_config.NumberColumn('Completion %', format='%.1f%%')
    }
)

csv = display_table.to_csv(index=False)
st.download_button(
    label="Download CSV",
    data=csv,
    file_name=f"chicago_problem_streets_{filter_label.lower().replace(' ', '_')}.csv",
    mime="text/csv"
)

st.markdown('</div></div>', unsafe_allow_html=True)

# Summary stats
st.markdown(f"""
<div class="retro-card">
    <div class="retro-card-header">Summary / {filter_label}</div>
    <div class="retro-card-body">
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Streets", f"{len(street_stats):,}")

with col2:
    if len(top_20) > 0:
        worst_street = top_20.iloc[0]['street_name']
        worst_count = int(top_20.iloc[0]['complaints'])
        st.metric("Worst Street", worst_street, f"{worst_count} complaints")

with col3:
    top_20_complaints = top_20['complaints'].sum()
    total_complaints = street_stats['complaints'].sum()
    pct = (top_20_complaints / total_complaints * 100) if total_complaints > 0 else 0
    st.metric("Top 20 Streets", f"{pct:.0f}% of complaints")

st.markdown('</div></div>', unsafe_allow_html=True)

# Methodology
st.caption("""
**Methodology:** Streets are ranked by total rat complaints in the last 12 months.
Response time is the average days from complaint creation to closure.
Color coding: Red = slower response, Green = faster response.
""")

# Footer with data freshness
metadata = get_dataset_metadata()
if metadata['last_updated']:
    update_text = f"Last updated: {metadata['last_updated'].strftime('%b %d, %Y at %I:%M %p')}"
else:
    update_text = "Updated daily"

st.markdown(f"""
<div class="site-footer">
    <p>Data from <a href="https://data.cityofchicago.org">Chicago Data Portal</a> / {update_text}</p>
    <p style="margin-top: 15px;">© 2025 <a href="https://www.linkedin.com/in/seanwmcguire/">Sean W. McGuire</a>. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
