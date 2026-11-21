import re
from collections.abc import Iterable, Iterator
from pathlib import Path

import yaml
from pypdf import PdfReader

from .kontekst import uzupelnij_sprawe
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
        t["rozdzielnik_cyfr"] = ust["wzorce"]["ROZDZIELNIK_CYFR"]
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


def dokument_z_tekstu(tekst: str, typy: list[dict], ust: dict, dziennik: list) -> dict:
    typ = klasyfikuj(tekst, typy, ust)
    dane = wyciagnij(tekst, typ, dziennik) if typ else None
    return {"typ": typ and typ["typ"], "tekst": tekst, "dane": dane, "dziennik": dziennik}


def przetworz(pdf: Path, typy: list[dict], ust: dict) -> tuple[str, dict] | None:
    d = dokument_z_tekstu(tekst_pdf(pdf, ust), typy, ust, [])
    return (d["typ"], d["dane"]) if d["typ"] else None


def _dokument(pdf: Path, typy: list[dict], ust: dict, dziennik: list) -> dict:
    try:
        return {"pdf": pdf, "blad": None, **dokument_z_tekstu(tekst_pdf(pdf, ust), typy, ust, dziennik)}
    except Exception as blad:
        return {"pdf": pdf, "typ": None, "tekst": "", "dane": None, "dziennik": dziennik, "blad": blad}


def kontekst_sprawy(dokumenty: list[dict], po_typie: dict[str, dict], ust: dict) -> None:
    if not ust["etapy"]["kontekst_sprawy"]:
        return
    try:
        uzupelnij_sprawe([d for d in dokumenty if d["typ"]], po_typie)
    except Exception as blad:
        for d in dokumenty:
            d["dziennik"].append({"pole": "-", "wartosc": None, "regula": f"kontekst sprawy: błąd {blad!r}", "fragment": ""})


def przetworz_wszystkie(pdfy: Iterable[Path], typy: list[dict], ust: dict,
                        dzienniki: dict | None = None) -> Iterator[tuple[Path, tuple[str, dict] | None, Exception | None]]:
    sprawy: dict[Path, list[Path]] = {}
    for pdf in pdfy:
        sprawy.setdefault(pdf.parent, []).append(pdf)
    po_typie = {t["typ"]: t for t in typy}
    for pliki in sprawy.values():
        dokumenty = [_dokument(pdf, typy, ust, dzienniki.setdefault(pdf, []) if dzienniki is not None else []) for pdf in pliki]
        kontekst_sprawy(dokumenty, po_typie, ust)
        for d in dokumenty:
            yield d["pdf"], (d["typ"], d["dane"]) if d["typ"] else None, d["blad"]
