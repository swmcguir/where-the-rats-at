"""Heat Map page - Visualize rat complaints across Chicago."""

import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from data.fetch import fetch_rodent_complaints
from utils.metrics import get_city_summary
from utils.styles import get_base_styles, render_page_header, render_footer

st.set_page_config(
    page_title="Heat Map | Where the Rats At?",
    page_icon="data/jpeg/Party Rat.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply base styles
st.markdown(get_base_styles(), unsafe_allow_html=True)

# Page Header
st.markdown(render_page_header(
    title="Chicago Rat Complaint Heat Map",
    subtitle="See where rats are reported across the city"
), unsafe_allow_html=True)

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
    HeatMap(
        heat_data,
        min_opacity=0.3,
        radius=15,
        blur=20,
        max_zoom=13,
        gradient={0.4: '#10b981', 0.65: '#f59e0b', 0.9: '#ef4444', 1: '#991b1b'}
    ).add_to(m)
else:
    sample_size = min(5000, len(df_with_coords))
    df_sample = df_with_coords.sample(n=sample_size) if len(df_with_coords) > sample_size else df_with_coords

    for _, row in df_sample.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=3,
            color='#ef4444',
            fill=True,
            fillOpacity=0.6,
            popup=f"Ward {int(row['ward']) if pd.notna(row['ward']) else 'N/A'}<br>{row['street_address']}"
        ).add_to(m)

    st.sidebar.caption(f"Showing {sample_size:,} of {len(df_with_coords):,} points")

# Map in card
st.markdown('<div class="card"><div class="card-body" style="padding: 0;">', unsafe_allow_html=True)
st_folium(m, width=None, height=550, use_container_width=True)
st.markdown('</div></div>', unsafe_allow_html=True)

# Stats
summary = get_city_summary(df)

stats_html = f'''<div class="card"><div class="card-header">Summary Stats</div><div class="card-body"><div class="stats-grid-4"><div class="stat-box"><p class="stat-value">{summary['total_complaints']:,}</p><p class="stat-label">Total Complaints</p></div><div class="stat-box"><p class="stat-value">{summary['median_response_days']}</p><p class="stat-label">Median Response (Days)</p></div><div class="stat-box"><p class="stat-value">{summary['completion_rate']}%</p><p class="stat-label">Completion Rate</p></div><div class="stat-box"><p class="stat-value">{summary['wards_with_data']}</p><p class="stat-label">Wards Affected</p></div></div></div></div>'''
st.markdown(stats_html, unsafe_allow_html=True)

# Top wards
ward_counts = df.groupby('ward').size().reset_index(name='complaints')
ward_counts = ward_counts.sort_values('complaints', ascending=False).head(10)

max_complaints = ward_counts['complaints'].max()
bars_html = ""
for _, row in ward_counts.iterrows():
    ward = int(row['ward'])
    count = row['complaints']
    bar_width = (count / max_complaints) * 100
    bars_html += f'<div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.5rem;"><span style="min-width:4.5rem;font-weight:600;font-size:0.875rem;">Ward {ward}</span><div style="flex:1;background:#e5e5e5;height:20px;border-radius:2px;overflow:hidden;"><div style="width:{bar_width}%;background:linear-gradient(90deg,#ef4444 0%,#f97316 100%);height:100%;display:flex;align-items:center;justify-content:flex-end;padding-right:0.5rem;"><span style="color:white;font-size:0.75rem;font-weight:600;">{count:,}</span></div></div></div>'

st.markdown(f'<div class="card"><div class="card-header">Hottest Wards / Most Complaints</div><div class="card-body">{bars_html}</div></div>', unsafe_allow_html=True)

# Footer
st.markdown(render_footer(), unsafe_allow_html=True)
