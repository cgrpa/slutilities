import os
import subprocess
import logging
import re
from dotenv import load_dotenv
from apis.Audio.ffmpeg_wrapper import convert_to_16kHz

load_dotenv()

# Configure logging settings
def configure_logging(log_level=logging.DEBUG):
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')

class WhisperTranscriber:
    def __init__(self, output_directory='/data', log_level=logging.DEBUG):
        self.output_directory = output_directory
        configure_logging(log_level)
        self.ensure_output_directory()
    
    def ensure_output_directory(self):
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
            logging.info(f'Directory {self.output_directory} created.')
        else:
            logging.info(f'Directory {self.output_directory} already exists.')
    
    def __process_audio(self, wav_file, model_name="base.en"):
        model = f"./models/ggml-{model_name}.bin"

        if not os.path.exists(model):
            raise FileNotFoundError(f"Model file not found: {model}")

        if not os.path.exists(wav_file):
            raise FileNotFoundError(f"WAV file not found: {wav_file}")

        full_command = ["./main", "-f", wav_file]

        process = subprocess.Popen(full_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        logging.debug(f"Raw output: {output.decode('utf-8')}")
        logging.debug(f"Raw error: {error.decode('utf-8')}")

        if error and not output:
            raise Exception(f"Error processing audio: {error.decode('utf-8')}")

        decoded_str = output.decode('utf-8').strip()
        processed_str = decoded_str.replace('[BLANK_AUDIO]', '').strip()

        metadata = self.__extract_timing_metadata(error.decode('utf-8'))
        
        return processed_str, metadata

    def __extract_timing_metadata(self, console_output):
        patterns = {
            'load_time': r'whisper_print_timings:\s+load time =\s+(\d+\.\d+) ms',
            'mel_time': r'whisper_print_timings:\s+mel time =\s+(\d+\.\d+) ms',
            'sample_time': r'whisper_print_timings:\s+sample time =\s+(\d+\.\d+) ms',
            'encode_time': r'whisper_print_timings:\s+encode time =\s+(\d+\.\d+) ms',
            'decode_time': r'whisper_print_timings:\s+decode time =\s+(\d+\.\d+) ms',
            'batchd_time': r'whisper_print_timings:\s+batchd time =\s+(\d+\.\d+) ms',
            'prompt_time': r'whisper_print_timings:\s+prompt time =\s+(\d+\.\d+) ms',
            'total_time': r'whisper_print_timings:\s+total time =\s+(\d+\.\d+) ms'
        }

        timing_metadata = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, console_output)
            if match:
                timing_metadata[key] = float(match.group(1))
            else:
                timing_metadata[key] = None

        return timing_metadata

    def transcribe_audio(self, audio_file_path):
        logging.info(f'Converting audio to 16 KHz for {audio_file_path}')
        converted_audio_path = convert_to_16kHz(audio_file_path)
        
        logging.info(f'Transcribing audio file {converted_audio_path}')
        
        original_cwd = os.getcwd()
        whisper_cpp_dir = os.path.join(original_cwd, 'apis/Audio/whisper_cpp')
        os.chdir(whisper_cpp_dir)
        
        try:
            output_transcription, metadata = self.__process_audio(converted_audio_path)
        except Exception as e:
            logging.error(f"Error during transcription: {e}")
            raise e
        finally:
            os.chdir(original_cwd)

        logging.info(f"Completed transcription for {converted_audio_path}")
        logging.debug(output_transcription)
        logging.debug(f"Metadata: {metadata}")
        return output_transcription, metadata
    
# if __name__ == "__main__":
#     # Example usage
#     transcriber = WhisperTranscriber(output_directory='./data', log_level=logging.DEBUG)
#     transcriber.transcribe_audio("/Users/che/Downloads/Faith Evans - Ain't Nobody (1996).mp4")