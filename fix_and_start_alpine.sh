#!/bin/bash

# Fix PATH to include user's local bin directory
export PATH="/home/ubuntu/.local/bin:$PATH"

# Also add Python user site-packages to PYTHONPATH
export PYTHONPATH="/home/ubuntu/.local/lib/python3.13/site-packages:$PYTHONPATH"

echo "🔧 Fixed PATH and PYTHONPATH"
echo "📦 Starting Alpine Bot..."

# Start the Alpine bot
python3 start_alpine_bot.py