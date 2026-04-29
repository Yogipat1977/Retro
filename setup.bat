@echo off
REM ──────────────────────────────────────────────────────────
REM AUTOPILOT PONG — One-Command Setup (Windows)
REM ──────────────────────────────────────────────────────────

echo Setting up Autopilot Pong...

python -m venv venv
call venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Setup complete!
echo Run the game with:  run.bat
echo.
pause
