import copy
import shutil
import tempfile
from pathlib import Path

import yaml

from .pipeline import KONFIG, klasyfikuj, ustawienia, wczytaj_typy, wyciagnij


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


def sprobuj(tekst_yaml: str, tekst: str, config: Path = KONFIG) -> dict:
    # nowy typ obok istniejących (kopia config/), jak po wrzuceniu pliku do config/typy/
    nowy = yaml.safe_load(tekst_yaml)
    with tempfile.TemporaryDirectory() as katalog:
        kopia = Path(katalog) / "config"
        shutil.copytree(config, kopia)
        (kopia / "typy" / f"{nowy['typ']}.yaml").write_text(tekst_yaml, encoding="utf-8")
        typy, ust = wczytaj_typy(kopia), ustawienia(kopia)
    typ = next(t for t in typy if t["typ"] == nowy["typ"])
    rozpoznany, dziennik = klasyfikuj(tekst, typy, ust), []
    return {"rozpoznany": rozpoznany and rozpoznany["typ"], "dane": wyciagnij(tekst, typ, dziennik), "dziennik": dziennik}
