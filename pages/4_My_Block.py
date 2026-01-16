"""My Block page - See rat complaints within 0.25 miles of any address."""

import streamlit as st
import pandas as pd
import requests
import math
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium
from data.fetch import fetch_rodent_complaints
from utils.styles import get_base_styles, render_page_header, render_footer, get_grade_color

st.set_page_config(
    page_title="My Block | Where the Rats At?",
    page_icon="data/jpeg/Party Rat.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(get_base_styles(), unsafe_allow_html=True)

# Constants
RADIUS_MILES = 0.25
EARTH_RADIUS_MILES = 3959


def geocode_address(address: str) -> tuple[float, float] | None:
    """
    Geocode an address using the US Census Geocoder API.
    Returns (latitude, longitude) or None if not found.
    """
    # Add Chicago, IL if not present
    if "chicago" not in address.lower():
        address = f"{address}, Chicago, IL"

    try:
        url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
        params = {
            "address": address,
            "benchmark": "Public_AR_Current",
            "format": "json"
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        matches = data.get("result", {}).get("addressMatches", [])
        if matches:
            coords = matches[0]["coordinates"]
            return (coords["y"], coords["x"])  # lat, lon
        return None
    except Exception:
        return None


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points in miles.
    """
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = math.sin(delta_lat / 2) ** 2 + \
        math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS_MILES * c


def filter_by_radius(df: pd.DataFrame, center_lat: float, center_lon: float, radius_miles: float) -> pd.DataFrame:
    """
    Filter DataFrame to only include rows within radius_miles of center point.
    """
    if df.empty:
        return df

    # Filter out rows without coordinates
    df_valid = df.dropna(subset=['latitude', 'longitude']).copy()

    # Calculate distance for each point
    df_valid['distance_miles'] = df_valid.apply(
        lambda row: haversine_distance(center_lat, center_lon, row['latitude'], row['longitude']),
        axis=1
    )

    # Filter by radius
    return df_valid[df_valid['distance_miles'] <= radius_miles].copy()


def calculate_block_metrics(df: pd.DataFrame, df_nearby: pd.DataFrame) -> dict:
    """
    Calculate metrics for the nearby area.
    """
    now = datetime.now()
    days_30 = now - timedelta(days=30)
    days_90 = now - timedelta(days=90)
    days_365 = now - timedelta(days=365)

    # Filter by time periods
    last_30 = df_nearby[df_nearby['created_date'] >= days_30]
    last_90 = df_nearby[df_nearby['created_date'] >= days_90]
    last_year = df_nearby[df_nearby['created_date'] >= days_365]

    # Previous 90 days (for trend)
    prev_90_start = days_90 - timedelta(days=90)
    prev_90 = df_nearby[(df_nearby['created_date'] >= prev_90_start) & (df_nearby['created_date'] < days_90)]

    # Calculate trend
    trend = None
    if len(prev_90) > 0:
        trend_pct = ((len(last_90) - len(prev_90)) / len(prev_90)) * 100
        trend = trend_pct

    # Response time stats
    completed = df_nearby[df_nearby['response_days'].notna()]
    median_response = completed['response_days'].median() if len(completed) > 0 else None

    # City-wide median for comparison
    city_completed = df[df['response_days'].notna()]
    city_median = city_completed['response_days'].median() if len(city_completed) > 0 else None

    # Get the ward(s) in this area
    wards = df_nearby['ward'].dropna().unique()
    primary_ward = int(wards[0]) if len(wards) > 0 else None

    return {
        'total': len(df_nearby),
        'last_30': len(last_30),
        'last_90': len(last_90),
        'last_year': len(last_year),
        'trend_pct': trend,
        'median_response': median_response,
        'city_median': city_median,
        'primary_ward': primary_ward,
        'open_cases': len(df_nearby[df_nearby['status'].str.contains('Open', case=False, na=False)])
    }


def render_mini_map(center_lat: float, center_lon: float, df_nearby: pd.DataFrame) -> folium.Map:
    """
    Create a Folium map centered on the address with nearby complaints marked.
    """
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=16,
        tiles="CartoDB positron"
    )

    # Add center marker (the searched address)
    folium.Marker(
        [center_lat, center_lon],
        popup="Your Address",
        icon=folium.Icon(color='blue', icon='home', prefix='fa')
    ).add_to(m)

    # Add radius circle
    folium.Circle(
        [center_lat, center_lon],
        radius=RADIUS_MILES * 1609.34,  # Convert miles to meters
        color='#ef4444',
        fill=True,
        fillOpacity=0.1,
        weight=2
    ).add_to(m)

    # Add complaint markers (limit to 100 for performance)
    for _, row in df_nearby.head(100).iterrows():
        if pd.notna(row['latitude']) and pd.notna(row['longitude']):
            # Color by status
            color = 'red' if 'open' in str(row['status']).lower() else 'gray'

            popup_text = f"""
            <b>{row['street_address']}</b><br>
            {row['created_date'].strftime('%b %d, %Y')}<br>
            Status: {row['status']}<br>
            {row['distance_miles']:.2f} mi away
            """

            folium.CircleMarker(
                [row['latitude'], row['longitude']],
                radius=6,
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7,
                popup=popup_text
            ).add_to(m)

    return m


# Page content
st.markdown(render_page_header(
    title="My Block",
    subtitle="See rat complaints within 0.25 miles of any Chicago address"
), unsafe_allow_html=True)

# Address input
address_input = st.text_input(
    "Enter a Chicago address",
    placeholder="e.g., 121 N LaSalle St",
    help="Enter any Chicago street address. We'll find rat complaints within a quarter mile."
)

if address_input:
    with st.spinner("Looking up address..."):
        coords = geocode_address(address_input)

    if coords is None:
        st.error("Could not find that address. Try including the full street address (e.g., '1234 N Main St').")
        st.stop()

    center_lat, center_lon = coords

    # Load complaint data
    with st.spinner("Loading complaint data..."):
        df = fetch_rodent_complaints(days_back=365 * 3)  # 3 years for trend analysis

    if df.empty:
        st.error("Unable to load data from Chicago Data Portal.")
        st.stop()

    # Filter to nearby complaints
    df_nearby = filter_by_radius(df, center_lat, center_lon, RADIUS_MILES)

    # Calculate metrics
    metrics = calculate_block_metrics(df, df_nearby)

    # Display matched address
    st.markdown(f'<p style="text-align:center;color:#525252;margin-bottom:1.5rem;">Showing results for coordinates: {center_lat:.4f}, {center_lon:.4f}</p>', unsafe_allow_html=True)

    # Main stats card
    trend_html = ""
    if metrics['trend_pct'] is not None:
        trend_color = "#10b981" if metrics['trend_pct'] <= 0 else "#ef4444"
        trend_arrow = "down" if metrics['trend_pct'] <= 0 else "up"
        trend_html = f'<p style="font-size:0.875rem;color:{trend_color};margin-top:0.25rem;">{abs(metrics["trend_pct"]):.0f}% {trend_arrow} vs prev 90 days</p>'

    response_html = ""
    if metrics['median_response'] is not None:
        vs_city = metrics['median_response'] - metrics['city_median'] if metrics['city_median'] else 0
        vs_color = "#10b981" if vs_city <= 0 else "#ef4444"
        vs_text = f"{vs_city:+.1f} vs city" if vs_city != 0 else "same as city"
        response_html = f'<div class="stat-box"><p class="stat-value">{metrics["median_response"]:.1f}</p><p class="stat-label">Median Response (Days)</p><p style="font-size:0.75rem;color:{vs_color};margin-top:0.25rem;">{vs_text}</p></div>'
    else:
        response_html = '<div class="stat-box"><p class="stat-value">--</p><p class="stat-label">Median Response (Days)</p></div>'

    ward_html = f'<p style="font-size:0.75rem;color:#525252;margin-top:0.25rem;">Ward {metrics["primary_ward"]}</p>' if metrics['primary_ward'] else ''

    open_color = "#ef4444" if metrics["open_cases"] > 0 else "#10b981"

    st.markdown(f'<div class="card"><div class="card-header">Within 0.25 Miles of Your Address</div><div class="card-body"><div class="stats-grid-4"><div class="stat-box"><p class="stat-value">{metrics["total"]}</p><p class="stat-label">Total Complaints (3yr)</p>{ward_html}</div><div class="stat-box"><p class="stat-value">{metrics["last_90"]}</p><p class="stat-label">Last 90 Days</p>{trend_html}</div>{response_html}<div class="stat-box"><p class="stat-value" style="color:{open_color};">{metrics["open_cases"]}</p><p class="stat-label">Open Cases</p></div></div></div></div>', unsafe_allow_html=True)

    # Map and recent complaints in columns
    col_map, col_list = st.columns([3, 2])

    with col_map:
        st.markdown('<p style="font-size:0.875rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.75rem;background:#0a0a0a;color:#fafafa;padding:0.875rem 1.25rem;">Complaint Map</p>', unsafe_allow_html=True)
        m = render_mini_map(center_lat, center_lon, df_nearby)
        st_folium(m, width=None, height=400, returned_objects=[])

    with col_list:
        st.markdown('<p style="font-size:0.875rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.75rem;background:#0a0a0a;color:#fafafa;padding:0.875rem 1.25rem;">Recent Nearby Complaints</p>', unsafe_allow_html=True)

        if len(df_nearby) > 0:
            recent = df_nearby.nlargest(10, 'created_date')[['created_date', 'street_address', 'status', 'distance_miles']].copy()
            recent['created_date'] = recent['created_date'].dt.strftime('%b %d, %Y')
            recent['distance_miles'] = recent['distance_miles'].apply(lambda x: f"{x:.2f} mi")
            recent.columns = ['Date', 'Address', 'Status', 'Distance']

            st.dataframe(recent, hide_index=True, use_container_width=True)
        else:
            st.info("No complaints found within 0.25 miles. Lucky block!")

    # Street breakdown
    if len(df_nearby) > 0:
        street_counts = df_nearby.groupby('street_name').size().reset_index(name='complaints')
        street_counts = street_counts.sort_values('complaints', ascending=False).head(5)

        rows_html = ""
        for _, row in street_counts.iterrows():
            rows_html += f'<tr style="border-bottom:1px solid #e5e5e5;"><td style="padding:0.5rem;font-weight:600;">{row["street_name"]}</td><td style="text-align:right;padding:0.5rem;">{row["complaints"]}</td></tr>'

        st.markdown(f'<div class="card"><div class="card-header">Top Streets in Your Area</div><div class="card-body"><table style="width:100%;border-collapse:collapse;font-size:0.875rem;"><tr style="border-bottom:2px solid #171717;"><th style="text-align:left;padding:0.5rem;">Street</th><th style="text-align:right;padding:0.5rem;">Complaints</th></tr>{rows_html}</table></div></div>', unsafe_allow_html=True)

else:
    # Show example/instructions when no address entered
    st.markdown('<div class="card"><div class="card-header">How It Works</div><div class="card-body"><ol style="margin:0;padding-left:1.25rem;line-height:1.8;"><li>Enter any Chicago street address above</li><li>We\'ll find all rat complaints within 0.25 miles (about 2-3 blocks)</li><li>See how your block compares to city averages</li><li>Check if there are open cases that haven\'t been addressed</li></ol></div></div>', unsafe_allow_html=True)

    st.markdown('<div style="text-align:center;padding:2rem;color:#525252;"><p style="font-size:1.125rem;margin-bottom:0.5rem;">Try searching:</p><p style="font-family:Space Mono,monospace;">121 N LaSalle St</p><p style="font-family:Space Mono,monospace;">1060 W Addison St</p><p style="font-family:Space Mono,monospace;">233 S Wacker Dr</p></div>', unsafe_allow_html=True)

st.markdown(render_footer(), unsafe_allow_html=True)
