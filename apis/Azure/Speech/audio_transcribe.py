import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv()

class AudioTranscriber:
    def __init__(self, output_directory='data'):
        """
        Initialize the AudioTranscriber with Azure Speech SDK configurations.
        
        Parameters:
        output_directory (str): Directory to save the transcription output.
        """
        self.speech_key = os.getenv("AZURE_SPEECH_KEY")
        self.speech_region = os.getenv("AZURE_SPEECH_REGION")
        
        if not self.speech_key or not self.speech_region:
            raise ValueError("[ERROR] AZURE_SPEECH_KEY and AZURE_SPEECH_REGION environment variables must be set.")
        
        try:
            self.speech_config = speechsdk.SpeechConfig(subscription=self.speech_key, region=self.speech_region)
        except Exception as e:
            raise ValueError(f"[ERROR] Failed to initialize SpeechConfig: {e}")
        
        self.output_directory = output_directory
        self.ensure_output_directory()

    def ensure_output_directory(self):
        """
        Ensure that the output directory exists.
        """
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
            print(f'[INFO] Directory {self.output_directory} created.')
        else:
            print(f'[INFO] Directory {self.output_directory} already exists.')

    def transcribe_audio(self, audio_file_path):
        """
        Transcribe the given audio file and save the transcription to a file.
        
        Parameters:
        audio_file_path (str): Path to the audio file to be transcribed.
        """
        print(f'[INFO] Starting transcription for {audio_file_path}')
        audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
        recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config, audio_config=audio_config)

        transcription_output = []

        def recognized(evt):
            """
            Callback function for recognized speech.
            """
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                print(f'[DEBUG] RECOGNIZED: {evt.result.text}')
                transcription_output.append(evt.result.text)
            elif evt.result.reason == speechsdk.ResultReason.NoMatch:
                print(f'[DEBUG] No speech could be recognized: {evt.result.no_match_details}')

        def canceled(evt):
            print(f'[INFO] CANCELED: {evt}')
            if evt.result.reason == speechsdk.CancellationReason.Error:
                print(f'[ERROR] Error details: {evt.result.error_details}')

        recognizer.recognized.connect(recognized)
        recognizer.canceled.connect(canceled)

        recognizer.start_continuous_recognition()
        print(f'[INFO] Recognition started.')

        try:
            while True:
                pass
        except KeyboardInterrupt:
            recognizer.stop_continuous_recognition()
            print(f'[INFO] Recognition stopped.')

        transcription_file_path = os.path.join(self.output_directory, 'transcription.txt')
        with open(transcription_file_path, 'w') as file:
            file.write('\n'.join(transcription_output))

        print(f'[INFO] Transcription output saved to {transcription_file_path}')