import streamlit as st
import pandas as pd
from datetime import datetime
from youtube_data import get_video_stats, write_to_csv
from plot import create_dual_axis_plot

# Cache the YouTube data fetching to avoid repeated API calls
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_cached_video_stats(video_id):
    return get_video_stats(video_id)

# Streamlit app
st.set_page_config(page_title="YouTube Music Popularity", layout="wide")

# Title and description
st.title("叱咤 903 我最喜愛歌曲票數比例 與 YouTube MV 觀看次數比例")
st.markdown("""
This app compares the popularity of songs based on:
- **903 Most Popular Song Votes**: Total votes from listeners
- **YouTube Views**: Daily view counts of official music videos
""")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('data.csv')
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# Update YouTube stats
if st.button('Update YouTube Statistics'):
    with st.spinner('Fetching latest YouTube data...'):
        video_ids = df[df['youtube_id'].notna()]['youtube_id']
        progress_bar = st.progress(0)
        
        for i, video_id in enumerate(video_ids):
            title, views, date = get_cached_video_stats(video_id)
            if views and date:
                write_to_csv(video_id, title, views, date)
            progress_bar.progress((i + 1) / len(video_ids))
        
        st.success('YouTube statistics updated successfully!')
        st.rerun()

# Filter for 2024 songs
df = df[df['Year'] == 2024]

# Create and display the plot
st.subheader("Popularity Comparison")
fig = create_dual_axis_plot(df, output_path=None)
st.plotly_chart(fig, use_container_width=True)

# Show raw data
if st.checkbox('Show raw data'):
    st.subheader("Raw Data")
    st.dataframe(df)
