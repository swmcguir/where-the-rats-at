"""Temporal Analysis page - When do rats get reported?"""

import streamlit as st
import pandas as pd
import plotly.express as px
from data.fetch import fetch_rodent_complaints, get_dataset_metadata
from utils.styles import get_base_styles, render_page_header, render_footer

st.set_page_config(
    page_title="Temporal Patterns | Where the Rats At?",
    page_icon="data/jpeg/Party Rat.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(get_base_styles(), unsafe_allow_html=True)

st.markdown(render_page_header(
    title="When Do Rats Get Reported?",
    subtitle="Temporal patterns in Chicago rat complaints"
), unsafe_allow_html=True)

with st.spinner("Loading complaint data..."):
    df = fetch_rodent_complaints(days_back=365)

if df.empty:
    st.error("No data available.")
    st.stop()

day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

hour_counts = df['created_hour'].value_counts().sort_index()
day_counts = df['created_day_of_week'].value_counts().sort_index()

peak_hour = hour_counts.idxmax()
peak_day = day_counts.idxmax()
quiet_hour = hour_counts.idxmin()

def format_hour(h):
    if h == 0: return "12 AM"
    elif h < 12: return f"{h} AM"
    elif h == 12: return "12 PM"
    else: return f"{h - 12} PM"

peak_hour_str = format_hour(peak_hour)
quiet_hour_str = format_hour(quiet_hour)

# Peak times - complete HTML block
st.markdown(f'<div class="card"><div class="card-header">Peak Complaint Times</div><div class="card-body"><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;"><div class="stat-box"><p class="stat-value">{peak_hour_str}</p><p class="stat-label">Peak Hour</p><p class="stat-delta">{hour_counts[peak_hour]:,} complaints</p></div><div class="stat-box"><p class="stat-value">{day_names[peak_day]}</p><p class="stat-label">Peak Day</p><p class="stat-delta">{day_counts[peak_day]:,} complaints</p></div><div class="stat-box"><p class="stat-value">{quiet_hour_str}</p><p class="stat-label">Quietest Hour</p><p class="stat-delta">{hour_counts[quiet_hour]:,} complaints</p></div></div></div></div>', unsafe_allow_html=True)

# Heatmap section - use subheader instead of split HTML
st.markdown('<p style="font-size:0.875rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin:1.5rem 0 0.75rem 0;background:#0a0a0a;color:#fafafa;padding:0.875rem 1.25rem;">Complaint Heatmap / Hour x Day of Week</p>', unsafe_allow_html=True)

heatmap_data = df.groupby(['created_day_of_week', 'created_hour']).size().reset_index(name='count')
heatmap_pivot = heatmap_data.pivot(index='created_hour', columns='created_day_of_week', values='count').fillna(0)
heatmap_pivot.columns = [day_names[i] for i in heatmap_pivot.columns]

fig_heatmap = px.imshow(
    heatmap_pivot,
    labels=dict(x="Day of Week", y="Hour of Day", color="Complaints"),
    aspect="auto",
    color_continuous_scale=[[0, '#fef3c7'], [0.5, '#f97316'], [1, '#991b1b']]
)
fig_heatmap.update_layout(
    height=500,
    font_family="Space Mono, monospace",
    paper_bgcolor='rgba(0,0,0,0)',
    yaxis=dict(tickmode='array', tickvals=list(range(24)), ticktext=[f"{h}:00" for h in range(24)], tickfont={'family': 'Space Mono, monospace', 'size': 10}),
    xaxis=dict(tickfont={'family': 'Space Mono, monospace', 'size': 11}),
    coloraxis_colorbar=dict(title=dict(text="Complaints", font={'family': 'Space Mono, monospace', 'size': 11}), tickfont={'family': 'Space Mono, monospace', 'size': 10}),
    margin={'l': 60, 'r': 20, 't': 20, 'b': 40}
)
st.plotly_chart(fig_heatmap, use_container_width=True)

# Two column charts
col_hour, col_day = st.columns(2)

with col_hour:
    st.markdown('<p style="font-size:0.875rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin:0.5rem 0 0.75rem 0;background:#0a0a0a;color:#fafafa;padding:0.875rem 1.25rem;">Complaints by Hour</p>', unsafe_allow_html=True)
    hour_df = pd.DataFrame({'Hour': [f"{h}:00" for h in range(24)], 'Complaints': [hour_counts.get(h, 0) for h in range(24)]})
    fig_hour = px.bar(hour_df, x='Hour', y='Complaints', color='Complaints', color_continuous_scale=[[0, '#dbeafe'], [1, '#1d4ed8']])
    fig_hour.update_layout(height=350, showlegend=False, font_family="Space Mono, monospace", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', coloraxis_showscale=False, xaxis={'tickfont': {'size': 9}, 'gridcolor': '#e5e5e5'}, yaxis={'gridcolor': '#e5e5e5'}, margin={'l': 40, 'r': 20, 't': 20, 'b': 40})
    st.plotly_chart(fig_hour, use_container_width=True)

with col_day:
    st.markdown('<p style="font-size:0.875rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin:0.5rem 0 0.75rem 0;background:#0a0a0a;color:#fafafa;padding:0.875rem 1.25rem;">Complaints by Day of Week</p>', unsafe_allow_html=True)
    day_df = pd.DataFrame({'Day': day_names, 'Complaints': [day_counts.get(i, 0) for i in range(7)]})
    fig_day = px.bar(day_df, x='Day', y='Complaints', color='Complaints', color_continuous_scale=[[0, '#d1fae5'], [1, '#059669']])
    fig_day.update_layout(height=350, showlegend=False, font_family="Space Mono, monospace", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', coloraxis_showscale=False, xaxis={'categoryorder': 'array', 'categoryarray': day_names, 'tickfont': {'size': 10}, 'gridcolor': '#e5e5e5'}, yaxis={'gridcolor': '#e5e5e5'}, margin={'l': 40, 'r': 20, 't': 20, 'b': 40})
    st.plotly_chart(fig_day, use_container_width=True)

# Monthly trends
st.markdown('<p style="font-size:0.875rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin:1.5rem 0 0.75rem 0;background:#0a0a0a;color:#fafafa;padding:0.875rem 1.25rem;">Monthly Complaint Volume / Rat Season</p>', unsafe_allow_html=True)

df['month_year'] = df['created_date'].dt.to_period('M')
month_year_counts = df.groupby('month_year').size().reset_index(name='Complaints')
month_year_counts['Month'] = month_year_counts['month_year'].apply(lambda x: x.strftime('%b %Y'))
month_year_counts = month_year_counts.sort_values('month_year')

peak_idx = month_year_counts['Complaints'].idxmax()
peak_month_name = month_year_counts.loc[peak_idx, 'Month']
peak_complaints = month_year_counts.loc[peak_idx, 'Complaints']

fig_month = px.bar(month_year_counts, x='Month', y='Complaints', color='Complaints', color_continuous_scale=[[0, '#fef3c7'], [0.5, '#f97316'], [1, '#dc2626']])
fig_month.update_layout(height=350, showlegend=False, font_family="Space Mono, monospace", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', coloraxis_showscale=False, xaxis={'categoryorder': 'array', 'categoryarray': month_year_counts['Month'].tolist(), 'tickfont': {'size': 10}, 'gridcolor': '#e5e5e5'}, yaxis={'gridcolor': '#e5e5e5'}, margin={'l': 40, 'r': 20, 't': 20, 'b': 60})
st.plotly_chart(fig_month, use_container_width=True)

st.markdown(f'<div style="background:linear-gradient(90deg,#fef3c7 0%,#fde68a 100%);border-left:4px solid #f59e0b;padding:1rem;"><strong>Peak Rat Season:</strong> {peak_month_name} with {peak_complaints:,} complaints</div>', unsafe_allow_html=True)

st.caption("**Methodology:** Temporal analysis based on complaint creation timestamps from the last 12 months.")

metadata = get_dataset_metadata()
update_text = metadata['last_updated'].strftime('%b %d, %Y') if metadata['last_updated'] else None
st.markdown(render_footer(update_text), unsafe_allow_html=True)
