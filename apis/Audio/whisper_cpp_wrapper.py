from dotenv import load_dotenv
import os
import subprocess
from ffmpeg_wrapper import convert_to_16kHz

load_dotenv()

class WhisperTranscriber:
    def __init__(self, output_directory='/data'):
        """
        Initialize the WhisperTranscriber
        
        Parameters:
        output_directory (str): Directory to save the transcription output.
        """
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
    
    def __process_audio(self, wav_file, model_name="base.en"):
        """
        Processes an audio file using a specified model and returns the processed string.

        :param wav_file: Path to the WAV file
        :param model_name: Name of the model to use
        :return: Processed string output from the audio processing
        :raises: Exception if an error occurs during processing
        """

        model = f"./models/ggml-{model_name}.bin"

        # Check if the file exists
        if not os.path.exists(model):
            raise FileNotFoundError(f"Model file not found: {model} \n\nDownload a model with this command:\n\n> bash ./models/download-ggml-model.sh {model_name}\n\n")

        if not os.path.exists(wav_file):
            raise FileNotFoundError(f"WAV file not found: {wav_file}")

        # Use a list to pass the command and its arguments
        full_command = ["./main", "-f", wav_file]

        # Execute the command 
        process = subprocess.Popen(full_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Get the output and error (if any)
        output, error = process.communicate()

        # Print raw output for debugging
        print(f"Raw output: {output.decode('utf-8')}")
        print(f"Raw error: {error.decode('utf-8')}")

        if error and not output:
            raise Exception(f"Error processing audio: {error.decode('utf-8')}")

        # Process and return the output string
        decoded_str = output.decode('utf-8').strip()
        processed_str = decoded_str.replace('[BLANK_AUDIO]', '').strip()

        return processed_str

    def transcribe_audio(self, audio_file_path):
        """
        Transcribe the given audio file and save the transcription to a file.
        This wrapper will convert the audio into 16 KHz if not already.
        
        Parameters:
        audio_file_path (str): Path to the audio file to be transcribed.
        """

        print(f'[INFO] Converting audio to 16 KHz for {audio_file_path}')
        converted_audio_path = convert_to_16kHz(audio_file_path)
        
        print(f'[INFO] Transcribing audio file {converted_audio_path}')
        
        # Save the current working directory
        original_cwd = os.getcwd()
        
        # Change to the directory where the whisper_cpp models are located
        whisper_cpp_dir = os.path.join(original_cwd, 'apis/Audio/whisper_cpp')
        os.chdir(whisper_cpp_dir)
        
        try:
            output_transcription = self.__process_audio(converted_audio_path)
        except Exception as e:
            print(f"Error during transcription: {e}")
            raise e
        finally:
            # Restore the original working directory
            os.chdir(original_cwd)

        print(output_transcription)
        return output_transcription


if __name__ == "__main__":
    # Example usage
    transcriber = WhisperTranscriber(output_directory='./data')
    transcriber.transcribe_audio("/Users/che/Downloads/Faith Evans - Ain't Nobody (1996).mp4")