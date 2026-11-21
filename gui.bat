@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo Tworzenie srodowiska Python...
  py -3 -m venv .venv
)
if not exist .venv\Scripts\streamlit.exe (
  echo Instalacja bibliotek GUI - pierwsze uruchomienie moze potrwac ok. 1 minuty...
  .venv\Scripts\python -m pip install -r requirements.txt -r requirements-gui.txt
)
if not exist "%USERPROFILE%\.streamlit\credentials.toml" (
  mkdir "%USERPROFILE%\.streamlit" 2>nul
  (echo [general]& echo email = "") > "%USERPROFILE%\.streamlit\credentials.toml"
)
echo Uruchamianie interfejsu Odwolania2JSON w przegladarce...
.venv\Scripts\streamlit run odwolania2json/gui.py --browser.gatherUsageStats false %*
