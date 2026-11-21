import json
import pytest

from odwolania2json.pipeline import przetworz, ustawienia, wczytaj_typy, wyciagnij
from tools.ocena_f1 import DANE

pytestmark = pytest.mark.skipif(not DANE.exists(), reason="brak data/uzp — zob. AGENTS.md")


@pytest.mark.parametrize("sprawa", ["przyklad_17", "przyklad_42"])
def test_t3_przelew(sprawa):
    typ, dane = przetworz(DANE / sprawa / "potwierdzenie_przelewu.pdf", wczytaj_typy(), ustawienia())

    assert typ == "przelew"
    assert dane == json.loads((DANE / sprawa / "przelew.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("sprawa", ["przyklad_02", "przyklad_41", "przyklad_44"])
def test_t4_pelnomocnictwo(sprawa):
    typ, dane = przetworz(DANE / sprawa / "pelnomocnictwo.pdf", wczytaj_typy(), ustawienia())

    assert typ == "pelnomocnictwo"
    assert dane == json.loads((DANE / sprawa / "pelnomocnictwo.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("sprawa", ["przyklad_01", "przyklad_03", "przyklad_41"])
def test_t6_odwolanie(sprawa):
    typ, dane = przetworz(DANE / sprawa / "odwolanie.pdf", wczytaj_typy(), ustawienia())

    assert typ == "odwolanie"
    assert dane == json.loads((DANE / sprawa / "odwolanie.json").read_text(encoding="utf-8"))


def test_t10_etykieta_nie_jest_wartoscia():
    typ = next(t for t in wczytaj_typy() if t["typ"] == "przelew")

    dane = wyciagnij("Data Opis Kwota\nData operacji 2026-04-09\nTytuł: opłata skarbowa od pełnomocnictwa\n", typ)

    assert dane["przelew_bankowy"]["tytul"] == "opłata skarbowa od pełnomocnictwa"
