import streamlit as st
import yt_dlp
import os
import threading
import logging
from pathlib import Path
import sys
import io
import time
from .logging_utils import MultiStream, redirect_stdout_and_stderr

# Function to download a YouTube video with retries
def download_youtube_video(url, output_path):
    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'retries': 5,  # Retry up to 5 times
        'verbose': True,
        'socket_timeout': 10,  # Increase socket timeout
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

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

# Page code for downloading YouTube video
def show_download_page():
    st.subheader("Download YouTube Video")
    
    with st.container():
        st.write("**YouTube Video URL**")
        
        url = st.text_input("Enter YouTube Video URL", 'https://www.youtube.com/watch?v=G6yC4KXGixE')
    
    with st.container():
        st.write("**Output Location**")
        col1, col2 = st.columns([3, 1])
        with col1:
            output_path = st.text_input("Enter output folder path", key="output_path", value=get_default_download_path())

    log_area = st.empty()
    output_buffer = io.StringIO()

    if st.button("Download"):
        if not url:
            st.error("Please enter a valid YouTube URL.")
            return
        if not output_path:
            output_path = get_default_download_path()
        
        original_stdout, original_stderr, multi_stream = redirect_stdout_and_stderr(output_buffer)

        def run_download():
            try:
                print("Log")
                download_youtube_video(url, output_path)
                print("Download finished.")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                print(f"Sometimes the library fails on certain videos, not sure why, sorry!")

        download_thread = threading.Thread(target=run_download)
        download_thread.start()

        while download_thread.is_alive():
            log_area.text(output_buffer.getvalue())
            time.sleep(1)  # Wait a little before checking for new messages

        log_area.text(output_buffer.getvalue())

        # Restore stdout and stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr

# Main app
def main():
    st.title("YouTube Utility Functions")
    
    menu = ["Download YouTube Video"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    if choice == "Download YouTube Video":
        show_download_page()

if __name__ == "__main__":
    main()