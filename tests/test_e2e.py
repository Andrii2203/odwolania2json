import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from odwolania2json import pipeline
from odwolania2json.pipeline import KONFIG, ROOT, przetworz_wszystkie, ustawienia, wczytaj_typy
from tools.ocena_f1 import DANE, UZP, ocena

pytestmark = pytest.mark.skipif(not UZP.exists(), reason="brak data/uzp — zob. AGENTS.md")


def run_cli(inp: Path, out: Path, *dodatkowe: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "odwolania2json", "--input", str(inp), "--output", str(out), *dodatkowe],
        cwd=ROOT, check=check, capture_output=True, text=True, encoding="utf-8",
    )


def test_t1_sprawa_trzy_dokumenty(tmp_path):
    for case in sorted(DANE.glob("przyklad_*")):
        shutil.copytree(case, tmp_path / "input" / case.name, ignore=shutil.ignore_patterns("*.json"))

    run_cli(tmp_path / "input", tmp_path / "output")

    def klucze(pliki):
        return sorted(sorted(json.loads(p.read_text(encoding="utf-8"))) for p in pliki)

    wrong = []
    for case in sorted((tmp_path / "input").iterdir()):
        out = tmp_path / "output" / case.name
        if {p.stem for p in out.glob("*.json")} != {p.stem for p in case.glob("*.pdf")}:
            wrong.append(f"{case.name}: nazwy")
        elif [k for k in klucze(out.glob("*.json")) if k] != klucze((DANE / case.name).glob("*.json")):
            wrong.append(f"{case.name}: klucze")
    assert wrong == []


def test_t2_obcy_dokument(tmp_path):
    case = tmp_path / "input" / "negatywne"
    shutil.copytree(DANE / "negatywne", case, ignore=shutil.ignore_patterns("*.md"))
    shutil.copy(UZP / "szablon-aplikacja" / "input" / "case1" / "negatywny przyklad.pdf", case)

    run_cli(tmp_path / "input", tmp_path / "output")

    pdfy = sorted(p.stem for p in case.glob("*.pdf"))
    jsony = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in (tmp_path / "output").rglob("*.json")}
    assert (sorted(jsony), set(map(str, jsony.values()))) == (pdfy, {"{}"})


def test_t7_blad_jednego_dokumentu(tmp_path):
    config = tmp_path / "config"
    shutil.copytree(KONFIG, config)
    plik_typu = config / "typy" / "przelew.yaml"
    typ = yaml.safe_load(plik_typu.read_text(encoding="utf-8"))
    typ["pola"]["przelew_bankowy.kwota"] = {"wzorce": ["([A-Za-z]+)"], "format": "liczba"}
    plik_typu.write_text(yaml.safe_dump(typ, allow_unicode=True), encoding="utf-8")
    shutil.copytree(DANE / "przyklad_01", tmp_path / "input" / "przyklad_01", ignore=shutil.ignore_patterns("*.json"))

    wynik = run_cli(tmp_path / "input", tmp_path / "output", "--config", str(config), check=False)

    assert wynik.returncode == 1
    assert "błąd: przyklad_01" in wynik.stdout
    wyjscie = tmp_path / "output" / "przyklad_01"
    assert sorted(p.name for p in wyjscie.glob("*.json")) == ["odwolanie.json", "pelnomocnictwo.json", "przelew.json"]
    assert json.loads((wyjscie / "przelew.json").read_text(encoding="utf-8")) == {}


def test_t8_f1_nie_spada():
    f1, *_ = ocena([DANE], wczytaj_typy(), ustawienia())

    assert f1 >= ustawienia()["narzedzia"]["MIN_F1"]


def test_t9_skany(tmp_path):
    for typ in ("potwierdzenia", "pelnomocnictwa", "odwolania"):
        shutil.copytree(DANE / "skany" / typ / "0001", tmp_path / typ)

    f1, _, _, licznik = ocena([tmp_path], wczytaj_typy(), ustawienia())

    assert licznik["trafione_typy"] == licznik["dokumenty"]
    assert f1 >= ustawienia()["narzedzia"]["MIN_F1_SKANY"]


def test_t12_wyjasnij(tmp_path):
    shutil.copy(DANE / "przyklad_01" / "przelew.pdf", (tmp_path / "input" / "przyklad_01").mkdir(parents=True) or tmp_path / "input" / "przyklad_01")

    zwykly = run_cli(tmp_path / "input", tmp_path / "zwykly")
    wynik = run_cli(tmp_path / "input", tmp_path / "output", "--wyjasnij")

    linie = wynik.stdout.splitlines()
    i = next(n for n, linia in enumerate(linie) if "przelew_bankowy.kwota = 200.0" in linia)
    _, regula, fragment, *_ = linie[i:]
    assert "reguła:" in regula and "200,00" in fragment
    sciezka = Path("przyklad_01") / "przelew.json"
    assert (tmp_path / "output" / sciezka).read_text(encoding="utf-8") == (tmp_path / "zwykly" / sciezka).read_text(encoding="utf-8")
    assert zwykly.returncode == 0


def test_t16_zapis_zaraz(tmp_path, monkeypatch):
    for pdf in sorted((DANE / "przyklad_01").glob("*.pdf")):
        shutil.copy(pdf, tmp_path)
    zdarzenia, tekst_pdf = [], pipeline.tekst_pdf
    monkeypatch.setattr(pipeline, "tekst_pdf", lambda pdf, *a, **k: zdarzenia.append(("tekst", pdf.stem)) or tekst_pdf(pdf, *a, **k))
    zaraz = lambda pdf, wynik, blad: zdarzenia.append(("zapis", pdf.stem))

    for pdf, _, _ in przetworz_wszystkie(sorted(tmp_path.glob("*.pdf")), wczytaj_typy(), ustawienia(), zaraz=zaraz):
        zdarzenia.append(("wynik", pdf.stem))

    nazwy = ["odwolanie", "pelnomocnictwo", "przelew"]
    assert zdarzenia == [z for n in nazwy for z in (("tekst", n), ("zapis", n))] + [("wynik", n) for n in nazwy]


def test_t17_limit_czasu(tmp_path):
    shutil.copy(DANE / "skany" / "potwierdzenia" / "0001" / "0001.pdf", tmp_path)
    ust = ustawienia()
    ust["liczby"]["CZAS_OCR_S"] = 0
    dzienniki = {}

    [(pdf, wynik, blad)] = przetworz_wszystkie([tmp_path / "0001.pdf"], wczytaj_typy(), ust, dzienniki)

    assert (wynik, blad) == (None, None)
    assert "OCR pominięty: limit czasu" in [w["regula"] for w in dzienniki[pdf]]
