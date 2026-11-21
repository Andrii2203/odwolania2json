import re
from pathlib import Path

import yaml
from pypdf import PdfReader

from .pola import przygotuj, pusty, wypelnij

ROOT = Path(__file__).resolve().parents[1]
KONFIG = ROOT / "config"
USTAWIENIA = "ustawienia.yaml"


def _yaml(p: Path):
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def ustawienia(config: Path = KONFIG) -> dict:
    return _yaml(config / USTAWIENIA)


def wczytaj_typy(config: Path = KONFIG) -> list[dict]:
    ust = ustawienia(config)
    typy = [_yaml(p) for p in sorted((config / "typy").glob("*.yaml"))]
    for t in typy:
        t["prog"] = ust["liczby"]["PROG"]
        t["wykluczenia"] = ust["wykluczenia"] + t.get("wykluczenia", [])
        przygotuj(t.setdefault("pola", {}), ust, t.get("wzorce", {}))
    return typy


def tekst_pdf(pdf: Path) -> str:
    try:
        return "\n".join(strona.extract_text() or "" for strona in PdfReader(pdf).pages)
    except Exception:
        return ""


def _scisnij(s: str) -> str:
    # „P E Ł N O M O C N I C T W O” → „pełnomocnictwo”
    return re.sub(r"\s+", "", s).lower()


def _jest(znacznik: str | list[str], plaski: str) -> bool:
    warianty = znacznik if isinstance(znacznik, list) else [znacznik]
    return any(_scisnij(w) in plaski for w in warianty)


def klasyfikuj(tekst: str, typy: list[dict]) -> dict | None:
    plaski = _scisnij(tekst)
    najlepszy, najlepszy_wynik = None, 0.0
    for t in typy:
        if any(_jest(w, plaski) for w in t["wykluczenia"]):
            continue
        znaczniki = t["znaczniki"]
        wynik = sum(_jest(z, plaski) for z in znaczniki) / len(znaczniki)
        if wynik > najlepszy_wynik:
            najlepszy, najlepszy_wynik = t, wynik
    return najlepszy if najlepszy is not None and najlepszy_wynik >= najlepszy["prog"] else None


def wyciagnij(tekst: str, typ: dict) -> dict:
    wynik, zamkniete = pusty(typ["szablon"]), set()
    for sciezka, spec in typ["pola"].items():
        wypelnij(wynik, typ["szablon"], sciezka, spec, tekst, zamkniete)
    return wynik


def przetworz(pdf: Path, typy: list[dict]) -> tuple[str, dict] | None:
    tekst = tekst_pdf(pdf)
    typ = klasyfikuj(tekst, typy)
    return None if typ is None else (typ["typ"], wyciagnij(tekst, typ))
