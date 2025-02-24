#!/bin/bash

# Check if venv already exists
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Skipping creation."
else
    echo "Creating virtual environment..."
    python -m venv venv
fi


# echo "Activating virtual environment..."
# source venv/Scripts/activate  
# echo "Virtual environment activated."


echo "Installing dependencies..."
pip install -r requirements.txt


