import streamlit as st
import os
import threading
import io
import time
from pathlib import Path
from .logging_utils import redirect_stdout_and_stderr
from apis.Audio.whisper_cpp_wrapper import WhisperTranscriber
from apis.YouTube.yt_dlp import download_youtube_video, get_video_metadata
import sys

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

def show_transcription_page():
    st.subheader("Transcription Options")
    
    with st.container():
        st.write("**YouTube Video URL**")
        url = st.text_input("Enter YouTube Video URL (or leave empty for local file):", '')
        
        if url:
            thumbnail_url, title, length = get_video_metadata(url)
            
            with st.container():
                st.image(image=url)
                st.write(title + '\n')
                st.write(length)
        
    with st.container():
        st.write("**Local Video/Audio File**")
        local_file = st.file_uploader("Upload Video/Audio file", type=['mp3', 'wav', 'm4a', 'mp4'], )

    with st.container():
        st.write("**Output Location**")
        output_path = st.text_input("Enter output folder path", value=get_default_download_path())

    transcription_type = st.radio("Select Transcription Type:", options=["Local Transcription", "Azure Transcription"], index=0)

    log_area = st.empty()
    output_buffer = io.StringIO()

    if st.button("Transcribe"): 
        if url == '' and local_file is None:
            st.error("Please enter a valid YouTube URL or upload a local audio file.")
            return
        if not output_path:
            output_path = get_default_download_path()
        
        original_stdout, original_stderr, multi_stream = redirect_stdout_and_stderr(output_buffer)

        def run_transcription():
            try:
                if url:
                    audio_file = download_youtube_audio(url, output_path)
                else:
                    audio_file_path = os.path.join(output_path, local_file.name)
                    with open(audio_file_path, 'wb') as f:
                        f.write(local_file.getbuffer())
                    audio_file = audio_file_path

                if transcription_type == "Local Transcription":
                    transcriber = WhisperTranscriber(output_directory=output_path)
                    result, metadata = transcriber.transcribe_audio(audio_file)
                elif transcription_type == "Azure Transcription":
                    result = "Azure transcription is not yet implemented."
                    metadata = {}

                # Save the transcription result to a file
                transcription_file_path = os.path.join(output_path, f"{Path(audio_file).stem}_transcription.txt")
                with open(transcription_file_path, 'w') as f:
                    f.write(f"Transcription Result:\n{result}\n\nMetadata:\n{metadata}\n")

                output_buffer.write(f"Transcription saved to {transcription_file_path}\n")
            except Exception as e:
                output_buffer.write(f"An unexpected error occurred: {e}\n")

        transcription_thread = threading.Thread(target=run_transcription)
        transcription_thread.start()

        while transcription_thread.is_alive():
            log_area.text(output_buffer.getvalue())
            time.sleep(1)

        log_area.text(output_buffer.getvalue())
        
        sys.stdout = original_stdout
        sys.stderr = original_stderr

def download_youtube_audio(url, output_path):
    download_youtube_video(url, audio_only=True, output_path=output_path)
    audio_file_path = os.path.join(output_path, f'{url.split("=")[-1]}.mp3')
    return audio_file_path