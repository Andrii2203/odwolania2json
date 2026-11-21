#!/bin/sh
# Instalacja na maszynie UZP (Ubuntu, ADR-0017): Python 3.13 i zależności w katalogu projektu, modele OCR pobrane od razu.
set -e
cd "$(dirname "$0")"
export UV_PYTHON_INSTALL_DIR="$PWD/.python" UV_CACHE_DIR="$PWD/.uv-cache"
[ -x .narzedzia/bin/uv ] || { python3 -m venv .narzedzia && .narzedzia/bin/pip install -q uv==0.12.24; }
[ -x .venv/bin/python ] || .narzedzia/bin/uv venv --python 3.13 .venv
.narzedzia/bin/uv pip install -q --python .venv/bin/python -r requirements.txt
.venv/bin/python -c "from odwolania2json.ocr import _silnik; _silnik()"
echo "Gotowe. Uruchomienie: sh uruchom.sh"
