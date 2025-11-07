@echo off
echo ==========================================
echo      Starting Neuro AI Assistant...
echo ==========================================

REM Activate virtual environment
IF EXIST venv (
    echo ✅ Virtual environment found.
) ELSE (
    echo 🔧 Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate

REM Install requirements if needed
echo ✅ Installing dependencies (if any changes)...
pip install -r requirements.txt >nul

REM Run the assistant
echo ✅ Launching Neuro...
python main.py

pause
