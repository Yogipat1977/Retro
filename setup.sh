#!/bin/bash
# ──────────────────────────────────────────────────────────
# AUTOPILOT PONG — One-Command Setup (Linux / macOS)
# ──────────────────────────────────────────────────────────
set -e

echo "🎮 Setting up Autopilot Pong..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo "👉 Run the game with:  ./run.sh"
echo ""
