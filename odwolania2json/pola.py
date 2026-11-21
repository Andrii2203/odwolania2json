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


def _bez_spacji(ust: dict, s: str) -> str:
    return re.sub(r"\s", "", s)


FORMATY = {"cyfry": _cyfry, "liczba": _liczba, "data": _data, "tekst": _tekst, "bez_spacji": _bez_spacji}


def _etykiety(etykiety: list[str]) -> str:
    return r"(?i:(?<!\w)(?:" + "|".join(r"\s+".join(map(re.escape, e.split())) for e in etykiety) + r")(?!\w))"


def _rozwin(wzorzec: str, fragmenty: dict, warianty: dict) -> re.Pattern:
    while (nowy := re.sub(r"\{([A-Z_]+)\}", lambda m: fragmenty.get(m[1], m[0]), wzorzec)) != wzorzec:
        wzorzec = nowy
    # poza klasami [...] litera z polskim znakiem pasuje też do tego, co z niej robi OCR: „ł” -> „[łlt]”
    wzorzec = re.sub(r"\\.|\[(?:\\.|[^\]\\])*\]|.", lambda m: f"[{m[0]}{warianty[m[0]]}]" if m[0] in warianty else m[0],
                     wzorzec, flags=re.DOTALL)
    return re.compile(wzorzec, re.MULTILINE)


def _wartosc(format_, slownik: dict | None, m: re.Match, surowe: str, stala: str | None):
    wartosc = format_(surowe) if stala is None else stala.format(**{k: v or "" for k, v in m.groupdict().items()})
    return wartosc if slownik is None else slownik.get(wartosc)


def przygotuj(pola: dict, ust: dict, fragmenty_typu: dict) -> None:
    wspolne = {**{k: str(v) for k, v in ust["liczby"].items()}, **ust["wzorce"], **fragmenty_typu,
               "MIESIAC": "|".join(ust["miesiace"])}
    warianty = {**ust["warianty_liter"], **{k.upper(): v.upper() for k, v in ust["warianty_liter"].items()}}
    for spec in pola.values():
        stopy = [e for s in pola.values() if s is not spec for e in s.get("etykiety", [])] + spec.get("stop", [])
        fragmenty = {**wspolne, "STOP": _etykiety(stopy) if stopy else "(?!)"}
        spec["_stopy"] = {" ".join(e.lower().split()) for e in stopy}
        przedrostki = [_etykiety([e]) + "{PO_ETYKIECIE}" for e in spec["etykiety"]] if "etykiety" in spec else [""]
        wzorce = [w if isinstance(w, dict) else {"wzorzec": w} for w in spec["wzorce"]]
        sekcja = _rozwin(spec["sekcja"], fragmenty, warianty) if "sekcja" in spec else None
        spec["_wzorce"] = [(_rozwin(p + w["wzorzec"], fragmenty, warianty), w.get("wartosc"),
                            _rozwin(w["sekcja"], fragmenty, warianty) if "sekcja" in w else sekcja)
                           for p in przedrostki for w in wzorce]
        spec["_podzial"] = _rozwin(spec["podzial"], fragmenty, warianty) if "podzial" in spec else None
        format_ = partial(FORMATY[spec["format"]], ust) if "format" in spec else str
        spec["_wartosc"] = partial(_wartosc, format_, ust["slowniki"][spec["slownik"]] if "slownik" in spec else None)


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


def _zakresy(sekcja: re.Pattern | None, tekst: str) -> list[tuple[int, int]]:
    return [m.span() for m in sekcja.finditer(tekst)] if sekcja else [(0, len(tekst))]


def trafienia(tekst: str, spec: dict) -> list[tuple[int, object]]:
    trafione = sorted(((m, stala) for wzorzec, stala, sekcja in spec["_wzorce"] for od, do in _zakresy(sekcja, tekst)
                       for m in wzorzec.finditer(tekst, od, do)), key=lambda t: t[0].start())
    wyniki, widziane = [], set()
    for m, stala in trafione:
        surowe = " ".join(m.group(1 if m.re.groups else 0).split())
        if surowe in widziane:
            continue
        widziane.add(surowe)
        wartosc = spec["_wartosc"](m, surowe, stala)
        if wartosc not in (None, "") and str(wartosc).lower() not in spec["_stopy"]:
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
    glowa, *srodek, reszta = czesci
    lista, wzor = _wez(wynik, glowa), _wez(szablon, glowa)[0]
    granice = [m.start() for m in spec["_podzial"].finditer(tekst)] if spec["_podzial"] else None
    for i, (poz, wartosc) in enumerate(znalezione):
        if granice is not None:
            i = max(sum(g <= poz for g in granice) - 1, 0)
        if srodek:
            i = min(i, max(len(lista) - 1, 0))
        while i >= len(lista) and glowa not in zamkniete:
            lista.append(pusty(wzor))
        if i >= len(lista):
            break
        element = lista[i]
        if srodek:
            wewnetrzna = _wez(element, srodek[0])
            wewnetrzna.append(pusty(_wez(wzor, srodek[0])[0]))
            element = wewnetrzna[-1]
        elif _wez(element, reszta) is not None:
            continue
        ustaw(element, reszta.lstrip("."), wartosc)
    zamkniete.add(glowa)
