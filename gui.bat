@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  py -3 -m venv .venv
)
.venv\Scripts\python -m pip install -q -r requirements.txt -r requirements-gui.txt
.venv\Scripts\streamlit run odwolania2json/gui.py %*
