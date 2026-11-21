@echo off
cd /d "%~dp0"
echo === Odwolania2JSON - GUI ===
if not exist .venv\Scripts\python.exe (
  echo [1/3] Tworzenie srodowiska Python .venv...
  py -3.13 -m venv .venv 2>nul || py -3 -m venv .venv
) else (
  echo [1/3] Srodowisko Python .venv gotowe.
)
if not exist .venv\Scripts\streamlit.exe (
  echo [2/3] Instalacja bibliotek GUI - pierwsze uruchomienie, prosze czekac...
  .venv\Scripts\python -m pip install -r requirements.txt -r requirements-gui.txt
) else (
  echo [2/3] Biblioteki GUI zainstalowane.
)
.venv\Scripts\python -c "from pathlib import Path; p = Path.home() / '.streamlit' / 'credentials.toml'; p.parent.mkdir(exist_ok=True); p.exists() or p.write_text('[general]\nemail = \"\"\n', encoding='utf-8')" 2>nul
echo [3/3] Uruchamianie serwera Streamlit na http://localhost:8501 ...
echo Nie zamykaj tego okna podczas korzystania z programu.
.venv\Scripts\python -m streamlit run odwolania2json/gui.py --browser.gatherUsageStats false %*
pause
