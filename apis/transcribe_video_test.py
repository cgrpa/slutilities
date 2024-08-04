from transcribe_video import MeetingMinutesGenerator
from dotenv import load_dotenv
import os

load_dotenv()
# Example usage
api_key = os.getenv('OPENAI_KEY')
audio_file_path = "data/AMA #3_ Adaptogens, Fasting & Fertility, Bluetooth_EMF Risks, Cognitive Load Limits & More - Andrew Huberman.mp3"
generator = MeetingMinutesGenerator(api_key)

transcription = generator.transcribe_audio(audio_file_path)
minutes = generator.generate_meeting_minutes(transcription)
print(minutes)
generator.save_as_docx(minutes, 'meeting_minutes.docx')