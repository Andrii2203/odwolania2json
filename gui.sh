#!/bin/sh
# GUI w przeglądarce na Linuksie (jak gui.bat), na porcie PORT_GUI z config/ustawienia.yaml (ADR-0006).
cd "$(dirname "$0")"
[ -x .venv/bin/python ] || sh instaluj.sh
.venv/bin/python -c "import streamlit" 2>/dev/null || .narzedzia/bin/uv pip install -q --python .venv/bin/python -r requirements-gui.txt
port=$(.venv/bin/python -c "from odwolania2json.pipeline import ustawienia; print(ustawienia()['liczby']['PORT_GUI'])")
exec .venv/bin/python -m streamlit run odwolania2json/gui.py --server.address 0.0.0.0 --server.port "$port" \
  --server.headless true --server.runOnSave true --browser.gatherUsageStats false
