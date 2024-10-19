import yt_dlp
import json
from tabulate import tabulate
import os
import traceback

# Save video info & formats
def save_info_to_json(info_dict, output_folder):
    video_id = info_dict.get('id', 'unknown_id')
    file_path = os.path.join(output_folder, f"{video_id}.json")

    
    with open(file_path, 'w') as json_file:
        json.dump(info_dict, json_file, indent=4)
    
    print(f"Information saved to {file_path}")


def get_video_metadata(url):
    metadata = get_info_youtube_video(url)
    
    if not metadata:
        raise Exception('Metadata is null')
    
    thumbnail = [thumbnail for thumbnail in metadata[0]['thumbnails'] if thumbnail['preference'] == 0]
    thumbnail_url = thumbnail[0]['url']
    title = metadata[0]['title']
    length = str(timedelta(seconds=metadata[0]['duration']))
    
    return thumbnail_url, title, length

# Get Video Info
def get_info_youtube_video(url):
    ydl_opts = {
        'verbose': True,
        'noplaylist': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        formats = ydl.list_formats(info_dict)


        return info_dict, formats

# Function to download a YouTube video with retries
def download_youtube_video(url, audio_only, output_path):
    try:
        ydl_opts = {
            'format': 'bestaudio' if audio_only else 'bestvideo+bestaudio',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'retries': 5,  # Retry up to 5 times
            'verbose': True,
            'socket_timeout': 10,  # Increase socket timeout
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'  # Convert to mp4 after download
            }]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            save_info_to_json(info_dict, 'log_dumps')
            ydl.download([url])
    except Exception as e:
        print(f'Exception: {e}')
        print(traceback.format_exc())
        raise e