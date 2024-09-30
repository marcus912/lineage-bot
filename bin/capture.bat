@ECHO OFF

echo Check Python venv
if not exist "venv" (
    echo folder not exists
    python -m venv venv
)

echo install required python libs
.\venv\Scripts\activate && pip install -r requirements.txt && python lin_window_capture\capture-screen.py

pause