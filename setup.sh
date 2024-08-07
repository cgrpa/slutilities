#!/bin/bash
set -e

# Clone the Whisper CPP repository if it does not exist
if [ ! -d "apis/Audio/whisper_cpp" ]; then
    echo "Cloning Whisper CPP..."
    git clone https://github.com/ggerganov/whisper.cpp apis/Audio/whisper_cpp
fi

# Navigate to the cloned repository
cd apis/Audio/whisper_cpp

# Download the Whisper model
if [ ! -f "models/ggml-base.en.bin" ]; then
    echo "Downloading Whisper base.en model..."
    bash models/download-ggml-model.sh base.en
fi

# Build the main example
echo "Building the main example..."
make

# Check if the main executable is created
if [ ! -f "./main" ]; then
    echo "Error: The main executable was not created."
    exit 1
fi



cd ../../../

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Setup completed successfully. You can now run your Streamlit app with 'run_app.sh"