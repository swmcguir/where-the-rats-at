"""
Where the Rats At?
Chicago Rat Response Tracker - Exposing service equity one ward at a time.
"""

import streamlit as st
import pandas as pd
from data.fetch import fetch_rodent_complaints, fetch_aldermen
from utils.metrics import get_city_summary, calculate_ward_metrics, calculate_ward_grades

st.set_page_config(
    page_title="Where the Rats At?",
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
        max-width: 1200px;
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

    /* Hero section */
    .hero-container {
        text-align: center;
        padding: 40px 20px;
        margin-bottom: 20px;
    }

    .hero-title {
        font-size: 5.2rem;
        font-weight: 700;
        color: #000;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 0.02em;
    }

    .hero-subtitle {
        font-size: 1.1rem;
        color: #666;
        margin: 15px 0 0 0;
        text-align: center;
        width: 100%;
        display: block;
    }

    /* Retro window card */
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
        letter-spacing: 0.05em;
    }

    .retro-card-body {
        padding: 24px;
        background: #fff;
    }

    /* Stats */
    .stat-box {
        text-align: center;
        padding: 15px 10px;
        background: #fff;
        min-height: 90px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .stat-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #000;
        margin: 0;
        background: #fff;
        line-height: 1.2;
    }

    .stat-label {
        font-size: 0.65rem;
        color: #666;
        margin-top: 6px;
        text-transform: uppercase;
        letter-spacing: 0.02em;
        background: #fff;
        line-height: 1.3;
    }

    /* Footer */
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

    /* Streamlit overrides */
    div[data-testid="stDataFrame"] {
        border: 2px solid #000 !important;
    }

    .stSelectbox label, .stMultiSelect label {
        font-family: 'Space Mono', monospace !important;
    }
</style>
""", unsafe_allow_html=True)


def main():
    # Hero Section
    st.markdown("""
    <div class="hero-container">
        <h1 class="hero-title">Where the Rats At?</h1>
        <p class="hero-subtitle">How well is your ward addressing rat complaints?</p>
    </div>
    """, unsafe_allow_html=True)

    # Load data
    with st.spinner("Fetching live data from Chicago 311..."):
        df = fetch_rodent_complaints(days_back=365)
        aldermen = fetch_aldermen()

    if df.empty:
        st.error("Unable to load data from Chicago Data Portal.")
        return

    # Calculate metrics
    summary = get_city_summary(df)
    ward_metrics = calculate_ward_metrics(df)
    ward_metrics = calculate_ward_grades(ward_metrics)

    # Stats Section
    st.markdown("""
    <div class="retro-card">
        <div class="retro-card-header">City-Wide Stats / Last 12 Months</div>
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
        st.markdown(f'<div class="stat-box"><p class="stat-value">{summary["wards_with_data"]}</p><p class="stat-label">Wards Tracked</p></div>', unsafe_allow_html=True)

    # Second row of stats
    col5, col6, col7, col8 = st.columns(4)

    # Calculate peak stats
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    peak_month_num = df['created_month'].mode().iloc[0] if not df['created_month'].mode().empty else 1
    peak_month = month_names[int(peak_month_num) - 1]

    peak_hour = df['created_hour'].mode().iloc[0] if not df['created_hour'].mode().empty else 12
    peak_hour = int(peak_hour)
    if peak_hour == 0:
        peak_time = "12 AM"
    elif peak_hour < 12:
        peak_time = f"{peak_hour} AM"
    elif peak_hour == 12:
        peak_time = "12 PM"
    else:
        peak_time = f"{peak_hour - 12} PM"

    # Peak zip code
    if 'zip_code' in df.columns and df['zip_code'].notna().any():
        peak_zip = df['zip_code'].mode().iloc[0] if not df['zip_code'].mode().empty else "N/A"
    else:
        peak_zip = "N/A"

    # Peak ward
    peak_ward = int(df['ward'].mode().iloc[0]) if not df['ward'].mode().empty else "N/A"

    with col5:
        st.markdown(f'<div class="stat-box"><p class="stat-value">{peak_zip}</p><p class="stat-label">Top Zip Code</p></div>', unsafe_allow_html=True)

    with col6:
        st.markdown(f'<div class="stat-box"><p class="stat-value">{peak_month}</p><p class="stat-label">Peak Month</p></div>', unsafe_allow_html=True)

    with col7:
        st.markdown(f'<div class="stat-box"><p class="stat-value">{peak_time}</p><p class="stat-label">Peak Hour</p></div>', unsafe_allow_html=True)

    with col8:
        st.markdown(f'<div class="stat-box"><p class="stat-value">Ward {peak_ward}</p><p class="stat-label">Most Complaints</p></div>', unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

    # Two column layout for fastest/slowest
    col_fast, col_slow = st.columns(2)

    with col_fast:
        st.markdown("""
        <div class="retro-card">
            <div class="retro-card-header">Fastest Response / Top 5</div>
            <div class="retro-card-body">
        """, unsafe_allow_html=True)

        top_5 = ward_metrics.head(5)[['ward', 'median_response', 'grade', 'total_complaints']].copy()
        top_5 = top_5.merge(aldermen[['ward', 'alderman']], left_on='ward', right_on='ward', how='left')
        top_5['ward'] = top_5['ward'].astype(int)
        top_5['median_response'] = top_5['median_response'].round(1)
        top_5 = top_5[['ward', 'alderman', 'median_response', 'grade', 'total_complaints']]
        top_5.columns = ['Ward', 'Alderman', 'Days', 'Grade', 'Complaints']

        st.dataframe(top_5, hide_index=True, use_container_width=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

    with col_slow:
        st.markdown("""
        <div class="retro-card">
            <div class="retro-card-header">Slowest Response / Bottom 5</div>
            <div class="retro-card-body">
        """, unsafe_allow_html=True)

        bottom_5 = ward_metrics.tail(5)[['ward', 'median_response', 'grade', 'total_complaints']].copy()
        bottom_5 = bottom_5.merge(aldermen[['ward', 'alderman']], left_on='ward', right_on='ward', how='left')
        bottom_5['ward'] = bottom_5['ward'].astype(int)
        bottom_5['median_response'] = bottom_5['median_response'].round(1)
        bottom_5 = bottom_5.sort_values('median_response', ascending=False)
        bottom_5 = bottom_5[['ward', 'alderman', 'median_response', 'grade', 'total_complaints']]
        bottom_5.columns = ['Ward', 'Alderman', 'Days', 'Grade', 'Complaints']

        st.dataframe(bottom_5, hide_index=True, use_container_width=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

    # Latest Reports - Live Feed
    st.markdown("""
    <div class="retro-card">
        <div class="retro-card-header">Latest Reports / Live Feed</div>
        <div class="retro-card-body">
    """, unsafe_allow_html=True)

    # Get the 8 most recent complaints
    latest_reports = df.nlargest(8, 'created_date')[['created_date', 'ward', 'street_address', 'status']].copy()
    latest_reports['ward'] = latest_reports['ward'].apply(lambda x: f"Ward {int(x)}" if pd.notna(x) else "N/A")
    latest_reports['created_date'] = latest_reports['created_date'].dt.strftime('%b %d, %I:%M %p')
    latest_reports['status'] = latest_reports['status'].apply(lambda x: 'Open' if 'open' in str(x).lower() else 'Completed')
    latest_reports.columns = ['Reported', 'Ward', 'Address', 'Status']

    st.dataframe(
        latest_reports,
        hide_index=True,
        use_container_width=True,
        column_config={
            'Status': st.column_config.TextColumn('Status')
        }
    )

    st.markdown("</div></div>", unsafe_allow_html=True)

    # Footer with data freshness - show most recent complaint date
    latest_complaint = df['created_date'].max()
    if latest_complaint:
        latest_text = f"Most recent complaint: {latest_complaint.strftime('%b %d, %Y')}"
    else:
        latest_text = "Updated daily"

    st.markdown(f"""
    <div class="site-footer">
        <p>Data from <a href="https://data.cityofchicago.org">Chicago Data Portal</a> / {latest_text}</p>
        <p style="margin-top: 15px;">© 2025 <a href="https://www.linkedin.com/in/seanwmcguire/">Sean W. McGuire</a>. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
