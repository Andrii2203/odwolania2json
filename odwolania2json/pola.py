import re
from functools import cache
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MIESIACE = {"stycznia": 1, "lutego": 2, "marca": 3, "kwietnia": 4, "maja": 5, "czerwca": 6, "lipca": 7,
            "sierpnia": 8, "września": 9, "października": 10, "listopada": 11, "grudnia": 12}


@cache
def ustawienia() -> dict:
    return yaml.safe_load((ROOT / "config" / "ustawienia.yaml").read_text(encoding="utf-8"))


def _wzorzec_etykiety(etykieta: str, od_linii: bool = False) -> re.Pattern:
    wzorzec = r"(?<!\w)" + r"\s+".join(map(re.escape, etykieta.split())) + r"(?!\w)"
    return re.compile((r"^[ \t]*" if od_linii else "") + wzorzec, re.IGNORECASE | re.MULTILINE)


def _rachunek(okno: str) -> str | None:
    m = re.search(r"(?:PL)?\s*(\d{2}(?:\s?\d{4}){6})(?!\d)", okno)
    return re.sub(r"\D", "", m.group(1)) if m else None


def _kwota(okno: str) -> float | None:
    m = re.search(r"(?<![\d,.])(\d{1,3}(?:[  .]\d{3})+|\d+)[,.](\d{2})(?!\d)", okno)
    return float(re.sub(r"\D", "", m.group(1)) + "." + m.group(2)) if m else None


def _data(okno: str) -> str | None:
    kandydaci = []
    if m := re.search(r"(\d{4})-(\d{2})-(\d{2})", okno):
        kandydaci.append((m.start(), f"{m[1]}-{m[2]}-{m[3]}"))
    if m := re.search(r"(?<!\d)(\d{1,2})[.\-/](\d{1,2})[.\-/](\d{4})", okno):
        kandydaci.append((m.start(), f"{m[3]}-{int(m[2]):02d}-{int(m[1]):02d}"))
    if m := re.search(r"(?<!\d)(\d{1,2})\s+(" + "|".join(MIESIACE) + r")\s+(\d{4})", okno, re.IGNORECASE):
        kandydaci.append((m.start(), f"{m[3]}-{MIESIACE[m[2].lower()]:02d}-{int(m[1]):02d}"))
    return min(kandydaci)[1] if kandydaci else None


def _identyfikator(okno: str) -> str | None:
    m = re.search(r"(?<![A-Za-z0-9])(?=[A-Z0-9/-]*\d)[A-Z0-9][A-Z0-9/-]{5,}", okno)
    return m.group(0) if m else None


FORMATY = {"rachunek": _rachunek, "kwota": _kwota, "data": _data, "identyfikator": _identyfikator}


def _znajdz_etykiete(tekst: str, etykiety: list[str]) -> int | None:
    for etykieta in etykiety:
        if m := _wzorzec_etykiety(etykieta).search(tekst):
            return m.end()
    return None


def _tekst(tekst: str, start: int, stopy: list[str]) -> str | None:
    reszta = tekst[start:start + ustawienia()["okno_tekstu"]]
    koniec = min((m.start() for s in stopy if (m := _wzorzec_etykiety(s, od_linii=True).search(reszta))),
                 default=len(reszta))
    wartosc = " ".join(reszta[:koniec].split()).lstrip(":.-– „\"").rstrip(" .”\"")
    return wartosc or None


def wyciagnij(tekst: str, spec: dict, wszystkie: dict) -> object:
    start = _znajdz_etykiete(tekst, spec["etykiety"])
    if start is None:
        return None
    if spec["format"] == "tekst":
        stopy = [e for s in wszystkie.values() if s is not spec for e in s["etykiety"]] + spec.get("stop", [])
        return _tekst(tekst, start, stopy)
    return FORMATY[spec["format"]](tekst[start:start + ustawienia()["okno_znakow"]])
