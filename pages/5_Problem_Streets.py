"""Problem Streets page - Top complained-about streets in Chicago."""

import streamlit as st
import pandas as pd
import plotly.express as px
from data.fetch import fetch_rodent_complaints, get_dataset_metadata
from utils.styles import get_base_styles, render_page_header, render_footer

st.set_page_config(
    page_title="Problem Streets | Where the Rats At?",
    page_icon="data/jpeg/Party Rat.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(get_base_styles(), unsafe_allow_html=True)

st.markdown(render_page_header(
    title="Problem Streets",
    subtitle="Which streets have the most rat complaints?"
), unsafe_allow_html=True)

with st.spinner("Loading complaint data..."):
    df = fetch_rodent_complaints(days_back=365)

if df.empty:
    st.error("No data available.")
    st.stop()

st.sidebar.header("Filters")

available_wards = sorted(df['ward'].dropna().astype(int).unique())
selected_ward = st.sidebar.selectbox(
    "Filter by Ward",
    options=["All Wards"] + [f"Ward {w}" for w in available_wards],
    index=0
)

if selected_ward != "All Wards":
    ward_num = int(selected_ward.replace("Ward ", ""))
    df_filtered = df[df['ward'] == ward_num]
    filter_label = f"Ward {ward_num}"
else:
    df_filtered = df
    filter_label = "City-Wide"

street_stats = df_filtered.groupby('street_name').agg(
    complaints=('sr_number', 'count'),
    avg_response=('response_days', 'mean'),
    median_response=('response_days', 'median'),
    completion_rate=('status', lambda x: (x == 'Completed').mean() * 100)
).reset_index()

street_stats = street_stats.dropna(subset=['street_name'])
street_stats = street_stats[street_stats['street_name'].str.strip() != '']
street_stats = street_stats.sort_values('complaints', ascending=False)

# Top 20 chart
st.markdown(f'<p style="font-size:0.875rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin:1rem 0 0.75rem 0;background:#0a0a0a;color:#fafafa;padding:0.875rem 1.25rem;">Top 20 Problem Streets / {filter_label}</p>', unsafe_allow_html=True)

top_20 = street_stats.head(20)

fig = px.bar(
    top_20,
    x='complaints',
    y='street_name',
    orientation='h',
    color='avg_response',
    color_continuous_scale=[[0, '#10b981'], [0.5, '#f59e0b'], [1, '#ef4444']],
    labels={'complaints': 'Number of Complaints', 'street_name': 'Street', 'avg_response': 'Avg Response (Days)'}
)
fig.update_layout(
    height=600,
    yaxis={'categoryorder': 'total ascending', 'title': None, 'tickfont': {'family': 'Space Mono, monospace', 'size': 11}},
    xaxis={'title': {'text': 'Number of Complaints', 'font': {'family': 'Space Grotesk, sans-serif', 'size': 12}}, 'tickfont': {'family': 'Space Mono, monospace', 'size': 11}, 'gridcolor': '#e5e5e5'},
    showlegend=False,
    font_family="Space Mono, monospace",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    coloraxis_colorbar=dict(title=dict(text="Avg Days", font={'family': 'Space Mono, monospace', 'size': 11}), tickfont={'family': 'Space Mono, monospace', 'size': 10}),
    margin={'l': 20, 'r': 20, 't': 20, 'b': 40}
)
st.plotly_chart(fig, use_container_width=True)

# Summary stats
top_20_complaints = top_20['complaints'].sum()
total_complaints = street_stats['complaints'].sum()
pct = (top_20_complaints / total_complaints * 100) if total_complaints > 0 else 0
worst_street = top_20.iloc[0]['street_name'] if len(top_20) > 0 else "N/A"
worst_count = int(top_20.iloc[0]['complaints']) if len(top_20) > 0 else 0

st.markdown(f'<div class="card"><div class="card-header">Summary / {filter_label}</div><div class="card-body"><div class="stats-grid-3"><div class="stat-box"><p class="stat-value">{len(street_stats):,}</p><p class="stat-label">Total Streets</p></div><div class="stat-box"><p class="stat-value" style="font-size:1.25rem;">{worst_street}</p><p class="stat-label">Worst Street ({worst_count:,} complaints)</p></div><div class="stat-box"><p class="stat-value">{pct:.0f}%</p><p class="stat-label">Top 20 Streets (of all complaints)</p></div></div></div></div>', unsafe_allow_html=True)

# Data table
st.markdown(f'<p style="font-size:0.875rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin:1.5rem 0 0.75rem 0;background:#0a0a0a;color:#fafafa;padding:0.875rem 1.25rem;">All Streets / {filter_label}</p>', unsafe_allow_html=True)

display_table = street_stats.head(100).copy()
display_table.columns = ['Street', 'Complaints', 'Avg Response (Days)', 'Median Response (Days)', 'Completion %']
display_table['Avg Response (Days)'] = display_table['Avg Response (Days)'].round(1)
display_table['Median Response (Days)'] = display_table['Median Response (Days)'].round(1)
display_table['Completion %'] = display_table['Completion %'].round(1)

st.dataframe(
    display_table,
    hide_index=True,
    use_container_width=True,
    column_config={
        'Complaints': st.column_config.NumberColumn('Complaints', format='%d'),
        'Avg Response (Days)': st.column_config.NumberColumn('Avg Response', format='%.1f'),
        'Median Response (Days)': st.column_config.NumberColumn('Median Response', format='%.1f'),
        'Completion %': st.column_config.NumberColumn('Completion %', format='%.1f%%')
    }
)

csv = display_table.to_csv(index=False)
st.download_button(label="Download CSV", data=csv, file_name=f"chicago_problem_streets_{filter_label.lower().replace(' ', '_')}.csv", mime="text/csv")

st.caption("**Methodology:** Streets ranked by total rat complaints in the last 12 months. Color: Green = faster, Red = slower response.")

metadata = get_dataset_metadata()
update_text = metadata['last_updated'].strftime('%b %d, %Y') if metadata['last_updated'] else None
st.markdown(render_footer(update_text), unsafe_allow_html=True)
