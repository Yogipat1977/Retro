@echo off
REM ──────────────────────────────────────────────────────────
REM AUTOPILOT PONG — Run Game (Windows)
REM ──────────────────────────────────────────────────────────

if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate
)

cd src
python game.py
