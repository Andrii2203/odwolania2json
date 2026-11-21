import json
import pytest

from odwolania2json.pipeline import ROOT, przetworz, wczytaj_typy

DANE = ROOT / "data" / "uzp" / "dane"

pytestmark = pytest.mark.skipif(not DANE.exists(), reason="brak data/uzp — zob. AGENTS.md")


@pytest.mark.parametrize("sprawa", ["przyklad_17", "przyklad_42"])
def test_t3_przelew(sprawa):
    typ, dane = przetworz(DANE / sprawa / "potwierdzenie_przelewu.pdf", wczytaj_typy())

    assert typ == "przelew"
    assert dane == json.loads((DANE / sprawa / "przelew.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("sprawa", ["przyklad_02", "przyklad_41", "przyklad_44"])
def test_t4_pelnomocnictwo(sprawa):
    typ, dane = przetworz(DANE / sprawa / "pelnomocnictwo.pdf", wczytaj_typy())

    assert typ == "pelnomocnictwo"
    assert dane == json.loads((DANE / sprawa / "pelnomocnictwo.json").read_text(encoding="utf-8"))
