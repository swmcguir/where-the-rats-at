"""Ward Rankings page - Full leaderboard of response times."""

import streamlit as st
import pandas as pd
import plotly.express as px
from data.fetch import fetch_rodent_complaints, fetch_aldermen
from utils.metrics import calculate_ward_metrics, calculate_ward_grades
from utils.styles import get_base_styles, render_page_header, render_footer, get_grade_color

st.set_page_config(
    page_title="Ward Rankings | Where the Rats At?",
    page_icon="data/jpeg/Party Rat.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(get_base_styles(), unsafe_allow_html=True)

st.markdown(render_page_header(
    title="Ward Response Time Rankings",
    subtitle="All 50 wards ranked by how fast they respond to rat complaints"
), unsafe_allow_html=True)

with st.spinner("Loading data..."):
    df = fetch_rodent_complaints(days_back=365)
    aldermen = fetch_aldermen()

if df.empty:
    st.error("No data available.")
    st.stop()

ward_metrics = calculate_ward_metrics(df)
ward_metrics = calculate_ward_grades(ward_metrics)
ward_metrics = ward_metrics.merge(aldermen[['ward', 'alderman']], on='ward', how='left')

# Bar chart header
st.markdown('<p style="font-size:0.875rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin:1rem 0 0.75rem 0;background:#0a0a0a;color:#fafafa;padding:0.875rem 1.25rem;">Median Response Time by Ward</p>', unsafe_allow_html=True)

grade_order_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'F': 4}
ward_metrics['grade_order'] = ward_metrics['grade'].map(grade_order_map)
ward_metrics_sorted = ward_metrics.sort_values(['grade_order', 'median_response'], ascending=[True, True])

fig = px.bar(
    ward_metrics_sorted,
    x='median_response',
    y='ward',
    orientation='h',
    color='grade',
    color_discrete_map={'A': '#10b981', 'B': '#84cc16', 'C': '#f59e0b', 'D': '#f97316', 'F': '#ef4444'},
    category_orders={'grade': ['A', 'B', 'C', 'D', 'F']},
    hover_data=['alderman', 'total_complaints', 'completion_rate'],
    labels={'median_response': 'Median Response (Days)', 'ward': 'Ward', 'grade': 'Grade', 'alderman': 'Alderman', 'total_complaints': 'Total Complaints', 'completion_rate': 'Completion Rate %'}
)

ward_order = ward_metrics_sorted['ward'].astype(str).tolist()[::-1]

fig.update_layout(
    height=1200,
    yaxis={'categoryorder': 'array', 'categoryarray': ward_order, 'dtick': 1, 'title': None, 'tickfont': {'family': 'Space Mono, monospace', 'size': 11}},
    xaxis={'title': {'text': 'Median Response (Days)', 'font': {'family': 'Space Grotesk, sans-serif', 'size': 12}}, 'tickfont': {'family': 'Space Mono, monospace', 'size': 11}, 'gridcolor': '#e5e5e5', 'gridwidth': 1},
    showlegend=True,
    legend={'title': {'text': 'Grade', 'font': {'family': 'Space Grotesk, sans-serif', 'size': 12}}, 'font': {'family': 'Space Mono, monospace', 'size': 11}, 'orientation': 'h', 'yanchor': 'bottom', 'y': 1.02, 'xanchor': 'center', 'x': 0.5},
    font_family="Space Mono, monospace",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin={'l': 60, 'r': 20, 't': 60, 'b': 40}
)
fig.update_traces(marker_line_width=0, opacity=0.9, hovertemplate='<b>Ward %{y}</b><br>Response: %{x:.1f} days<br>Alderman: %{customdata[0]}<br>Complaints: %{customdata[1]:,}<extra></extra>')

st.plotly_chart(fig, use_container_width=True)

# Data table header
st.markdown('<p style="font-size:0.875rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin:1.5rem 0 0.75rem 0;background:#0a0a0a;color:#fafafa;padding:0.875rem 1.25rem;">Full Rankings Table</p>', unsafe_allow_html=True)

display_table = ward_metrics[['rank', 'ward', 'alderman', 'median_response', 'mean_response', 'p90_response', 'total_complaints', 'completion_rate', 'grade']].copy()
display_table.columns = ['Rank', 'Ward', 'Alderman', 'Median (days)', 'Mean (days)', 'P90 (days)', 'Complaints', 'Completion %', 'Grade']
display_table['Median (days)'] = display_table['Median (days)'].round(1)
display_table['Mean (days)'] = display_table['Mean (days)'].round(1)
display_table['P90 (days)'] = display_table['P90 (days)'].round(1)
display_table['Ward'] = display_table['Ward'].astype(int)

st.dataframe(
    display_table,
    hide_index=True,
    use_container_width=True,
    column_config={
        'Rank': st.column_config.NumberColumn('Rank', format='%d', width='small'),
        'Ward': st.column_config.NumberColumn('Ward', format='%d', width='small'),
        'Median (days)': st.column_config.NumberColumn('Median', format='%.1f'),
        'Mean (days)': st.column_config.NumberColumn('Mean', format='%.1f'),
        'P90 (days)': st.column_config.NumberColumn('P90', format='%.1f'),
        'Completion %': st.column_config.NumberColumn('Completion', format='%.1f%%'),
        'Grade': st.column_config.TextColumn('Grade', width='small')
    }
)

csv = display_table.to_csv(index=False)
st.download_button(label="Download CSV", data=csv, file_name="chicago_rat_response_rankings.csv", mime="text/csv")

# Grade distribution - compact HTML
grade_order = ['A', 'B', 'C', 'D', 'F']
grade_counts = ward_metrics['grade'].value_counts().reindex(grade_order, fill_value=0)

grade_bars = ""
for grade in grade_order:
    count = grade_counts.get(grade, 0)
    color = get_grade_color(grade)
    bar_width = (count / 50) * 100
    grade_bars += f'<div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.5rem;"><span style="width:1.5rem;height:1.5rem;background:{color};color:white;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:0.75rem;border-radius:2px;">{grade}</span><div style="flex:1;background:#e5e5e5;height:6px;border-radius:3px;"><div style="width:{bar_width}%;background:{color};height:100%;border-radius:3px;"></div></div><span style="font-weight:600;min-width:2rem;text-align:right;">{count}</span></div>'

st.markdown(f'<div class="card"><div class="card-header">Grade Distribution</div><div class="card-body">{grade_bars}</div></div>', unsafe_allow_html=True)

st.caption("**Methodology:** Multi-factor grading: Speed (30%), Workload (25%), Worst-case (20%), Consistency (15%), Completion (10%).")

st.markdown(render_footer(), unsafe_allow_html=True)
