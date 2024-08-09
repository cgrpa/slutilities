import streamlit as st
from pages.download_video import show_download_page
from pages.get_playlist_videos import show_playlist_page
from pages.get_video_metadata import show_metadata_page
from pages.transcription_page import show_transcription_page  # Import the new page

# Main app
def main():
    st.title("YouTube Utility Functions")

    menu = ["Home", "Download YouTube Video", "Get Playlist Videos", "Get Video Metadata", "Transcription"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("Welcome to YouTube Utility Functions App")
    elif choice == "Download YouTube Video":
        show_download_page()
    elif choice == "Get Playlist Videos":
        show_playlist_page()
    elif choice == "Get Video Metadata":
        show_metadata_page()
    elif choice == "Transcription":
        show_transcription_page()  # Add the transcription page

if __name__ == '__main__':
    main()