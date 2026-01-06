"""About page - Grading methodology and data sources."""

import streamlit as st
from utils.styles import get_base_styles, render_page_header, render_footer, get_grade_color

st.set_page_config(
    page_title="About | Where the Rats At?",
    page_icon="data/jpeg/Party Rat.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(get_base_styles(), unsafe_allow_html=True)
st.markdown('<style>.main .block-container { max-width: 900px; }</style>', unsafe_allow_html=True)

st.markdown(render_page_header(
    title="About This Project",
    subtitle="How we grade Chicago's response to rat complaints"
), unsafe_allow_html=True)

# === GRADING METHODOLOGY ===
st.markdown('<p style="font-size:0.875rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin:1.5rem 0 0.75rem 0;background:#0a0a0a;color:#fafafa;padding:0.875rem 1.25rem;">How Grades Are Calculated</p>', unsafe_allow_html=True)

st.markdown("""
Each of Chicago's 50 wards is scored on **5 factors** using percentile-based ranking.
The best-performing ward on each factor receives 100 points, the worst receives 20 points,
with all others spread evenly between.
""")

st.markdown("### The Five Factors")

factors = [
    ('Speed', '30%', 'Median response time - how fast are complaints resolved?', '#10b981'),
    ('Workload', '25%', 'Volume of complaints handled - credit for high-volume wards', '#84cc16'),
    ('Worst Case', '20%', '90th percentile response - are some complaints left waiting weeks?', '#f59e0b'),
    ('Consistency', '15%', 'Standard deviation - is service reliable or a lottery?', '#f97316'),
    ('Completion', '10%', 'Completion rate - are complaints actually getting resolved?', '#ef4444'),
]

factors_items = ""
for name, weight, desc, color in factors:
    weight_num = int(weight.replace('%', ''))
    factors_items += f'<div style="display:flex;align-items:center;gap:1rem;padding:0.75rem;background:#fafafa;border-radius:4px;"><div style="min-width:100px;"><span style="font-weight:700;">{name}</span><span style="color:#525252;font-size:0.875rem;"> ({weight})</span></div><div style="flex:1;background:#e5e5e5;height:8px;border-radius:4px;overflow:hidden;"><div style="width:{weight_num * 3}%;background:{color};height:100%;"></div></div><div style="flex:2;font-size:0.875rem;color:#525252;">{desc}</div></div>'

st.markdown(f'<div style="display:flex;flex-direction:column;gap:0.75rem;margin:1.5rem 0;">{factors_items}</div>', unsafe_allow_html=True)

st.markdown("### Why These Weights?")

st.markdown("""
- **Speed (30%)**: The core metric residents care about - how long until help arrives?
- **Workload (25%)**: A ward handling 5,000 complaints deserves more credit than one handling 500
- **Worst Case (20%)**: Averages can hide problems. P90 ensures no one waits forever
- **Consistency (15%)**: Residents deserve predictable service, not random outcomes
- **Completion (10%)**: De-emphasized because most wards complete 95%+ of complaints
""")

# === GRADE THRESHOLDS ===
st.markdown('<p style="font-size:0.875rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin:1.5rem 0 0.75rem 0;background:#0a0a0a;color:#fafafa;padding:0.875rem 1.25rem;">Grade Thresholds</p>', unsafe_allow_html=True)

grades = [
    ('A', '80-100', 'Excellent - top performers across all metrics'),
    ('B', '65-79', 'Good - above average performance'),
    ('C', '50-64', 'Average - room for improvement'),
    ('D', '35-49', 'Below Average - significant issues need attention'),
    ('F', '0-34', 'Poor - needs immediate improvement'),
]

grades_items = ""
for grade, score_range, meaning in grades:
    color = get_grade_color(grade)
    grades_items += f'<div style="display:flex;align-items:center;gap:1rem;padding:0.5rem;"><div style="width:2.5rem;height:2.5rem;background:{color};color:white;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:1.25rem;border-radius:4px;">{grade}</div><div style="min-width:80px;font-weight:600;">{score_range}</div><div style="color:#525252;">{meaning}</div></div>'

st.markdown(f'<div style="display:flex;flex-direction:column;gap:0.5rem;margin:1rem 0;">{grades_items}</div>', unsafe_allow_html=True)

st.markdown("""
**Final Score Formula:**
```
Final Score = (Speed × 0.30) + (Workload × 0.25) + (Worst Case × 0.20)
            + (Consistency × 0.15) + (Completion × 0.10)
```
""")

# === WHY THIS APPROACH ===
st.markdown('<p style="font-size:0.875rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin:1.5rem 0 0.75rem 0;background:#0a0a0a;color:#fafafa;padding:0.875rem 1.25rem;">Why This Approach?</p>', unsafe_allow_html=True)

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

# === DATA SOURCE ===
st.markdown('<p style="font-size:0.875rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin:1.5rem 0 0.75rem 0;background:#0a0a0a;color:#fafafa;padding:0.875rem 1.25rem;">Data Source</p>', unsafe_allow_html=True)

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

# === CREDITS ===
st.markdown('<p style="font-size:0.875rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin:1.5rem 0 0.75rem 0;background:#0a0a0a;color:#fafafa;padding:0.875rem 1.25rem;">Credits</p>', unsafe_allow_html=True)

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

st.markdown(render_footer(), unsafe_allow_html=True)
