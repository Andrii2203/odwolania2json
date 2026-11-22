import argparse
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from odwolania2json.cli import konsola_utf8
from odwolania2json.pipeline import ROOT, ustawienia

OBCE = ROOT / "data" / "obce"
PRZYKLAD = ROOT / "data" / "przyklad_ted"
TED_API = "https://api.ted.europa.eu/v3/notices/search"


def _json(url: str, dane: dict) -> dict:
    zapytanie = urllib.request.Request(url, json.dumps(dane).encode(), {"Content-Type": "application/json"})
    with urllib.request.urlopen(zapytanie) as odp:
        return json.load(odp)


def ogloszenia_ted(zapytanie: str, ile: int, jezyk: str, pola: list[str]) -> list[dict]:
    wynik = _json(TED_API, {"query": zapytanie, "fields": ["publication-number", *pola], "limit": ile})
    return [o for o in wynik["notices"] if jezyk in o["links"]["pdf"]]


def _pierwsza(v, jezyk: str):
    if isinstance(v, dict):
        v = v.get(jezyk.lower(), next(iter(v.values()), None))
    if isinstance(v, list):
        v = v[0] if v else None
    return v


def wzorzec_ted(o: dict, ted: dict) -> dict:
    # poprawny JSON nowego typu z danych TED (nie z naszego odczytu PDF): docs/przyklady/ogloszenie_ted.yaml
    wynik = {}
    for sciezka, pole in ted["wzorzec"].items():
        grupa, klucz = sciezka.split(".")
        v = _pierwsza(o.get(pole), ted["jezyk"])
        wynik.setdefault(grupa, {})[klucz] = v.partition("+")[0] if pole in ted["daty"] and v else v
    return wynik


def _pobierz(url: str, plik: Path) -> None:
    if not plik.exists():
        with urllib.request.urlopen(url) as odp:
            plik.write_bytes(odp.read())


def main() -> int:
    ap = argparse.ArgumentParser(description="Pobiera obce dokumenty (ogłoszenia TED po polsku) do data/obce/ted")
    ap.add_argument("--cel", type=Path, default=OBCE / "ted")
    ap.add_argument("--przyklad", type=Path, default=PRZYKLAD,
                    help="tu każde ogłoszenie w osobnym katalogu z poprawnym JSON (przykład nowego typu)")
    args = ap.parse_args()
    konsola_utf8()
    ted = ustawienia()["narzedzia"]["obce_ted"]
    args.cel.mkdir(parents=True, exist_ok=True)
    lista = ogloszenia_ted(ted["zapytanie"], ted["ILE"], ted["jezyk"], sorted(set(ted["wzorzec"].values())))
    rozwoj = round(len(lista) * ted["CZESC_ROZWOJ"])
    for nr, o in enumerate(lista):
        numer = o["publication-number"]
        plik = args.cel / f"ted-{numer}.pdf"
        _pobierz(o["links"]["pdf"][ted["jezyk"]], plik)
        sprawa = args.przyklad / ("rozwoj" if nr < rozwoj else "pomiar") / numer
        sprawa.mkdir(parents=True, exist_ok=True)
        (sprawa / "ogloszenie.pdf").write_bytes(plik.read_bytes())
        (sprawa / "ogloszenie.json").write_text(json.dumps(wzorzec_ted(o, ted), ensure_ascii=False), encoding="utf-8")
    print(f"Ogłoszenia TED: {len(lista)} w {args.cel}; przykład nowego typu: {rozwoj} do reguł, reszta do pomiaru, w {args.przyklad}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
