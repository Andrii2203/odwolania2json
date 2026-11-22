import ast
import re

import shutil

from odwolania2json.pipeline import KONFIG, ROOT, USTAWIENIA, dokument_z_tekstu, ustawienia, wczytaj_typy

KWANTYFIKATOR = re.compile(r"\{\d+(?:,\d*)?\}")


def _liczba(w: ast.AST) -> bool:
    if isinstance(w, ast.Constant) and type(w.value) in (int, float):
        return w.value not in (0, 1)
    if isinstance(w, ast.Constant) and isinstance(w.value, str):
        return bool(KWANTYFIKATOR.search(w.value))
    return isinstance(w, ast.FormattedValue) and w.format_spec is not None and bool(re.search(r"\d", ast.unparse(w.format_spec)))


def test_t5_liczby_w_jednym_pliku():
    typy_z_cyframi = [p.name for p in (KONFIG / "typy").glob("*.yaml")
                      if re.search(r"\d", p.read_text(encoding="utf-8"))]

    liczby_w_kodzie = [f"{p.relative_to(ROOT).as_posix()}:{w.lineno} {ast.unparse(w)}"
                       for katalog in ("odwolania2json", "tools", "tests") for p in (ROOT / katalog).rglob("*.py")
                       for w in ast.walk(ast.parse(p.read_text(encoding="utf-8"))) if _liczba(w)]

    linie = (KONFIG / USTAWIENIA).read_text(encoding="utf-8").splitlines()
    bez_pochodzenia = [linia for i, linia in enumerate(linie)
                       if re.search(r"\d", linia) and not linia.lstrip().startswith("#") and " #" not in linia
                       and not (i and linie[i - 1].lstrip().startswith("#"))]

    assert (typy_z_cyframi, liczby_w_kodzie, bez_pochodzenia) == ([], [], [])


def test_t21_nowy_typ_z_yaml(tmp_path):
    config = tmp_path / "config"
    shutil.copytree(KONFIG, config)
    shutil.copy(ROOT / "docs" / "przyklady" / "wezwanie.yaml", config / "typy")
    tekst = ("Gdańsk, dnia 12 maja 2026 r.\nZnak sprawy: ZP.271.4.2026\nWykonawca:\n"
             "Budex Serwis sp. z o.o., ul. Długa 5, 80-001 Gdańsk\nNIP: 999-123-45-67\n"
             "WEZWANIE DO UZUPEŁNIENIA DOKUMENTÓW\nZamawiający wzywa Wykonawcę do uzupełnienia dokumentów w postępowaniu "
             "o udzielenie zamówienia publicznego w terminie do dnia 19 maja 2026 r.\n")

    d = dokument_z_tekstu(tekst, wczytaj_typy(config), ustawienia(config), [])

    assert (d["typ"], d["dane"]) == ("wezwanie", {
        "Wezwanie": {"data": "2026-05-12", "miejscowosc": "Gdańsk", "numer_postepowania": "ZP.271.4.2026", "termin": "2026-05-19"},
        "Wykonawca": {"nazwa": "Budex Serwis sp. z o.o.", "nip": "9991234567"}})
