import argparse
import json
import sys
from pathlib import Path

from .pipeline import KONFIG, ROOT, przetworz_wszystkie, ustawienia, wczytaj_typy


def konsola_utf8() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="odwolania2json", description="PDF sprawy odwoławczej → JSON (typy w config/typy/)")
    ap.add_argument("--input", type=Path, default=ROOT / "input")
    ap.add_argument("--output", type=Path, default=ROOT / "output")
    ap.add_argument("--config", type=Path, default=KONFIG)
    args = ap.parse_args(argv)
    konsola_utf8()

    typy, ust = wczytaj_typy(args.config), ustawienia(args.config)
    bledy = 0
    for pdf, wynik, blad in przetworz_wszystkie(sorted(args.input.rglob("*.pdf")), typy, ust):
        wzgledna = pdf.relative_to(args.input)
        typ, dane = wynik or (None, {})
        if blad is not None:
            bledy += 1
            print(f"błąd: {wzgledna.as_posix()}: {type(blad).__name__}: {blad} → {{}}")
        elif typ is None:
            print(f"nieznany typ: {wzgledna} → {{}}")
        else:
            print(f"{wzgledna} → {typ}")
        cel = args.output / wzgledna.with_suffix(".json")
        cel.parent.mkdir(parents=True, exist_ok=True)
        cel.write_text(json.dumps(dane, ensure_ascii=False, indent=ust["liczby"]["WCIECIE_JSON"]), encoding="utf-8")
    if bledy:
        print(f"Błędy: {bledy}. Pozostałe pliki zapisane.")
    return 1 if bledy else 0
