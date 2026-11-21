import re
from collections.abc import Iterable, Iterator
from pathlib import Path

import yaml
from pypdf import PdfReader

from .ocr import tekst_skanu
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


def tekst_pdf(pdf: Path, ust: dict) -> str:
    strony = [strona.extract_text() or "" for strona in PdfReader(pdf).pages]
    skany = [nr for nr, tekst in enumerate(strony) if len(tekst.strip()) < ust["liczby"]["MIN_ZNAKOW_STRONY"]]
    for nr, tekst in zip(skany, tekst_skanu(pdf, skany, ust) if skany else []):
        strony[nr] = tekst
    return "\n".join(strony)


def _scisnij(s: str, bez_znakow: dict) -> str:
    # „P E Ł N O M O C N I C T W O” → „pelnomocnictwo”; bez polskich znaków, bo OCR je gubi
    return re.sub(r"\s+", "", s).lower().translate(bez_znakow)


def _jest(znacznik: str | list[str], plaski: str, bez_znakow: dict) -> bool:
    warianty = znacznik if isinstance(znacznik, list) else [znacznik]
    return any(_scisnij(w, bez_znakow) in plaski for w in warianty)


def klasyfikuj(tekst: str, typy: list[dict], ust: dict) -> dict | None:
    bez_znakow = str.maketrans({litera: zamiany[0] for litera, zamiany in ust["warianty_liter"].items()})
    plaski = _scisnij(tekst, bez_znakow)
    najlepszy, najlepszy_wynik = None, 0.0
    for t in typy:
        if any(_jest(w, plaski, bez_znakow) for w in t["wykluczenia"]):
            continue
        znaczniki = t["znaczniki"]
        wynik = sum(_jest(z, plaski, bez_znakow) for z in znaczniki) / len(znaczniki)
        if wynik > najlepszy_wynik:
            najlepszy, najlepszy_wynik = t, wynik
    return najlepszy if najlepszy is not None and najlepszy_wynik >= najlepszy["prog"] else None


def wyciagnij(tekst: str, typ: dict, dziennik: list | None = None) -> dict:
    wynik, zamkniete = pusty(typ["szablon"]), set()
    for sciezka, spec in typ["pola"].items():
        wypelnij(wynik, typ["szablon"], sciezka, spec, tekst, zamkniete, dziennik)
    return wynik


def przetworz(pdf: Path, typy: list[dict], ust: dict, dziennik: list | None = None) -> tuple[str, dict] | None:
    tekst = tekst_pdf(pdf, ust)
    typ = klasyfikuj(tekst, typy, ust)
    return None if typ is None else (typ["typ"], wyciagnij(tekst, typ, dziennik))


def przetworz_wszystkie(pdfy: Iterable[Path], typy: list[dict], ust: dict,
                        dzienniki: dict | None = None) -> Iterator[tuple[Path, tuple[str, dict] | None, Exception | None]]:
    for pdf in pdfy:
        try:
            dziennik = dzienniki.setdefault(pdf, []) if dzienniki is not None else None
            yield pdf, przetworz(pdf, typy, ust, dziennik), None
        except Exception as blad:
            yield pdf, None, blad
