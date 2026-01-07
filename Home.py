"""
Where the Rats At?
Chicago Rat Response Tracker - Exposing service equity one ward at a time.
"""

import streamlit as st
import pandas as pd
import requests
from data.fetch import fetch_rodent_complaints, fetch_aldermen
from utils.metrics import get_city_summary, calculate_ward_metrics, calculate_ward_grades
from utils.styles import get_base_styles, render_hero, render_footer, get_grade_color

# Historical views before counter was added
HISTORICAL_VIEWS = 18

def get_view_count():
    """Get and increment view count using CountAPI. Only counts once per session."""
    # Check if we've already counted this session
    if 'view_counted' not in st.session_state:
        st.session_state.view_counted = False

    try:
        if not st.session_state.view_counted:
            # First visit this session - increment counter
            response = requests.get(
                "https://countapi.mileshilliard.com/api/v1/hit/chicago-rats-wheretheratsat-visits",
                timeout=5
            )
            st.session_state.view_counted = True
        else:
            # Already counted - just get current value
            response = requests.get(
                "https://countapi.mileshilliard.com/api/v1/get/chicago-rats-wheretheratsat-visits",
                timeout=5
            )

        if response.status_code == 200:
            data = response.json()
            # API returns value as string, need to convert
            count = int(data.get('value', 0))
            return count + HISTORICAL_VIEWS
    except:
        pass

    return None  # Return None if API fails - we'll hide the counter

st.set_page_config(
    page_title="Where the Rats At?",
    page_icon="data/jpeg/Party Rat.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply base styles
st.markdown(get_base_styles(), unsafe_allow_html=True)


def main():
    # Hero Section
    st.markdown(render_hero(
        title="Where the Rats At?",
        subtitle="Grading Chicago's 50 wards on how they respond to rat complaints",
        badge="Live Data"
    ), unsafe_allow_html=True)

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

    # === CITY-WIDE STATS ===
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

    if 'zip_code' in df.columns and df['zip_code'].notna().any():
        peak_zip = df['zip_code'].mode().iloc[0] if not df['zip_code'].mode().empty else "N/A"
    else:
        peak_zip = "N/A"

    peak_ward = int(df['ward'].mode().iloc[0]) if not df['ward'].mode().empty else "N/A"

    stats_html = f'''<div class="card"><div class="card-header">City-Wide Stats / Last 12 Months</div><div class="card-body">
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:1rem;">
    <div class="stat-box"><p class="stat-value">{summary['total_complaints']:,}</p><p class="stat-label">Total Complaints</p></div>
    <div class="stat-box"><p class="stat-value">{summary['median_response_days']}</p><p class="stat-label">Median Response (Days)</p></div>
    <div class="stat-box"><p class="stat-value">{summary['completion_rate']}%</p><p class="stat-label">Completion Rate</p></div>
    <div class="stat-box"><p class="stat-value">{summary['wards_with_data']}</p><p class="stat-label">Wards Tracked</p></div>
    </div>
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;">
    <div class="stat-box"><p class="stat-value">{peak_zip}</p><p class="stat-label">Top Zip Code</p></div>
    <div class="stat-box"><p class="stat-value">{peak_month}</p><p class="stat-label">Peak Month</p></div>
    <div class="stat-box"><p class="stat-value">{peak_time}</p><p class="stat-label">Peak Hour</p></div>
    <div class="stat-box"><p class="stat-value">Ward {peak_ward}</p><p class="stat-label">Most Complaints</p></div>
    </div>
    </div></div>'''
    st.markdown(stats_html, unsafe_allow_html=True)

    # === FASTEST / SLOWEST ===
    col_fast, col_slow = st.columns(2)

    with col_fast:
        top_5 = ward_metrics.head(5)[['ward', 'median_response', 'grade', 'total_complaints']].copy()
        top_5 = top_5.merge(aldermen[['ward', 'alderman']], on='ward', how='left')
        top_5['ward'] = top_5['ward'].astype(int)
        top_5['median_response'] = top_5['median_response'].round(1)

        rows_html = ""
        for _, row in top_5.iterrows():
            grade = row['grade']
            rows_html += f'<tr style="border-bottom:1px solid #e5e5e5;"><td style="padding:0.5rem;font-weight:600;">{int(row["ward"])}</td><td style="padding:0.5rem;">{row["alderman"] or "—"}</td><td style="text-align:right;padding:0.5rem;">{row["median_response"]}</td><td style="text-align:center;padding:0.5rem;"><span class="grade-badge grade-{grade.lower()}">{grade}</span></td></tr>'

        st.markdown(f'<div class="card"><div class="card-header">Fastest Response / Top 5</div><div class="card-body"><table style="width:100%;border-collapse:collapse;font-size:0.875rem;"><tr style="border-bottom:2px solid #171717;"><th style="text-align:left;padding:0.5rem;">Ward</th><th style="text-align:left;padding:0.5rem;">Alderman</th><th style="text-align:right;padding:0.5rem;">Days</th><th style="text-align:center;padding:0.5rem;">Grade</th></tr>{rows_html}</table></div></div>', unsafe_allow_html=True)

    with col_slow:
        bottom_5 = ward_metrics.tail(5)[['ward', 'median_response', 'grade', 'total_complaints']].copy()
        bottom_5 = bottom_5.merge(aldermen[['ward', 'alderman']], on='ward', how='left')
        bottom_5['ward'] = bottom_5['ward'].astype(int)
        bottom_5['median_response'] = bottom_5['median_response'].round(1)
        bottom_5 = bottom_5.sort_values('median_response', ascending=False)

        rows_html = ""
        for _, row in bottom_5.iterrows():
            grade = row['grade']
            rows_html += f'<tr style="border-bottom:1px solid #e5e5e5;"><td style="padding:0.5rem;font-weight:600;">{int(row["ward"])}</td><td style="padding:0.5rem;">{row["alderman"] or "—"}</td><td style="text-align:right;padding:0.5rem;">{row["median_response"]}</td><td style="text-align:center;padding:0.5rem;"><span class="grade-badge grade-{grade.lower()}">{grade}</span></td></tr>'

        st.markdown(f'<div class="card"><div class="card-header">Slowest Response / Bottom 5</div><div class="card-body"><table style="width:100%;border-collapse:collapse;font-size:0.875rem;"><tr style="border-bottom:2px solid #171717;"><th style="text-align:left;padding:0.5rem;">Ward</th><th style="text-align:left;padding:0.5rem;">Alderman</th><th style="text-align:right;padding:0.5rem;">Days</th><th style="text-align:center;padding:0.5rem;">Grade</th></tr>{rows_html}</table></div></div>', unsafe_allow_html=True)

    # === GRADE DISTRIBUTION ===
    grade_order = ['A', 'B', 'C', 'D', 'F']
    grade_counts = ward_metrics['grade'].value_counts().reindex(grade_order, fill_value=0)

    # Build complete HTML block
    grade_items = ""
    for grade in grade_order:
        count = grade_counts.get(grade, 0)
        color = get_grade_color(grade)
        grade_items += f'<div style="text-align:center;min-width:80px;"><div style="background:{color};color:white;font-family:Space Grotesk,sans-serif;font-size:2rem;font-weight:700;width:3.5rem;height:3.5rem;display:flex;align-items:center;justify-content:center;margin:0 auto;border-radius:4px;">{grade}</div><p style="margin:0.5rem 0 0 0;font-size:1.25rem;font-weight:700;">{count}</p><p style="margin:0;font-size:0.75rem;color:#525252;">wards</p></div>'

    st.markdown(f'''<div class="card"><div class="card-header">Grade Distribution</div><div class="card-body"><div style="display:flex;gap:1rem;flex-wrap:wrap;justify-content:center;">{grade_items}</div></div></div>''', unsafe_allow_html=True)

    # === LIVE FEED ===
    st.markdown('<div style="margin-top:1.5rem;"><p style="font-size:0.875rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.75rem;display:flex;align-items:center;gap:0.5rem;"><span class="live-dot"></span> Latest Reports</p></div>', unsafe_allow_html=True)

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

    # View counter
    view_count = get_view_count()
    if view_count:
        st.markdown(f'<p style="text-align:center;color:#737373;font-size:0.875rem;margin:2rem 0 1rem 0;font-style:italic;">{view_count:,} people are curious where the rats at</p>', unsafe_allow_html=True)

    # Footer
    latest_complaint = df['created_date'].max()
    if latest_complaint:
        latest_text = latest_complaint.strftime('%b %d, %Y')
    else:
        latest_text = None

    st.markdown(render_footer(latest_text), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
