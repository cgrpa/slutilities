import subprocess
import os
from dotenv import load_dotenv

load_dotenv()

def convert_to_16kHz(audio_file_path):
    """
    Convert any audio or video file to a 16 kHz WAV file.
    
    Parameters:
    audio_file_path (str): Path to the audio or video file to be converted.
    
    Returns:
    str: Absolute path to the converted 16 kHz WAV file.
    """
    # Get the temporary path from the environment variable
    temp_path = os.getenv('TEMP_PATH', 'temp')
    
    # Ensure the temporary path exists
    os.makedirs(temp_path, exist_ok=True)
    
    # Define the path for the final 16 kHz WAV file
    base_name = os.path.splitext(os.path.basename(audio_file_path))[0]
    final_wav_path = os.path.join(temp_path, f"{base_name}_16kHz.wav")

    if os.path.exists(final_wav_path):
        os.remove(final_wav_path)
    
    # Convert the input file to a 16 kHz WAV fi
    # le using ffmpeg
    command = ["ffmpeg", "-i", audio_file_path, "-ar", "16000", final_wav_path]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error converting to 16 kHz: {e}")
        raise
    
    # Return the absolute path to the converted file
    return os.path.abspath(final_wav_path)