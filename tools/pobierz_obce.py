import argparse
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from odwolania2json.cli import konsola_utf8
from odwolania2json.pipeline import ROOT, ustawienia

OBCE = ROOT / "data" / "obce"
TED_API = "https://api.ted.europa.eu/v3/notices/search"


def _json(url: str, dane: dict) -> dict:
    zapytanie = urllib.request.Request(url, json.dumps(dane).encode(), {"Content-Type": "application/json"})
    with urllib.request.urlopen(zapytanie) as odp:
        return json.load(odp)


def ogloszenia_ted(zapytanie: str, ile: int, jezyk: str) -> list[tuple[str, str]]:
    wynik = _json(TED_API, {"query": zapytanie, "fields": ["publication-number"], "limit": ile})
    return [(o["publication-number"], o["links"]["pdf"][jezyk]) for o in wynik["notices"] if jezyk in o["links"]["pdf"]]


def main() -> int:
    ap = argparse.ArgumentParser(description="Pobiera obce dokumenty (ogłoszenia TED po polsku) do data/obce/ted")
    ap.add_argument("--cel", type=Path, default=OBCE / "ted")
    args = ap.parse_args()
    konsola_utf8()
    ted = ustawienia()["narzedzia"]["obce_ted"]
    args.cel.mkdir(parents=True, exist_ok=True)
    lista = ogloszenia_ted(ted["zapytanie"], ted["ILE"], ted["jezyk"])
    for numer, url in lista:
        plik = args.cel / f"ted-{numer}.pdf"
        if not plik.exists():
            with urllib.request.urlopen(url) as odp:
                plik.write_bytes(odp.read())
    print(f"Ogłoszenia TED: {len(lista)} w {args.cel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
