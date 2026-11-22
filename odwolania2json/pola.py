import re
from datetime import datetime
from functools import cache, partial


def _cyfry(ust: dict, s: str) -> str:
    return re.sub(r"\D", "", s)


def _liczba(ust: dict, s: str) -> float:
    if m := re.fullmatch(rf"(.*)[{re.escape(ust['separatory_dziesietne'])}](\d+)", s):
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


@cache
def _morfeusz():
    import morfeusz2
    return morfeusz2.Morfeusz(generate=False)


def _formy(slowo: str) -> dict[tuple[str, str], str]:
    # (rodzaj, przypadek) -> forma podstawowa; tylko nazwy własne (rzeczownik z wielkiej litery)
    formy = {}
    for *_, (_, lemat, tag, *_) in _morfeusz().analyse(slowo):
        if not tag.startswith("subst:") or not lemat[:1].isupper():
            continue
        _, _, przypadki, rodzaje, *_ = tag.split(":")
        for przypadek in przypadki.split("."):
            for rodzaj in rodzaje.split("."):
                formy.setdefault((rodzaj, przypadek), lemat.split(":")[0])
    return formy


def _mianownik(ust: dict, s: str) -> str:
    # rodzaj i przypadek wspólne dla wszystkich znanych słów; słowo spoza słownika SGJP bez zmian (T24)
    formy = {w: _formy(w) for w in re.findall(r"[^\s-]+", s)}
    znane = [f for f in formy.values() if f]
    if not znane or all(any(p == "nom" for _, p in f) for f in znane):
        return s
    wspolne = set.intersection(*map(set, znane))
    if not wspolne:
        return s
    klucz = min(wspolne)
    return re.sub(r"[^\s-]+", lambda m: formy[m.group()].get(klucz, m.group()), s)


FORMATY = {"cyfry": _cyfry, "liczba": _liczba, "data": _data, "tekst": _tekst, "bez_spacji": _bez_spacji,
           "mianownik": _mianownik}


def fraza(s: str) -> str:
    return r"\s+".join(map(re.escape, s.split()))


def _etykiety(etykiety: list[str]) -> str:
    return r"(?i:(?<!\w)(?:" + "|".join(map(fraza, etykiety)) + r")(?!\w))"


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
        etykiety = spec.get("etykiety", [None])
        przedrostki = [_etykiety([e]) + "{PO_ETYKIECIE}" if e else "" for e in etykiety]
        wzorce = [w if isinstance(w, dict) else {"wzorzec": w} for w in spec["wzorce"]]
        spec["_opisy"] = [(f"etykieta „{e}”, " if e else "") + f"wzorzec „{w['wzorzec']}”" for e in etykiety for w in wzorce]
        sekcja = _rozwin(spec["sekcja"], fragmenty, warianty) if "sekcja" in spec else None
        spec["_wzorce"] = [(_rozwin(p + w["wzorzec"], fragmenty, warianty), w.get("wartosc"),
                            _rozwin(w["sekcja"], fragmenty, warianty) if "sekcja" in w else sekcja)
                           for p in przedrostki for w in wzorce]
        spec["_podzial"] = _rozwin(spec["podzial"], fragmenty, warianty) if "podzial" in spec else None
        spec["_utnij"] = _rozwin("|".join(f"(?:{w})" for w in spec["utnij"]), fragmenty, warianty) if "utnij" in spec else None
        spec["_obcinane_po_bramce"] = ust["obcinane_po_bramce"]
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


def wez(obiekt, sciezka: str):
    for klucz in filter(None, sciezka.split(".")):
        obiekt = obiekt[klucz]
    return obiekt


def _zakresy(sekcja: re.Pattern | None, tekst: str) -> list[tuple[int, int]]:
    return [m.span() for m in sekcja.finditer(tekst)] if sekcja else [(0, len(tekst))]


def trafienia(tekst: str, spec: dict) -> list[tuple[int, object, str, str]]:
    trafione = sorted(((m, stala, opis) for (wzorzec, stala, sekcja), opis in zip(spec["_wzorce"], spec["_opisy"])
                       for od, do in _zakresy(sekcja, tekst) for m in wzorzec.finditer(tekst, od, do)),
                      key=lambda t: t[0].start())
    wyniki, widziane = [], set()
    for m, stala, opis in trafione:
        surowe = " ".join(m.group(1 if m.re.groups else 0).split())
        if surowe in widziane:
            continue
        widziane.add(surowe)
        if spec["_utnij"] and (stop := spec["_utnij"].search(surowe)):
            surowe = surowe[:stop.start()].rstrip(spec["_obcinane_po_bramce"])
            opis = f"{opis}; bramka: ucięte przed „{stop[0].strip()}”"
        wartosc = spec["_wartosc"](m, surowe, stala)
        # ta sama wartość innym zapisem („999-509-02-81” = „9995090281”); stała może się powtarzać (T18)
        if stala is None and (wartosc,) in widziane:
            continue
        widziane.add((wartosc,))
        if wartosc not in (None, "") and str(wartosc).lower() not in spec["_stopy"]:
            wyniki.append((m.start(), wartosc, opis, " ".join(m[0].split())))
    return wyniki


def wypelnij(wynik: dict, szablon: dict, sciezka: str, spec: dict, tekst: str, zamkniete: set,
             dziennik: list | None = None) -> None:
    znalezione = trafienia(tekst, spec)
    czesci = sciezka.split("[]")
    zapisz = dziennik.append if dziennik is not None else lambda _: None
    if not znalezione:
        return
    if len(czesci) == 1:
        _, wartosc, opis, fragment = znalezione[0]
        ustaw(wynik, sciezka, wartosc)
        zapisz({"pole": sciezka, "wartosc": wartosc, "regula": opis, "fragment": fragment})
        return
    glowa, *srodek, reszta = czesci
    lista, wzor = wez(wynik, glowa), wez(szablon, glowa)[0]
    granice = [m.start() for m in spec["_podzial"].finditer(tekst)] if spec["_podzial"] else None
    for i, (poz, wartosc, opis, fragment) in enumerate(znalezione):
        if granice is not None:
            i = max(sum(g <= poz for g in granice) - 1, 0)
        if srodek:
            i = min(i, max(len(lista) - 1, 0))
        while i >= len(lista) and glowa not in zamkniete:
            lista.append(pusty(wzor))
        if i >= len(lista):
            break
        element = lista[i]
        konkretna = f"{glowa}[{i}]{reszta}"
        if srodek:
            wewnetrzna = wez(element, srodek[0])
            wewnetrzna.append(pusty(wez(wzor, srodek[0])[0]))
            element = wewnetrzna[-1]
            konkretna = f"{glowa}[{i}]{srodek[0]}[{len(wewnetrzna) - 1}]{reszta}"
        elif wez(element, reszta) is not None:
            continue
        ustaw(element, reszta.lstrip("."), wartosc)
        zapisz({"pole": konkretna, "wartosc": wartosc, "regula": opis, "fragment": fragment})
    zamkniete.add(glowa)
