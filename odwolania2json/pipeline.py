import re
from pathlib import Path

import yaml
from pypdf import PdfReader

from .pola import przygotuj, pusty, wypelnij

ROOT = Path(__file__).resolve().parents[1]
KONFIG = ROOT / "config"


def _yaml(p: Path):
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def ustawienia(config: Path = KONFIG) -> dict:
    return _yaml(config / "ustawienia.yaml")


def load_types(config: Path = KONFIG) -> list[dict]:
    ust = ustawienia(config)
    types = [_yaml(p) for p in sorted((config / "typy").glob("*.yaml"))]
    for t in types:
        t["prog"] = ust["liczby"]["PROG"]
        t["wykluczenia"] = ust["wykluczenia"] + t.get("wykluczenia", [])
        przygotuj(t.setdefault("pola", {}), ust)
    return types


def pdf_text(pdf: Path) -> str:
    try:
        return "\n".join(page.extract_text() or "" for page in PdfReader(pdf).pages)
    except Exception:
        return ""


def _squash(s: str) -> str:
    # „P E Ł N O M O C N I C T W O” → „pełnomocnictwo”
    return re.sub(r"\s+", "", s).lower()


def _found(mark: str | list[str], flat: str) -> bool:
    alternatives = mark if isinstance(mark, list) else [mark]
    return any(_squash(m) in flat for m in alternatives)


def classify(text: str, types: list[dict]) -> dict | None:
    flat = _squash(text)
    best, best_score = None, 0.0
    for t in types:
        if any(_found(w, flat) for w in t["wykluczenia"]):
            continue
        marks = t["znaczniki"]
        score = sum(_found(m, flat) for m in marks) / len(marks)
        if score > best_score:
            best, best_score = t, score
    return best if best is not None and best_score >= best["prog"] else None


def extract(text: str, typ: dict) -> dict:
    wynik, zamkniete = pusty(typ["szablon"]), set()
    for sciezka, spec in typ["pola"].items():
        wypelnij(wynik, typ["szablon"], sciezka, spec, text, zamkniete)
    return wynik


def process(pdf: Path, types: list[dict]) -> tuple[str, dict] | None:
    text = pdf_text(pdf)
    typ = classify(text, types)
    return None if typ is None else (typ["typ"], extract(text, typ))
