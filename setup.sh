#!/bin/bash
# Quick setup script for Zork Rewrite

echo "Setting up Zork Rewrite..."

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

echo "Setup complete! Run the game with:"
echo "  source .venv/bin/activate"
echo "  PYTHONPATH=. python main.py"