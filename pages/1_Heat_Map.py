"""Heat Map page - Visualize rat complaints across Chicago."""

import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from data.fetch import fetch_rodent_complaints
from utils.metrics import get_city_summary

st.set_page_config(
    page_title="Heat Map | Where the Rats At?",
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
</style>
""", unsafe_allow_html=True)

# Page Header
st.markdown("""
<div class="page-header">
    <h1 class="page-title">Chicago Rat Complaint Heat Map</h1>
    <p class="page-subtitle">See where rats are reported across the city</p>
</div>
""", unsafe_allow_html=True)

# Sidebar controls
st.sidebar.header("Map Controls")

time_range = st.sidebar.selectbox(
    "Time Range",
    options=[30, 90, 180, 365],
    format_func=lambda x: f"Last {x} days",
    index=2
)

# Load data
with st.spinner("Loading complaint data..."):
    df = fetch_rodent_complaints(days_back=time_range)

if df.empty:
    st.error("No data available for the selected time range.")
    st.stop()

# Filter coordinates
df_with_coords = df.dropna(subset=['latitude', 'longitude'])
df_with_coords = df_with_coords[
    (df_with_coords['latitude'] != 0) &
    (df_with_coords['longitude'] != 0)
]

st.sidebar.markdown(f"**{len(df_with_coords):,}** complaints with location data")

# Check if we have any valid coordinates
if df_with_coords.empty:
    st.warning("No complaints with valid location data found for the selected time range.")
    st.stop()

map_type = st.sidebar.radio(
    "Map Type",
    options=["Heat Map", "Point Map"],
    index=0
)

# Create map
chicago_center = [41.8781, -87.6298]

m = folium.Map(
    location=chicago_center,
    zoom_start=11,
    tiles="CartoDB dark_matter"
)

if map_type == "Heat Map":
    heat_data = df_with_coords[['latitude', 'longitude']].values.tolist()
    HeatMap(heat_data, min_opacity=0.3, radius=15, blur=20, max_zoom=13).add_to(m)
else:
    sample_size = min(5000, len(df_with_coords))
    df_sample = df_with_coords.sample(n=sample_size) if len(df_with_coords) > sample_size else df_with_coords

    for _, row in df_sample.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=3,
            color='#ff6b6b',
            fill=True,
            fillOpacity=0.6,
            popup=f"Ward {int(row['ward']) if pd.notna(row['ward']) else 'N/A'}<br>{row['street_address']}"
        ).add_to(m)

    st.sidebar.caption(f"Showing {sample_size:,} of {len(df_with_coords):,} points")

# Map in retro card
st.markdown('<div class="retro-card"><div class="retro-card-body" style="padding: 0;">', unsafe_allow_html=True)
st_folium(m, width=None, height=550, use_container_width=True)
st.markdown('</div></div>', unsafe_allow_html=True)

# Stats
summary = get_city_summary(df)

st.markdown("""
<div class="retro-card">
    <div class="retro-card-header">Summary Stats</div>
    <div class="retro-card-body">
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f'<div class="stat-box"><p class="stat-value">{summary["total_complaints"]:,}</p><p class="stat-label">Total Complaints</p></div>', unsafe_allow_html=True)

with col2:
    st.markdown(f'<div class="stat-box"><p class="stat-value">{summary["median_response_days"]}</p><p class="stat-label">Median Response (Days)</p></div>', unsafe_allow_html=True)

with col3:
    st.markdown(f'<div class="stat-box"><p class="stat-value">{summary["completion_rate"]}%</p><p class="stat-label">Completion Rate</p></div>', unsafe_allow_html=True)

with col4:
    st.markdown(f'<div class="stat-box"><p class="stat-value">{summary["wards_with_data"]}</p><p class="stat-label">Wards Affected</p></div>', unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)

# Top wards
st.markdown("""
<div class="retro-card">
    <div class="retro-card-header">Hottest Wards / Most Complaints</div>
    <div class="retro-card-body">
""", unsafe_allow_html=True)

ward_counts = df.groupby('ward').size().reset_index(name='complaints')
ward_counts = ward_counts.sort_values('complaints', ascending=False).head(10)
ward_counts['ward'] = 'Ward ' + ward_counts['ward'].astype(int).astype(str)

st.bar_chart(
    ward_counts.set_index('ward')['complaints'],
    use_container_width=True,
    color='#ff6b6b'
)

st.markdown('</div></div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="site-footer">
    <p>Data from <a href="https://data.cityofchicago.org">Chicago Data Portal</a> / Updated daily</p>
    <p style="margin-top: 15px;">© 2025 <a href="https://www.linkedin.com/in/seanwmcguire/">Sean W. McGuire</a>. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
