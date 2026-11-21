import re
from pathlib import Path

import yaml
from pypdf import PdfReader


def load_types(config_dir: Path) -> list[dict]:
    return [yaml.safe_load(p.read_text(encoding="utf-8")) for p in sorted(config_dir.glob("*.yaml"))]


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
        if any(_found(w, flat) for w in t.get("wykluczenia", [])):
            continue
        marks = t["znaczniki"]
        score = sum(_found(m, flat) for m in marks) / len(marks)
        if score > best_score:
            best, best_score = t, score
    return best if best is not None and best_score >= best["prog"] else None


def _empty(shape):
    if isinstance(shape, dict):
        return {k: _empty(v) for k, v in shape.items()}
    if isinstance(shape, list):
        return []
    return None


def extract(text: str, typ: dict) -> dict:
    return _empty(typ["szablon"])


def process(pdf: Path, types: list[dict]) -> tuple[str, dict] | None:
    text = pdf_text(pdf)
    typ = classify(text, types)
    return None if typ is None else (typ["typ"], extract(text, typ))
