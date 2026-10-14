@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe py -3 -m venv .venv
if errorlevel 1 goto failure
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto failure
echo Start Ollama and run: ollama pull qwen2.5:3b
.venv\Scripts\python.exe app.py --mode local
pause
exit /b
:failure
echo Setup failed. Install Python 3.11 or 3.12 and try again.
pause
