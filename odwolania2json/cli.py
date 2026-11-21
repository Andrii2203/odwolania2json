import argparse
import json
import sys
from pathlib import Path

from .pipeline import KONFIG, ROOT, przetworz, ustawienia, wczytaj_typy


def konsola_utf8() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="odwolania2json", description="PDF sprawy odwoławczej → JSON (typy w config/typy/)")
    ap.add_argument("--input", type=Path, default=ROOT / "input")
    ap.add_argument("--output", type=Path, default=ROOT / "output")
    ap.add_argument("--config", type=Path, default=KONFIG)
    args = ap.parse_args(argv)
    konsola_utf8()

    typy, wciecie = wczytaj_typy(args.config), ustawienia(args.config)["liczby"]["WCIECIE_JSON"]
    for pdf in sorted(args.input.rglob("*.pdf")):
        wzgledna = pdf.relative_to(args.input)
        wynik = przetworz(pdf, typy)
        if wynik is None:
            print(f"pominięto (nieznany typ): {wzgledna}")
            continue
        typ, dane = wynik
        cel = args.output / wzgledna.with_suffix(".json")
        cel.parent.mkdir(parents=True, exist_ok=True)
        cel.write_text(json.dumps(dane, ensure_ascii=False, indent=wciecie), encoding="utf-8")
        print(f"{wzgledna} → {typ}")
    return 0
