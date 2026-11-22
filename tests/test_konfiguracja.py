import ast
import json
import re
import shutil

import yaml
from pypdf import PdfReader

from odwolania2json.podglad import miejsce
from odwolania2json.kreator import jako_yaml, pole_z_przykladu, sprobuj, typ_z_formularza
from odwolania2json.pipeline import KONFIG, ROOT, USTAWIENIA, klasyfikuj, przetworz_wszystkie, tekst_pdf, ustawienia, wczytaj_typy

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
    shutil.copy(ROOT / "docs" / "przyklady" / "ogloszenie_ted.yaml", config / "typy")
    pdf = ROOT / "tests" / "dane" / "ted" / "ogloszenie.pdf"
    wzor = json.loads(pdf.with_suffix(".json").read_text(encoding="utf-8"))

    [(_, z_nowym_typem, _)] = przetworz_wszystkie([pdf], wczytaj_typy(config), ustawienia(config))
    [(_, bez_nowego_typu, _)] = przetworz_wszystkie([pdf], wczytaj_typy(), ustawienia())

    assert z_nowym_typem == ("ogloszenie_ted", wzor)
    assert bez_nowego_typu is None


def test_t22_kreator_typu():
    pdf = ROOT / "tests" / "dane" / "ted" / "ogloszenie.pdf"
    wzor = json.loads(pdf.with_suffix(".json").read_text(encoding="utf-8"))
    pola = [{"pole": "OgloszenieTED.cpv", "etykiety": ["Główna klasyfikacja (cpv)"], "rodzaj": "numer / identyfikator"},
            {"pole": "Nabywca.nazwa", "etykiety": ["Oficjalna nazwa"], "rodzaj": "tekst do końca linii"}]
    typ = typ_z_formularza("ogloszenie", "Ogłoszenie TED", ["see the notice", "oficjalna nazwa", "nabywca"], pola,
                           ustawienia()["kreator"]["rodzaje"], wspolne_wykluczenia=False)

    tekst_yaml = jako_yaml(typ)
    wynik = sprobuj(tekst_yaml, tekst_pdf(pdf, ustawienia()))

    assert yaml.safe_load(tekst_yaml) == typ
    assert (wynik["rozpoznany"], wynik["dane"]) == ("ogloszenie", {
        "OgloszenieTED": {"cpv": wzor["OgloszenieTED"]["cpv"]}, "Nabywca": {"nazwa": wzor["Nabywca"]["nazwa"]}})


def test_t26_pole_z_przykladu():
    tekst, ust = tekst_pdf(ROOT / "tests" / "dane" / "ted" / "ogloszenie.pdf", ustawienia()), ustawienia()
    rodzaje = ust["kreator"]["rodzaje"]
    nazwa = "Miejskie Przedsiębiorstwo Wodociągów i Kanalizacji w m. st. Warszawie S.A."

    znalezione = [pole_z_przykladu(pole, wartosc, tekst, rodzaje, ust) for pole, wartosc in
                  [("OgloszenieTED.cpv", "24111900"), ("Nabywca.nazwa", nazwa), ("Nabywca.nip", "1234567890")]]

    assert znalezione == [
        {"pole": "OgloszenieTED.cpv", "etykiety": ["Główna klasyfikacja (cpv)"], "rodzaj": "numer / identyfikator"},
        {"pole": "Nabywca.nazwa", "etykiety": ["Oficjalna nazwa"], "rodzaj": "tekst do końca linii"},
        None]


def _wewnatrz(w: tuple, f: tuple) -> bool:
    (wl, wd, wp, wg), (fl, fd, fp, fg) = w, f
    return fl <= wl and wp <= fp and fd <= wd and wg <= fg


def test_t27_podswietlenie():
    pdf = ROOT / "tests" / "dane" / "ted" / "ogloszenie.pdf"
    strony = [s.extract_text() for s in PdfReader(pdf).pages]

    strona, fragment, wartosc = miejsce(pdf.read_bytes(), "Główna klasyfikacja (cpv): 24111900", "24111900")

    assert "24111900" in strony[strona]
    assert fragment and wartosc
    assert all(any(_wewnatrz(w, f) for f in fragment) for w in wartosc)
    assert miejsce(pdf.read_bytes(), "Nr ref. CEN2604016344389", "CEN2604016344389") is None


def test_t23_inne_pisma_z_akt():
    typy, ust = wczytaj_typy(), ustawienia()
    rozpoznane = {p.stem: (klasyfikuj(p.read_text(encoding="utf-8"), typy, ust) or {}).get("typ")
                  for p in sorted((ROOT / "tests" / "dane" / "pisma").glob("*.txt"))}

    assert rozpoznane and rozpoznane == dict.fromkeys(rozpoznane)
