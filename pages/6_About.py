"""About page - Grading methodology and data sources."""

import streamlit as st

st.set_page_config(
    page_title="About | Where the Rats At?",
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
        max-width: 900px;
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
</style>
""", unsafe_allow_html=True)

# Page Header
st.markdown("""
<div class="page-header">
    <h1 class="page-title">About This Project</h1>
    <p class="page-subtitle" style="text-align: center;">How we grade Chicago's response to rat complaints</p>
</div>
""", unsafe_allow_html=True)

# Grading Methodology
st.markdown("""
<div class="retro-card">
    <div class="retro-card-header">How Grades Are Calculated</div>
    <div class="retro-card-body">
""", unsafe_allow_html=True)

st.markdown("""
Each of Chicago's 50 wards is scored on **5 factors** using percentile-based ranking.
The best-performing ward on each factor receives 100 points, the worst receives 20 points,
with all others spread evenly between.
""")

st.markdown("### The Five Factors")

factors_data = {
    "Factor": ["Speed", "Workload", "Worst Case", "Consistency", "Completion"],
    "Weight": ["30%", "25%", "20%", "15%", "10%"],
    "What It Measures": [
        "Median response time - how fast are complaints resolved?",
        "Volume of complaints handled - credit for high-volume wards",
        "90th percentile response - are some complaints left waiting weeks?",
        "Standard deviation - is service reliable or a lottery?",
        "Completion rate - are complaints actually getting resolved?"
    ]
}

import pandas as pd
st.table(pd.DataFrame(factors_data))

st.markdown("### Why These Weights?")

st.markdown("""
- **Speed (30%)**: The core metric residents care about - how long until help arrives?
- **Workload (25%)**: A ward handling 5,000 complaints deserves more credit than one handling 500
- **Worst Case (20%)**: Averages can hide problems. P90 ensures no one waits forever
- **Consistency (15%)**: Residents deserve predictable service, not random outcomes
- **Completion (10%)**: De-emphasized because most wards complete 95%+ of complaints
""")

st.markdown("</div></div>", unsafe_allow_html=True)

# Grade Thresholds
st.markdown("""
<div class="retro-card">
    <div class="retro-card-header">Grade Thresholds</div>
    <div class="retro-card-body">
""", unsafe_allow_html=True)

grades_data = {
    "Grade": ["A", "B", "C", "D", "F"],
    "Score Range": ["80-100", "65-79", "50-64", "35-49", "0-34"],
    "Meaning": [
        "Excellent - top performers across all metrics",
        "Good - above average performance",
        "Average - room for improvement",
        "Below Average - significant issues need attention",
        "Poor - needs immediate improvement"
    ]
}

st.table(pd.DataFrame(grades_data))

st.markdown("""
**Final Score Formula:**
```
Final Score = (Speed × 0.30) + (Workload × 0.25) + (Worst Case × 0.20)
            + (Consistency × 0.15) + (Completion × 0.10)
```
""")

st.markdown("</div></div>", unsafe_allow_html=True)

# Why This Approach
st.markdown("""
<div class="retro-card">
    <div class="retro-card-header">Why This Approach?</div>
    <div class="retro-card-body">
""", unsafe_allow_html=True)

st.markdown("""
### The Problem with Simple Rankings

A naive approach would rank wards purely by median response time. But this ignores important context:

1. **Volume matters**: Ward 25 handling 3,000 complaints in 5 days is more impressive than Ward 42 handling 300 in 4 days

2. **Averages lie**: A ward could have a 5-day median but leave 10% of complaints waiting 30+ days. The P90 metric catches this.

3. **Consistency matters**: Would you rather have a ward that always responds in 5 days, or one that sometimes responds in 1 day and sometimes in 20?

### Our Solution: Multi-Factor Grading

By combining 5 metrics with appropriate weights, we create a more holistic picture of ward performance. This approach:

- **Rewards hard work**: High-volume wards get credit for their workload
- **Catches outliers**: The P90 metric accounts for this
- **Values reliability**: Consistent service is rewarded
- **Stays grounded**: Percentile-based scoring adapts to actual data distributions
""")

st.markdown("</div></div>", unsafe_allow_html=True)

# Data Source
st.markdown("""
<div class="retro-card">
    <div class="retro-card-header">Data Source</div>
    <div class="retro-card-body">
""", unsafe_allow_html=True)

st.markdown("""
All data comes from the **Chicago Data Portal**, the city's official open data platform.

| Field | Source |
|-------|--------|
| Rat complaints | [311 Service Requests](https://data.cityofchicago.org/Service-Requests/311-Service-Requests/v6vf-nfxy) |
| Alderman info | [Ward Offices](https://data.cityofchicago.org/Facilities-Geo-Boundaries/Ward-Offices/htai-wnw4) |

**Update Frequency:**
- Data refreshes every **1 hour** (cached for performance)
- Covers the last **12 months** of rodent baiting complaints
- Typically includes **40,000-60,000** complaints per year

**What counts as a complaint?**
- Service Request Type: "Rodent Baiting/Rat Complaint"
- Response time = Days from complaint creation to closure
""")

st.markdown("</div></div>", unsafe_allow_html=True)

# Credits
st.markdown("""
<div class="retro-card">
    <div class="retro-card-header">Credits</div>
    <div class="retro-card-body">
""", unsafe_allow_html=True)

st.markdown("""
**Created by:** [Sean W. McGuire](https://www.linkedin.com/in/seanwmcguire/)

**Built with:**
- [Streamlit](https://streamlit.io) - Web framework
- [Plotly](https://plotly.com) - Interactive charts
- [Folium](https://python-visualization.github.io/folium/) - Maps
- [Chicago Data Portal](https://data.cityofchicago.org) - Open data

**Why I built this:**

City of Chicago tracks a lot of data about rats. Enough data that it felt irresponsible not to turn it into a live scorecard and competition. This dashboard seeks to track performance ward by ward, so maybe one day we'll have a slightly less ratty future.
""")

st.markdown("</div></div>", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="site-footer">
    <p>Data from <a href="https://data.cityofchicago.org">Chicago Data Portal</a></p>
    <p style="margin-top: 15px;">&copy; 2025 <a href="https://www.linkedin.com/in/seanwmcguire/">Sean W. McGuire</a>. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
