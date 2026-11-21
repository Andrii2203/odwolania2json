import re
from datetime import datetime
from functools import partial


def _cyfry(ust: dict, s: str) -> str:
    return re.sub(r"\D", "", s)


def _liczba(ust: dict, s: str) -> float:
    if m := re.fullmatch(r"(.*)[,.](\d+)", s):
        calkowite, ulamek = m.groups()
        return float(_cyfry(ust, calkowite) + "." + ulamek)
    return float(_cyfry(ust, s))


def _data(ust: dict, s: str) -> str | None:
    miesiace = ust["miesiace"]
    s = " ".join(str(miesiace.index(t) + 1) if t in miesiace else t for t in s.lower().split())
    for format_daty in ust["formaty_daty"]:
        try:
            return datetime.strptime(s, format_daty).date().isoformat()
        except ValueError:
            pass
    return None


def _tekst(ust: dict, s: str) -> str:
    return s.strip(ust["obcinane_znaki"])


FORMATY = {"cyfry": _cyfry, "liczba": _liczba, "data": _data, "tekst": _tekst}


def _etykiety(etykiety: list[str]) -> str:
    return r"(?i:(?<!\w)(?:" + "|".join(r"\s+".join(map(re.escape, e.split())) for e in etykiety) + r")(?!\w))"


def _rozwin(wzorzec: str, fragmenty: dict) -> re.Pattern:
    while (nowy := re.sub(r"\{([A-Z_]+)\}", lambda m: fragmenty.get(m[1], m[0]), wzorzec)) != wzorzec:
        wzorzec = nowy
    return re.compile(wzorzec, re.MULTILINE)


def przygotuj(pola: dict, ust: dict) -> None:
    wspolne = {**{k: str(v) for k, v in ust["liczby"].items()}, **ust["wzorce"], "MIESIAC": "|".join(ust["miesiace"])}
    for spec in pola.values():
        stopy = [e for s in pola.values() if s is not spec for e in s.get("etykiety", [])] + spec.get("stop", [])
        fragmenty = {**wspolne, "STOP": _etykiety(stopy) if stopy else "(?!)"}
        przedrostki = [_etykiety([e]) + "{PO_ETYKIECIE}" for e in spec["etykiety"]] if "etykiety" in spec else [""]
        wzorce = [w if isinstance(w, dict) else {"wzorzec": w} for w in spec["wzorce"]]
        spec["_wzorce"] = [(_rozwin(p + w["wzorzec"], fragmenty), w.get("wartosc")) for p in przedrostki for w in wzorce]
        spec["_podzial"] = _rozwin(spec["podzial"], fragmenty) if "podzial" in spec else None
        spec["_format"] = partial(FORMATY[spec["format"]], ust) if "format" in spec else str


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


def trafienia(tekst: str, spec: dict) -> list[tuple[int, object]]:
    wyniki, widziane = [], set()
    for wzorzec, stala in spec["_wzorce"]:
        for m in wzorzec.finditer(tekst):
            surowe = " ".join(m.group(1 if m.re.groups else 0).split())
            if surowe in widziane:
                continue
            widziane.add(surowe)
            wartosc = spec["_format"](surowe) if stala is None else stala
            if wartosc not in (None, ""):
                wyniki.append((m.start(), wartosc))
    return wyniki


def wypelnij(wynik: dict, szablon: dict, sciezka: str, spec: dict, tekst: str, zamkniete: set) -> None:
    znalezione = trafienia(tekst, spec)
    czesci = sciezka.split("[]")
    if not znalezione:
        return
    if len(czesci) == 1:
        ustaw(wynik, sciezka, znalezione[0][1])
        return
    znalezione.sort(key=lambda t: t[0])
    glowa, *srodek, reszta = czesci
    lista, wzor = _wez(wynik, glowa), _wez(szablon, glowa)[0]
    granice = [m.start() for m in spec["_podzial"].finditer(tekst)] if spec["_podzial"] else []
    for i, (poz, wartosc) in enumerate(znalezione):
        if srodek:
            i = min(max(sum(g <= poz for g in granice) - 1, 0), max(len(lista) - 1, 0))
        if i >= len(lista):
            if glowa in zamkniete:
                break
            lista.append(pusty(wzor))
        element = lista[i]
        if srodek:
            wewnetrzna = _wez(element, srodek[0])
            wewnetrzna.append(pusty(_wez(wzor, srodek[0])[0]))
            element = wewnetrzna[-1]
        ustaw(element, reszta.lstrip("."), wartosc)
    zamkniete.add(glowa)
