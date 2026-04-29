#!/bin/bash
# ──────────────────────────────────────────────────────────
# AUTOPILOT PONG — Run Game (Linux / macOS)
# ──────────────────────────────────────────────────────────

# Activate venv if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

cd src
python3 game.py
