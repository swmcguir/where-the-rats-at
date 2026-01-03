"""Temporal Analysis page - When do rats get reported?"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data.fetch import fetch_rodent_complaints, get_dataset_metadata

st.set_page_config(
    page_title="Temporal Patterns | Where the Rats At?",
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

    .insight-box {
        background: #000;
        color: #fff;
        padding: 20px;
        text-align: center;
        margin: 20px 0;
    }

    .insight-value {
        font-size: 2rem;
        font-weight: 700;
    }

    .insight-label {
        font-size: 0.9rem;
        margin-top: 5px;
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
    <h1 class="page-title">When Do Rats Get Reported?</h1>
    <p class="page-subtitle">Temporal patterns in Chicago rat complaints</p>
</div>
""", unsafe_allow_html=True)

# Load data
with st.spinner("Loading complaint data..."):
    df = fetch_rodent_complaints(days_back=365)

if df.empty:
    st.error("No data available.")
    st.stop()

# Day of week names
day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# Calculate peak times
hour_counts = df['created_hour'].value_counts().sort_index()
day_counts = df['created_day_of_week'].value_counts().sort_index()

peak_hour = hour_counts.idxmax()
peak_day = day_counts.idxmax()

# Format peak hour nicely
if peak_hour == 0:
    peak_hour_str = "12 AM"
elif peak_hour < 12:
    peak_hour_str = f"{peak_hour} AM"
elif peak_hour == 12:
    peak_hour_str = "12 PM"
else:
    peak_hour_str = f"{peak_hour - 12} PM"

# Key insights
st.markdown("""
<div class="retro-card">
    <div class="retro-card-header">Peak Complaint Times</div>
    <div class="retro-card-body">
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Peak Hour", peak_hour_str, f"{hour_counts[peak_hour]:,} complaints")

with col2:
    st.metric("Peak Day", day_names[peak_day], f"{day_counts[peak_day]:,} complaints")

with col3:
    # Find quietest hour
    quiet_hour = hour_counts.idxmin()
    if quiet_hour == 0:
        quiet_hour_str = "12 AM"
    elif quiet_hour < 12:
        quiet_hour_str = f"{quiet_hour} AM"
    elif quiet_hour == 12:
        quiet_hour_str = "12 PM"
    else:
        quiet_hour_str = f"{quiet_hour - 12} PM"
    st.metric("Quietest Hour", quiet_hour_str, f"{hour_counts[quiet_hour]:,} complaints")

st.markdown('</div></div>', unsafe_allow_html=True)

# Hour x Day heatmap
st.markdown("""
<div class="retro-card">
    <div class="retro-card-header">Complaint Heatmap / Hour × Day of Week</div>
    <div class="retro-card-body">
""", unsafe_allow_html=True)

# Create pivot table for heatmap
heatmap_data = df.groupby(['created_day_of_week', 'created_hour']).size().reset_index(name='count')
heatmap_pivot = heatmap_data.pivot(index='created_hour', columns='created_day_of_week', values='count').fillna(0)

# Rename columns to day names
heatmap_pivot.columns = [day_names[i] for i in heatmap_pivot.columns]

fig_heatmap = px.imshow(
    heatmap_pivot,
    labels=dict(x="Day of Week", y="Hour of Day", color="Complaints"),
    aspect="auto",
    color_continuous_scale="YlOrRd"
)

fig_heatmap.update_layout(
    height=500,
    font_family="Space Mono, monospace",
    paper_bgcolor='rgba(0,0,0,0)',
    yaxis=dict(
        tickmode='array',
        tickvals=list(range(24)),
        ticktext=[f"{h}:00" for h in range(24)]
    )
)

st.plotly_chart(fig_heatmap, use_container_width=True)
st.markdown('</div></div>', unsafe_allow_html=True)

# Two column layout
col_hour, col_day = st.columns(2)

with col_hour:
    st.markdown("""
    <div class="retro-card">
        <div class="retro-card-header">Complaints by Hour</div>
        <div class="retro-card-body">
    """, unsafe_allow_html=True)

    hour_df = pd.DataFrame({
        'Hour': [f"{h}:00" for h in range(24)],
        'Complaints': [hour_counts.get(h, 0) for h in range(24)]
    })

    fig_hour = px.bar(
        hour_df,
        x='Hour',
        y='Complaints',
        color='Complaints',
        color_continuous_scale='Blues'
    )

    fig_hour.update_layout(
        height=350,
        showlegend=False,
        font_family="Space Mono, monospace",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        coloraxis_showscale=False
    )

    st.plotly_chart(fig_hour, use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

with col_day:
    st.markdown("""
    <div class="retro-card">
        <div class="retro-card-header">Complaints by Day of Week</div>
        <div class="retro-card-body">
    """, unsafe_allow_html=True)

    day_df = pd.DataFrame({
        'Day': day_names,
        'Complaints': [day_counts.get(i, 0) for i in range(7)]
    })

    fig_day = px.bar(
        day_df,
        x='Day',
        y='Complaints',
        color='Complaints',
        color_continuous_scale='Greens'
    )

    fig_day.update_layout(
        height=350,
        showlegend=False,
        font_family="Space Mono, monospace",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        coloraxis_showscale=False,
        xaxis={'categoryorder': 'array', 'categoryarray': day_names}
    )

    st.plotly_chart(fig_day, use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

# Monthly trends
st.markdown("""
<div class="retro-card">
    <div class="retro-card-header">Monthly Complaint Volume / Rat Season</div>
    <div class="retro-card-body">
""", unsafe_allow_html=True)

# Group by month-year for proper time series
df['month_year'] = df['created_date'].dt.to_period('M')
month_year_counts = df.groupby('month_year').size().reset_index(name='Complaints')
month_year_counts['Month'] = month_year_counts['month_year'].apply(lambda x: x.strftime('%b %Y'))
month_year_counts = month_year_counts.sort_values('month_year')

# Find peak month
peak_idx = month_year_counts['Complaints'].idxmax()
peak_month_name = month_year_counts.loc[peak_idx, 'Month']
peak_complaints = month_year_counts.loc[peak_idx, 'Complaints']

fig_month = px.bar(
    month_year_counts,
    x='Month',
    y='Complaints',
    color='Complaints',
    color_continuous_scale='OrRd'
)

fig_month.update_layout(
    height=350,
    showlegend=False,
    font_family="Space Mono, monospace",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    coloraxis_showscale=False,
    xaxis={'categoryorder': 'array', 'categoryarray': month_year_counts['Month'].tolist()}
)

st.plotly_chart(fig_month, use_container_width=True)

st.info(f"Peak Rat Season: **{peak_month_name}** with {peak_complaints:,} complaints")

st.markdown('</div></div>', unsafe_allow_html=True)

# Methodology
st.caption("""
**Methodology:** Temporal analysis based on complaint creation timestamps from the last 12 months.
Hour of day uses 24-hour format (0-23). Day of week: Monday=0, Sunday=6.
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
