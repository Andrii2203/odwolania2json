import json
from pathlib import Path

import pytest

from odwolania2json.pipeline import load_types, process

ROOT = Path(__file__).resolve().parents[1]
DANE = ROOT / "data" / "uzp" / "dane"

pytestmark = pytest.mark.skipif(not DANE.exists(), reason="brak data/uzp — zob. AGENTS.md")


@pytest.mark.parametrize("sprawa", ["przyklad_17", "przyklad_42"])
def test_t3_przelew(sprawa):
    typ, dane = process(DANE / sprawa / "potwierdzenie_przelewu.pdf", load_types(ROOT / "config" / "typy"))

    assert typ == "przelew"
    assert dane == json.loads((DANE / sprawa / "przelew.json").read_text(encoding="utf-8"))
