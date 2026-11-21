import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
UZP = ROOT / "data" / "uzp"

pytestmark = pytest.mark.skipif(not UZP.exists(), reason="brak data/uzp — zob. AGENTS.md")


def run_cli(inp: Path, out: Path) -> None:
    subprocess.run(
        [sys.executable, "-m", "odwolania2json", "--input", str(inp), "--output", str(out)],
        cwd=ROOT, check=True,
    )


def test_t1_sprawa_trzy_dokumenty(tmp_path):
    for case in sorted((UZP / "dane").glob("przyklad_*")):
        shutil.copytree(case, tmp_path / "input" / case.name, ignore=shutil.ignore_patterns("*.json"))

    run_cli(tmp_path / "input", tmp_path / "output")

    expected = {
        "odwolanie.json": "OdwolanieKIO",
        "pelnomocnictwo.json": "mocodawca",
        "potwierdzenie_przelewu.json": "przelew_bankowy",
    }
    wrong = []
    for case in sorted((tmp_path / "input").iterdir()):
        for name, key in expected.items():
            out = tmp_path / "output" / case.name / name
            if not out.exists() or key not in json.loads(out.read_text(encoding="utf-8")):
                wrong.append(f"{case.name}/{name}")
    assert wrong == []


def test_t2_obcy_dokument(tmp_path):
    case = tmp_path / "input" / "negatywne"
    shutil.copytree(UZP / "dane" / "negatywne", case, ignore=shutil.ignore_patterns("*.md"))
    shutil.copy(UZP / "szablon-aplikacja" / "input" / "case1" / "negatywny przyklad.pdf", case)

    run_cli(tmp_path / "input", tmp_path / "output")

    assert sorted(p.name for p in (tmp_path / "output").rglob("*.json")) == []
