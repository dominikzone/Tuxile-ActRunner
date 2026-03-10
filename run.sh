#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Activate the virtual environment if it exists
if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
else
    echo "Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

echo "Starting Tuxile ActRunner..."

# Run the Python application in the background and get its PID
nohup python3 main.py > /dev/null 2>&1 &
APP_PID=$! # Get the PID of the last background command

echo "Tuxile ActRunner works perfect. Terminal will close with app or in 5 seconds."

# Monitor the application for up to 5 seconds
for i in {1..10}; do # Check 10 times, with 0.5s sleep = 5 seconds total
    if ! ps -p $APP_PID > /dev/null; then
        # Application has terminated, exit immediately
        exit 0
    fi
    sleep 0.5
done

# If 5 seconds passed and application is still running, exit
exit 0
