import sys
import io

class MultiStream:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, message):
        for stream in self.streams:
            stream.write(message)
            stream.flush()  # Ensure message is written immediately

    def flush(self):
        for stream in self.streams:
            stream.flush()

def redirect_stdout_and_stderr(output_buffer):
    multi_stream = MultiStream(sys.stdout, output_buffer)
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    sys.stdout = multi_stream
    sys.stderr = multi_stream
    return original_stdout, original_stderr, multi_stream