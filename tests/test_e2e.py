import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from odwolania2json.pipeline import KONFIG, ROOT, ustawienia, wczytaj_typy
from tools.ocena_f1 import ocena

UZP = ROOT / "data" / "uzp"

pytestmark = pytest.mark.skipif(not UZP.exists(), reason="brak data/uzp — zob. AGENTS.md")


def run_cli(inp: Path, out: Path, *dodatkowe: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "odwolania2json", "--input", str(inp), "--output", str(out), *dodatkowe],
        cwd=ROOT, check=check, capture_output=True, text=True, encoding="utf-8",
    )


def test_t1_sprawa_trzy_dokumenty(tmp_path):
    for case in sorted((UZP / "dane").glob("przyklad_*")):
        shutil.copytree(case, tmp_path / "input" / case.name, ignore=shutil.ignore_patterns("*.json"))

    run_cli(tmp_path / "input", tmp_path / "output")

    def klucze(pliki):
        return sorted(sorted(json.loads(p.read_text(encoding="utf-8"))) for p in pliki)

    wrong = []
    for case in sorted((tmp_path / "input").iterdir()):
        out = tmp_path / "output" / case.name
        if not {p.stem for p in out.glob("*.json")} <= {p.stem for p in case.glob("*.pdf")}:
            wrong.append(f"{case.name}: nazwy")
        elif klucze(out.glob("*.json")) != klucze((UZP / "dane" / case.name).glob("*.json")):
            wrong.append(f"{case.name}: klucze")
    assert wrong == []


def test_t2_obcy_dokument(tmp_path):
    case = tmp_path / "input" / "negatywne"
    shutil.copytree(UZP / "dane" / "negatywne", case, ignore=shutil.ignore_patterns("*.md"))
    shutil.copy(UZP / "szablon-aplikacja" / "input" / "case1" / "negatywny przyklad.pdf", case)

    run_cli(tmp_path / "input", tmp_path / "output")

    assert sorted(p.name for p in (tmp_path / "output").rglob("*.json")) == []


def test_t7_blad_jednego_dokumentu(tmp_path):
    config = tmp_path / "config"
    shutil.copytree(KONFIG, config)
    plik_typu = config / "typy" / "przelew.yaml"
    typ = yaml.safe_load(plik_typu.read_text(encoding="utf-8"))
    typ["pola"]["przelew_bankowy.kwota"] = {"wzorce": ["([A-Za-z]+)"], "format": "liczba"}
    plik_typu.write_text(yaml.safe_dump(typ, allow_unicode=True), encoding="utf-8")
    shutil.copytree(UZP / "dane" / "przyklad_01", tmp_path / "input" / "przyklad_01", ignore=shutil.ignore_patterns("*.json"))

    wynik = run_cli(tmp_path / "input", tmp_path / "output", "--config", str(config), check=False)

    assert wynik.returncode == 1
    assert "błąd: przyklad_01" in wynik.stdout
    assert sorted(p.name for p in (tmp_path / "output" / "przyklad_01").glob("*.json")) == ["odwolanie.json", "pelnomocnictwo.json"]


def test_t8_f1_nie_spada():
    f1, *_ = ocena(UZP / "dane", wczytaj_typy())

    assert f1 >= ustawienia()["narzedzia"]["MIN_F1"]
