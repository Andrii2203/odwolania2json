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


def pusty(ksztalt):
    if isinstance(ksztalt, dict):
        return {k: pusty(v) for k, v in ksztalt.items()}
    if isinstance(ksztalt, list):
        return []
    return None


def ustaw(wynik: dict, sciezka: str, wartosc) -> None:
    *rodzice, klucz = sciezka.split(".")
    for r in rodzice:
        wynik = wynik[r]
    wynik[klucz] = wartosc


def _wez(obiekt, sciezka: str):
    for klucz in filter(None, sciezka.split(".")):
        obiekt = obiekt[klucz]
    return obiekt


@cache
def _wzorzec(wzorzec: str) -> re.Pattern:
    fragmenty = ustawienia().get("wzorce", {})
    while (nowy := re.sub(r"\{([A-Z_]+)\}", lambda m: fragmenty.get(m[1], m[0]), wzorzec)) != wzorzec:
        wzorzec = nowy
    return re.compile(wzorzec, re.MULTILINE)


def trafienia(tekst: str, spec: dict) -> list[tuple[int, object]]:
    wyniki, widziane = [], set()
    for w in spec["wzorce"]:
        w = w if isinstance(w, dict) else {"wzorzec": w}
        for m in _wzorzec(w["wzorzec"]).finditer(tekst):
            surowe = " ".join(m.group(1 if m.re.groups else 0).split())
            if surowe in widziane:
                continue
            widziane.add(surowe)
            wartosc = re.sub(r"\D", "", surowe) if spec.get("format") == "cyfry" else surowe
            wyniki.append((m.start(), w.get("wartosc", wartosc)))
    return sorted(wyniki, key=lambda t: t[0])


def wypelnij(wynik: dict, szablon: dict, sciezka: str, spec: dict, tekst: str, zamkniete: set) -> None:
    znalezione = trafienia(tekst, spec)
    czesci = sciezka.split("[]")
    if not znalezione:
        return
    if len(czesci) == 1:
        ustaw(wynik, sciezka, znalezione[0][1])
        return
    lista, wzor = _wez(wynik, czesci[0]), _wez(szablon, czesci[0])[0]
    granice = [m.start() for m in _wzorzec(spec["podzial"]).finditer(tekst)] if "podzial" in spec else []
    for i, (poz, wartosc) in enumerate(znalezione):
        if len(czesci) == 3:
            i = min(max(sum(g <= poz for g in granice) - 1, 0), max(len(lista) - 1, 0))
        if i >= len(lista):
            if czesci[0] in zamkniete:
                break
            lista.append(pusty(wzor))
        element, reszta = lista[i], czesci[-1]
        if len(czesci) == 3:
            wewnetrzna = _wez(element, czesci[1])
            wewnetrzna.append(pusty(_wez(wzor, czesci[1])[0]))
            element = wewnetrzna[-1]
        ustaw(element, reszta.lstrip("."), wartosc)
    zamkniete.add(czesci[0])


def wyciagnij(tekst: str, spec: dict, wszystkie: dict) -> object:
    start = _znajdz_etykiete(tekst, spec["etykiety"])
    if start is None:
        return None
    if spec["format"] == "tekst":
        stopy = [e for s in wszystkie.values() if s is not spec for e in s.get("etykiety", [])] + spec.get("stop", [])
        return _tekst(tekst, start, stopy)
    return FORMATY[spec["format"]](tekst[start:start + ustawienia()["okno_znakow"]])
