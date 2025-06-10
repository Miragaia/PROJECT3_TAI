#!/bin/bash

# Script to automatically run the Python noise addition script with intensity-based method
# This script will choose option 2 (intensity-based) automatically

echo "=========================================="
echo "SoX Audio Noise Addition - Intensity Mode"
echo "=========================================="
echo ""

# Check if the Python script exists
PYTHON_SCRIPT="noise_generator.py"

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: Python script '$PYTHON_SCRIPT' not found!"
    echo "Please make sure the Python script is in the same directory as this bash script."
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "Error: Python is not installed or not in PATH"
    echo "Please install Python 3 to run this script."
    exit 1
fi

# Determine which Python command to use
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

echo "Using Python command: $PYTHON_CMD"
echo "Running intensity-based noise addition..."
echo ""

# Run the Python script and automatically choose option 2
echo "2" | $PYTHON_CMD "$PYTHON_SCRIPT"

# Check the exit status
if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Script completed successfully!"
    echo "Check the 'test_files' directory for output files."
else
    echo ""
    echo "✗ Script encountered an error."
    exit 1
fi