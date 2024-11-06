#!/bin/bash

# Set the name of your virtual environment
VENV_NAME="venv"

# Create a virtual environment if it doesn't already exist
if [ ! -d "$VENV_NAME" ]; then
    echo "Creating virtual environment..."
    python -m venv "$VENV_NAME"
else
    echo "Virtual environment already exists."
fi

python.exe -m pip install --upgrade pip

# Determine the OS and activate the virtual environment accordingly
echo "Activating virtual environment..."

# Check if the system is running on Windows
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    # Activate for Windows
    source "$VENV_NAME/Scripts/activate"
else
    # Activate for Unix-based systems
    source "$VENV_NAME/bin/activate"
fi

# Check if requirements.txt exists and install the dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing requirements from requirements.txt..."
    pip install -r requirements.txt
else
    echo "No requirements.txt file found. Skipping installation."
fi

echo "Virtual environment setup complete and activated."
