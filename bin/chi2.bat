@ECHO OFF

SET VAR_NAME=%LIN_BOT_PATH%

IF "%VAR_NAME%"=="" (
    echo Environment variableLIN_BOT_PATH is not set.
    exit /b 1
) ELSE (
    echo Environment variable LIN_BOT_PATH is set to %VAR_NAME%.
)

cd %LIN_BOT_PATH%
echo Check Python venv
if not exist ".venv" (
    echo folder not exists, create venv
    python -m venv .venv
)

echo install required python libs
.\.venv\Scripts\activate && pip install -r requirements.txt && python scripts\run_chi2.py

pause
