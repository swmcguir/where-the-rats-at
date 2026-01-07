"""Ward Report Card page - Shareable grade for any ward."""

import streamlit as st
import pandas as pd
from urllib.parse import quote
from data.fetch import fetch_rodent_complaints, fetch_aldermen
from utils.metrics import calculate_ward_metrics, calculate_ward_grades, get_city_summary
from utils.styles import get_base_styles, render_page_header, render_footer, get_grade_color

st.set_page_config(
    page_title="Ward Report Card | Where the Rats At?",
    page_icon="data/jpeg/Party Rat.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(get_base_styles(), unsafe_allow_html=True)

st.markdown(render_page_header(
    title="Ward Report Card",
    subtitle="Get a shareable grade for any Chicago ward"
), unsafe_allow_html=True)

with st.spinner("Loading data..."):
    df = fetch_rodent_complaints(days_back=365)
    aldermen = fetch_aldermen()

if df.empty:
    st.error("No data available.")
    st.stop()

ward_metrics = calculate_ward_metrics(df)
ward_metrics = calculate_ward_grades(ward_metrics)
city_summary = get_city_summary(df)

ward_metrics = ward_metrics.merge(aldermen[['ward', 'alderman', 'ward_phone', 'website']], on='ward', how='left')

available_wards = sorted(ward_metrics['ward'].dropna().astype(int).unique())

selected_ward = st.selectbox("Select Your Ward", options=available_wards, index=0)

ward_data = ward_metrics[ward_metrics['ward'] == selected_ward].iloc[0]

grade_info = {'A': ('Excellent', 'Top performers across all metrics'), 'B': ('Good', 'Above average performance'), 'C': ('Average', 'Room for improvement'), 'D': ('Below Average', 'Significant issues need attention'), 'F': ('Poor', 'Needs immediate improvement')}

grade = ward_data['grade']
color = get_grade_color(grade)
glow = get_grade_color(grade, 'glow')
description, detail = grade_info[grade]
low_sample_warning = f'<p style="color:#f97316;font-size:0.875rem;margin-top:1rem;">Low sample size ({int(ward_data["total_complaints"])} complaints)</p>' if ward_data.get('low_sample_size', False) else ""

# Grade card - single compact block
st.markdown(f'<div class="card" style="max-width:600px;margin:0 auto 2rem auto;"><div class="card-header" style="text-align:center;">Ward {selected_ward} Report Card</div><div class="card-body" style="text-align:center;padding:3rem 2rem;"><div style="width:140px;height:140px;background:{color};color:white;font-family:Space Grotesk,sans-serif;font-size:6rem;font-weight:700;display:flex;align-items:center;justify-content:center;margin:0 auto;border-radius:12px;box-shadow:0 10px 40px {glow};">{grade}</div><h2 style="font-family:Space Grotesk,sans-serif;font-size:1.75rem;margin:1.5rem 0 0.5rem 0;">{description}</h2><p style="color:#525252;margin:0;">{detail}</p>{low_sample_warning}</div></div>', unsafe_allow_html=True)

if pd.notna(ward_data.get('alderman')):
    st.markdown(f'<p style="text-align:center;font-size:1rem;margin-bottom:2rem;"><strong>Alderman:</strong> {ward_data["alderman"]}</p>', unsafe_allow_html=True)

# Performance metrics
vs_city_pct = ward_data['vs_city_median']
delta_text = f"{vs_city_pct:.0f}%" if vs_city_pct <= 0 else f"+{vs_city_pct:.0f}%"
delta_class = "positive" if vs_city_pct <= 0 else "negative"
rank = int(ward_data['rank'])
rank_color = "#10b981" if rank <= 10 else ("#f59e0b" if rank <= 30 else "#ef4444")

st.markdown(f'<div class="card"><div class="card-header">Performance Metrics</div><div class="card-body"><div class="stats-grid-4"><div class="stat-box"><p class="stat-value">{ward_data["median_response"]:.1f}</p><p class="stat-label">Median Response (Days)</p><p class="stat-delta {delta_class}">{delta_text} vs city</p></div><div class="stat-box"><p class="stat-value">#{rank}</p><p class="stat-label">City Ranking</p><p style="font-size:0.75rem;color:{rank_color};margin-top:0.25rem;">of 50 wards</p></div><div class="stat-box"><p class="stat-value">{int(ward_data["total_complaints"]):,}</p><p class="stat-label">Total Complaints</p></div><div class="stat-box"><p class="stat-value">{ward_data["completion_rate"]:.1f}%</p><p class="stat-label">Completion Rate</p></div></div></div></div>', unsafe_allow_html=True)

# Factor breakdown
factors = [('Speed', ward_data.get('speed_score', 0), '30%'), ('Workload', ward_data.get('volume_score', 0), '25%'), ('Worst Case', ward_data.get('p90_score', 0), '20%'), ('Consistency', ward_data.get('consistency_score', 0), '15%'), ('Completion', ward_data.get('completion_score', 0), '10%')]

factor_items = ""
for name, score, weight in factors:
    score_color = "#10b981" if score >= 70 else ("#f59e0b" if score >= 40 else "#ef4444")
    factor_items += f'<div style="text-align:center;padding:1rem;background:#fafafa;border-radius:4px;"><p style="font-size:2rem;font-weight:700;margin:0;color:{score_color};">{score:.0f}</p><p style="font-size:0.875rem;font-weight:600;margin:0.5rem 0 0.25rem 0;">{name}</p><p style="font-size:0.6875rem;color:#a3a3a3;margin:0;">{weight}</p></div>'

final_score = ward_data.get('final_score', 0)

st.markdown(f'<div class="card"><div class="card-header">Grade Factor Breakdown</div><div class="card-body"><div class="stats-grid-5">{factor_items}</div><div style="margin-top:1.5rem;"><div style="display:flex;justify-content:space-between;font-size:0.875rem;margin-bottom:0.5rem;"><span>Final Score</span><span style="font-weight:700;">{final_score:.1f}/100</span></div><div style="background:#e5e5e5;height:12px;border-radius:6px;overflow:hidden;"><div style="background:{color};height:100%;width:{final_score}%;"></div></div></div></div></div>', unsafe_allow_html=True)

# Comparison table
resp_diff = ward_data['median_response'] - city_summary['median_response_days']
resp_color = "#10b981" if resp_diff <= 0 else "#ef4444"
comp_diff = ward_data['completion_rate'] - city_summary['completion_rate']
comp_color = "#10b981" if comp_diff >= 0 else "#ef4444"

st.markdown(f'<div class="card"><div class="card-header">Compared to City Average</div><div class="card-body"><table style="width:100%;border-collapse:collapse;font-size:0.9375rem;"><tr style="border-bottom:2px solid #171717;"><th style="text-align:left;padding:0.75rem;">Metric</th><th style="text-align:right;padding:0.75rem;">Ward {selected_ward}</th><th style="text-align:right;padding:0.75rem;">City Average</th><th style="text-align:right;padding:0.75rem;">Difference</th></tr><tr style="border-bottom:1px solid #e5e5e5;"><td style="padding:0.75rem;">Response Time (days)</td><td style="text-align:right;padding:0.75rem;font-weight:600;">{ward_data["median_response"]:.1f}</td><td style="text-align:right;padding:0.75rem;">{city_summary["median_response_days"]}</td><td style="text-align:right;padding:0.75rem;color:{resp_color};">{"+" if resp_diff > 0 else ""}{resp_diff:.1f}</td></tr><tr><td style="padding:0.75rem;">Completion Rate (%)</td><td style="text-align:right;padding:0.75rem;font-weight:600;">{ward_data["completion_rate"]:.1f}%</td><td style="text-align:right;padding:0.75rem;">{city_summary["completion_rate"]}%</td><td style="text-align:right;padding:0.75rem;color:{comp_color};">{"+" if comp_diff >= 0 else ""}{comp_diff:.1f}%</td></tr></table></div></div>', unsafe_allow_html=True)

# Share section
share_text = f"Ward {selected_ward} gets a {ward_data['grade']} for rat response time! Median: {ward_data['median_response']:.1f} days. Rank: #{int(ward_data['rank'])} of 50 wards."
if pd.notna(ward_data.get('alderman')):
    share_text += f" Alderman: {ward_data['alderman']}"
share_text += " #WhereTheRatsAt #Chicago311"

st.markdown('<p style="font-size:0.875rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin:1.5rem 0 0.75rem 0;background:#0a0a0a;color:#fafafa;padding:0.875rem 1.25rem;">Share This Report Card</p>', unsafe_allow_html=True)
st.code(share_text, language=None)

col_share1, col_share2 = st.columns(2)
with col_share1:
    st.link_button("Share on X", f"https://twitter.com/intent/tweet?text={quote(share_text, safe='')}", use_container_width=True)
with col_share2:
    st.link_button("Share on LinkedIn", "https://www.linkedin.com/sharing/share-offsite/?url=https://chicago-rats.streamlit.app", use_container_width=True)

# Contact info
if pd.notna(ward_data.get('alderman')):
    phone_html = f'<p style="margin:0.5rem 0;"><strong>Phone:</strong> {ward_data["ward_phone"]}</p>' if pd.notna(ward_data.get('ward_phone')) else ""
    st.markdown(f'<div class="card"><div class="card-header">Contact Your Alderman</div><div class="card-body"><p style="font-size:1.125rem;font-weight:600;margin:0 0 1rem 0;">{ward_data["alderman"]}</p>{phone_html}</div></div>', unsafe_allow_html=True)
    if pd.notna(ward_data.get('website')) and str(ward_data['website']).lower() != 'nan':
        st.link_button("Visit Ward Website", str(ward_data['website']))

st.caption("**How grades are calculated:** Multi-factor scoring: Speed (30%), Workload (25%), Worst-Case (20%), Consistency (15%), Completion (10%). A=80+, B=65-79, C=50-64, D=35-49, F=<35.")

st.markdown(render_footer(), unsafe_allow_html=True)
