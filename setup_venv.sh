#!/bin/bash
echo "Creating virtual environment for Cost Calculation System..."
echo

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

echo
echo "Virtual environment created successfully!"
echo
echo "To activate the virtual environment, run:"
echo "source .venv/bin/activate"
echo
echo "To run the application, use:"
echo "python app.py"
echo
