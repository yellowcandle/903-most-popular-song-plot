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
究竟叱咤 903 我最喜愛歌曲票數與 YouTube MV 觀看次數有沒有關係？  
近年的叱咤 903 頒獎典禮的我最喜愛歌曲現場投票，都會有人問「究竟場內投票有無代表性？」  
畢竟叱咤頒獎典禮的門票有限，亦非常難取得。  
我們可以將2024年度的我最喜愛歌曲五強的現場票數，與它們在 YouTube 的受歡迎程度作比較。  
為了避免 YouTube 的觀看次數受歌曲發佈的日期先後次序影響，我們會將觀看次數標準化，以每日觀看次數作比較。  
然後，我們將**每日觀看次數最高的歌曲，設定為基準**，其他歌曲的觀看次數和叱咤頒獎禮的票數，都會與基準作比較。  
如果叱咤 903 我最喜愛歌曲的場內投票有代表性，那麼我們應該會看到票數較高的歌曲，在 YouTube 的觀看次數亦較高。  

最理想嘅情況當然就係將幾個主要串流平台嘅數據都搜集埋，然後再作比較。  
但係由於我哋冇足夠嘅資源，所以暫時只可以做到 YouTube 嘅數據。
另外，播放 MV 同聽歌嘅行為，未必完全等同，所以呢個分析只可以作為參考，唔可以完全代表叱咤 903 我最喜愛歌曲嘅場內投票有冇代表性。
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
