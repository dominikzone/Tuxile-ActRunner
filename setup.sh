#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Checking for Python and pip installation..."
if ! command -v python3 &> /dev/null
then
    echo "Python 3 is not installed. Please install Python 3.8+."
    exit 1
fi

if ! command -v pip3 &> /dev/null
then
    echo "pip 3 is not installed. Please install pip for Python 3."
    exit 1
fi

echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Setup complete! You can now run the application using: ./run.sh"
