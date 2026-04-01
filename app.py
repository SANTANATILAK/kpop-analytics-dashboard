import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from src.data_processing import load_data, calculate_re_entries_and_momentum, get_artist_summary
from datetime import datetime

st.set_page_config(page_title="Atlantic K-Pop Analytics", layout="wide", page_icon="📈")

st.markdown("""
<style>
    .metric-box {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px;
    }
    .metric-value {
        font-size: 2em;
        font-weight: bold;
        color: #1DB954;
    }
    .metric-title {
        color: #B3B3B3;
        font-size: 1.1em;
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 K-Pop Momentum & Re-entry Dashboard")
st.markdown("**Atlantic Recording Corporation** | Intelligence via Fandom Momentum Dynamics")


@st.cache_data
def load_and_process():
    filepath = os.path.join(os.path.dirname(__file__), 'data', 'playlist_history.csv')
    try:
        raw_df = load_data(filepath)
        momentum_df = calculate_re_entries_and_momentum(raw_df)
        artist_df = get_artist_summary(momentum_df)
        return raw_df, momentum_df, artist_df
    except Exception as e:
        return None, None, None

raw_df, momentum_df, artist_df = load_and_process()

if raw_df is None:
    st.error("Data not found. Please run `python src/generate_mock_data.py` first.")
    st.stop()


st.sidebar.header("Filter Configuration")


min_date = raw_df['date'].min().to_pydatetime()
max_date = raw_df['date'].max().to_pydatetime()
start_date, end_date = st.sidebar.slider("Date Range", min_value=min_date, max_value=max_date, value=(min_date, max_date))

all_artists = ["All"] + sorted(raw_df['artist'].unique().tolist())
selected_artist = st.sidebar.selectbox("Select Artist", all_artists)


album_types = ["All", "Single", "Album"]
selected_type = st.sidebar.selectbox("Album Type", album_types)


filtered_raw = raw_df[(raw_df['date'] >= start_date) & (raw_df['date'] <= end_date)]
filtered_momentum = momentum_df[(momentum_df['start_date'] >= start_date) & (momentum_df['end_date'] <= end_date)]

if selected_artist != "All":
    filtered_raw = filtered_raw[filtered_raw['artist'] == selected_artist]
    filtered_momentum = filtered_momentum[filtered_momentum['artist'] == selected_artist]

if selected_type != "All":
    filtered_raw = filtered_raw[filtered_raw['album_type'] == selected_type]
    filtered_momentum = filtered_momentum[filtered_momentum['album_type'] == selected_type]


col1, col2, col3, col4 = st.columns(4)
col1.markdown(f'<div class="metric-box"><div class="metric-value">{len(filtered_momentum)}</div><div class="metric-title">Total Chart Runs</div></div>', unsafe_allow_html=True)
re_entries = filtered_momentum[filtered_momentum['entry_type'] == 'Re-Entry']
col2.markdown(f'<div class="metric-box"><div class="metric-value">{len(re_entries)}</div><div class="metric-title">Total Re-Entries</div></div>', unsafe_allow_html=True)
avg_retention = filtered_momentum['retention_days'].mean()
col3.markdown(f'<div class="metric-box"><div class="metric-value">{avg_retention:.1f}</div><div class="metric-title">Avg Retention Days</div></div>', unsafe_allow_html=True)
max_fandom = filtered_momentum['fandom_proxy_score'].max() if not filtered_momentum.empty else 0
col4.markdown(f'<div class="metric-box"><div class="metric-value">{max_fandom:.1f}</div><div class="metric-title">Peak Fandom Score</div></div>', unsafe_allow_html=True)

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "Re-Entry & Timeline Visualizer", 
    "Momentum & Comeback Spikes", 
    "Content Strategy (Album vs Single)",
    "Fandom Intensity Leaderboard"
])

with tab1:
    st.subheader("Chart Position Timeline")
    st.write("Visualizes how specific tracks enter, exit, and resurge back into the Top 50.")
    
    if not filtered_raw.empty:
        fig1 = px.line(filtered_raw, x='date', y='position', color='song', line_group='artist',
                       hover_name='artist', render_mode='svg', 
                       title="Daily Chart Rank (Inverted y-axis)")
        fig1.update_yaxes(autorange="reversed") # Rank 1 at top
        fig1.update_layout(height=600)
        st.plotly_chart(fig1, use_container_width=True)
    
    st.subheader("Re-Entry Duration (Gantt)")
    if not filtered_momentum.empty:
        fig_gantt = px.timeline(filtered_momentum, x_start="start_date", x_end="end_date", y="song", 
                                color="entry_type", title="Lifespan of original entries vs comebacks")
        fig_gantt.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_gantt, use_container_width=True)

with tab2:
    st.subheader("Momentum Spike Analysis")
    st.write("Comparing the initial popularity vs the peak popularity achieved during a specific run.")
    
  
    fig_scatter = px.scatter(filtered_momentum, x="momentum_spike_score", y="retention_days", 
                             color="entry_type", size="fandom_proxy_score", hover_name="song",
                             hover_data=["artist", "best_rank_achieved"],
                             title="Momentum Surge vs Sustainability (Days retained)")
    st.plotly_chart(fig_scatter, use_container_width=True)
    
with tab3:
    st.subheader("Content Attribute vs Momentum Strategy")
    st.write("Does distributing a single vs full album yield a longer retention or higher comeback spike?")
    
    col_a, col_b = st.columns(2)

    with col_a:
        fig_box_retention = px.box(filtered_momentum, x="album_type", y="retention_days", 
                                   color="entry_type", points="all",
                                   title="Post-Comeback Retention: Single vs Album")
        st.plotly_chart(fig_box_retention, use_container_width=True)
        
    with col_b:
        fig_box_spike = px.box(filtered_momentum, x="album_type", y="momentum_spike_score", 
                               color="entry_type", points="all",
                               title="Comeback Intensity: Single vs Album")
        st.plotly_chart(fig_box_spike, use_container_width=True)
        
with tab4:
    st.subheader("Fandom Intensity Proxy Leaderboard")
    st.write("A composite score (0-100) aggregating high-retention days, sharp rank jump capacity, and frequency of re-entries.")
    
    st.dataframe(artist_df.style.background_gradient(cmap="Greens", subset=['fandom_proxy_score']),
                 use_container_width=True, hide_index=True)
