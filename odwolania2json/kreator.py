import copy
import re
from collections.abc import Iterator

import yaml

from .kontekst import cyfry_w_tekscie
from .pipeline import klasyfikuj, przygotuj_typ, ustawienia, wczytaj_typy, wyciagnij
from .pola import FORMATY, fraza, wez


def szablon(sciezki: list[str]) -> dict:
    # „Nabywca.nazwa” -> {"Nabywca": {"nazwa": None}}
    wynik = {}
    for sciezka in sciezki:
        *grupy, klucz = sciezka.split(".")
        cel = wynik
        for grupa in grupy:
            cel = cel.setdefault(grupa, {})
        cel[klucz] = None
    return wynik


def typ_z_formularza(nazwa: str, opis: str, znaczniki: list[str], pola: list[dict], rodzaje: dict,
                     wspolne_wykluczenia: bool = True) -> dict:
    # rodzaj pola (z config/ustawienia.yaml, kreator.rodzaje) daje wzorce, format i bramkę: bez pisania wyrażeń regularnych
    spec = {}
    for p in pola:
        spec[p["pole"]] = {**({"etykiety": p["etykiety"]} if p["etykiety"] else {}), **copy.deepcopy(rodzaje[p["rodzaj"]])}
    return {"typ": nazwa, "opis": opis, "znaczniki": znaczniki, "wspolne_wykluczenia": wspolne_wykluczenia,
            "szablon": szablon([p["pole"] for p in pola]), "pola": spec}


def jako_yaml(typ: dict) -> str:
    return yaml.safe_dump(typ, allow_unicode=True, sort_keys=False)


def sprobuj(tekst_yaml: str, tekst: str) -> dict:
    # nowy typ obok istniejących, jak po wrzuceniu pliku do config/typy/
    typy, ust = wczytaj_typy(dodatkowe=[tekst_yaml]), ustawienia()
    typ = next(t for t in typy if t["typ"] == yaml.safe_load(tekst_yaml)["typ"])
    rozpoznany, dziennik = klasyfikuj(tekst, typy, ust), []
    return {"rozpoznany": rozpoznany and rozpoznany["typ"], "dane": wyciagnij(tekst, typ, dziennik), "dziennik": dziennik}


def etykiety_przed(tekst: str, wartosc: str, ust: dict) -> Iterator[str]:
    # słowa przed wartością w tej samej linii; gdy wartość zaczyna linię: poprzednia linia (etykieta nad wartością)
    wzor = re.compile(ust["kreator"]["etykieta_przed"])
    cyfry = "".join(wartosc.split())
    szukany = cyfry_w_tekscie(cyfry, ust["wzorce"]["ROZDZIELNIK_CYFR"]) if cyfry.isdigit() else re.compile(fraza(wartosc))
    for m in szukany.finditer(tekst):
        poczatek = tekst.rfind("\n", 0, m.start()) + 1
        przed = tekst[poczatek:m.start()] if tekst[poczatek:m.start()].strip() else tekst[:poczatek].rstrip().split("\n")[-1]
        e = wzor.search(przed)
        yield e[1].strip() if e and re.search(r"[^\W\d_]", e[1]) else ""


def _oczekiwane(wartosc: str, rodzaj: dict, ust: dict) -> list:
    if "format" not in rodzaj:
        return [" ".join(wartosc.split())]
    wyniki = []
    # „200,00 PLN”, „21.03.2026 r.”: format dostaje też wartość bez dopisku na końcu
    for s in dict.fromkeys([wartosc, re.sub(ust["kreator"]["dopisek_po_wartosci"], "", wartosc.strip())]):
        try:
            wyniki.append(FORMATY[rodzaj["format"]](ust, s))
        except ValueError:
            pass
    return [w for w in wyniki if w is not None]


def pole_z_przykladu(pole: str, wartosc: str, tekst: str, rodzaje: dict, ust: dict,
                     etykieta: str | None = None, rodzaj: str | None = None) -> dict | None:
    # pierwszy rodzaj (kolejność z kreator.rodzaje, najpierw ten z nazwą w etykiecie), z którym typ odtwarza wartość;
    # najpierw krótsze etykiety, na końcu bez etykiety; wartość jest w dokumencie, ale żaden rodzaj jej nie odtwarza:
    # etykieta bez rodzaju (wybiera użytkownik); wartości nie ma w dokumencie: None
    znalezione = set(etykiety_przed(tekst, wartosc, ust))
    if not (znalezione or etykieta):
        return None
    etykiety = [etykieta] if etykieta else sorted(znalezione - {""}, key=len) + [""]
    for e in etykiety:
        kandydaci = [rodzaj] if rodzaj else sorted(rodzaje, key=lambda r: r.lower() not in e.lower())
        for r in kandydaci:
            proba = {"pole": pole, "etykiety": [e] if e else [], "rodzaj": r}
            typ = przygotuj_typ(typ_z_formularza(pole, pole, [], [proba], rodzaje), ust)
            if (wynik := wez(wyciagnij(tekst, typ), pole)) is not None and wynik in _oczekiwane(wartosc, rodzaje[r], ust):
                return proba
    return {"pole": pole, "etykiety": [e for e in etykiety[:1] if e], "rodzaj": None}
