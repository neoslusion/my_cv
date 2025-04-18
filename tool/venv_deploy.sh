#!/bin/bash

# Define the directory for the virtual environment at the root
VENV_DIR="../venv"

# Check if the virtual environment directory already exists
if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists. Activating..."
else
    # Create the virtual environment
    echo "Creating virtual environment..."
    python -m venv $VENV_DIR
fi

# Activate the virtual environment
source $VENV_DIR/bin/activate

# Check if requirements.txt exists and install dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    python -m pip install -r requirements.txt
else
    echo "requirements.txt not found. Skipping dependency installation."e
fi

echo "Virtual environment setup complete."
