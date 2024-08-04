import streamlit as st
import yt_dlp
import threading
import sys
import io
import time
import os
from pathlib import Path
from .logging_utils import MultiStream, redirect_stdout_and_stderr

# Function to get list of videos from a YouTube playlist
def get_playlist_videos(url):
    ydl_opts = {
        'extract_flat': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            playlist_title = info_dict.get('title', 'playlist')
            videos = [entry['title'] for entry in info_dict['entries']]
            return playlist_title, videos
    except yt_dlp.utils.DownloadError:
        raise Exception("Invalid YouTube Playlist URL or playlist is unavailable.")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}")

# Function to get the default downloads folder
def get_default_download_path():
    if os.name == 'nt':  # Windows
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders') as key:
                downloads_path = winreg.QueryValueEx(key, '{374DE290-123F-4565-9164-39C4925E467B}')[0]
        except Exception:
            downloads_path = str(Path.home() / 'Downloads')
    else:  # macOS, Linux
        downloads_path = str(Path.home() / 'Downloads')
    return downloads_path

# Page code for getting playlist videos
def show_playlist_page():
    st.subheader("Get List of Videos from Playlist")
    
    with st.container():
        st.write("**YouTube Playlist URL**")
        url = st.text_input("Enter YouTube Playlist URL", 'https://www.youtube.com/watch?v=gSlLFx2U4qo&list=RDznzkbw4c4dQ')
    
    with st.container():
        st.write("**Output Location**")
        col1, col2 = st.columns([3, 1])
        with col1:
            output_path = st.text_input("Enter output folder path", key="output_path", value=get_default_download_path())
        with col2:
            save_to_file = st.checkbox("Save to txt file?")

    log_area = st.empty()
    output_buffer = io.StringIO()

    if st.button("Get Videos"):
        if not url:
            st.error("Please enter a valid YouTube Playlist URL.")
            return
        if not output_path:
            output_path = get_default_download_path()
        
        original_stdout, original_stderr, multi_stream = redirect_stdout_and_stderr(output_buffer)

        def run_get_videos():
            try:
                print("Log")
                playlist_title, videos = get_playlist_videos(url)
                for video in videos:
                    print(video)
                if save_to_file:
                    save_videos_to_file(playlist_title, videos, output_path)
                print("Operation finished.")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

        def save_videos_to_file(playlist_title, videos, output_path):
            try:
                # Sanitize the playlist title to create a valid filename
                sanitized_title = "".join([c if c.isalnum() else "_" for c in playlist_title])
                file_path = os.path.join(output_path, f"{sanitized_title}_playlist_videos.txt")
                with open(file_path, 'w') as f:
                    for video in videos:
                        f.write(f"{video}\n")
                print(f"Saved to {file_path}")
            except Exception as e:
                print(f"Failed to save file: {e}")

        get_videos_thread = threading.Thread(target=run_get_videos)
        get_videos_thread.start()

        while get_videos_thread.is_alive():
            log_area.text(output_buffer.getvalue())
            time.sleep(1)  # Wait a little before checking for new messages

        log_area.text(output_buffer.getvalue())

        # Restore stdout and stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr

# Main app
def main():
    st.title("YouTube Utility Functions")
    
    menu = ["Get List of Videos from Playlist"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    if choice == "Get List of Videos from Playlist":
        show_playlist_page()

if __name__ == "__main__":
    main()