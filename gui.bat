@echo off
cd /d "%~dp0"
echo === Odwolania2JSON - GUI ===
if not exist .venv\Scripts\python.exe (
  echo [1/3] Tworzenie srodowiska wirtualnego Python (.venv)...
  py -3 -m venv .venv
) else (
  echo [1/3] Srodowisko Python (.venv) gotowe.
)
if not exist .venv\Scripts\streamlit.exe (
  echo [2/3] Instalacja bibliotek GUI (pierwsze uruchomienie - prosze czekac)...
  .venv\Scripts\python -m pip install -r requirements.txt -r requirements-gui.txt
) else (
  echo [2/3] Biblioteki GUI zainstalowane.
)
if not exist "%USERPROFILE%\.streamlit\credentials.toml" (
  mkdir "%USERPROFILE%\.streamlit" 2>nul
  (echo [general]& echo email = "") > "%USERPROFILE%\.streamlit\credentials.toml"
)
echo [3/3] Uruchamianie serwera Streamlit (zaraz otworzy sie przegladarka na http://localhost:8501)...
echo Nie zamykaj tego okna podczas korzystania z programu.
.venv\Scripts\streamlit run odwolania2json/gui.py --browser.gatherUsageStats false %*
if errorlevel 1 pause
