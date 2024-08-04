import streamlit as st
import yt_dlp

# Function to get metadata of a YouTube video
def get_video_metadata(url):
    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            metadata = {
                "Title": info_dict['title'],
                "Views": info_dict['view_count'],
                "Duration": info_dict['duration'],
                "Rating": info_dict.get('average_rating', 'N/A')
            }
            return metadata
    except yt_dlp.utils.DownloadError:
        st.error("Invalid YouTube URL or video is unavailable.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return {}

# Page code for getting video metadata
def show_metadata_page():
    st.subheader("Get Video Metadata")
    url = st.text_input("Enter YouTube Video URL")
    if st.button("Get Metadata"):
        metadata = get_video_metadata(url)
        for key, value in metadata.items():
            st.write(f"{key}: {value}")