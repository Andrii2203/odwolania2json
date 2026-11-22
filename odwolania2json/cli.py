import argparse
import json
import sys
from collections.abc import Iterator
from pathlib import Path

from .pipeline import KONFIG, ROOT, przetworz_wszystkie, ustawienia, wczytaj_typy


def konsola_utf8() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def _puste(v, sciezka: str = "") -> Iterator[str]:
    if isinstance(v, dict):
        for k, x in v.items():
            yield from _puste(x, f"{sciezka}.{k}" if sciezka else k)
    elif isinstance(v, list):
        for i, x in enumerate(v):
            yield from _puste(x, f"{sciezka}[{i}]")
    elif v is None:
        yield sciezka


def wyjasnij(dane: dict, dziennik: list[dict]) -> None:
    for wpis in dziennik:
        print(f"  {wpis['pole']} = {wpis['wartosc']!r}")
        print(f"      reguła: {wpis['regula']}")
        print(f"      tekst:  „{wpis['fragment']}”")
    print(f"  puste: {', '.join(_puste(dane)) or '(brak)'}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="odwolania2json", description="PDF sprawy odwoławczej → JSON (typy w config/typy/)")
    ap.add_argument("--input", type=Path, default=ROOT / "input")
    ap.add_argument("--output", type=Path, default=ROOT / "output")
    ap.add_argument("--config", type=Path, default=KONFIG)
    ap.add_argument("--wyjasnij", action="store_true", help="dla każdego pola pokaż regułę i fragment tekstu (nie trafia do output)")
    args = ap.parse_args(argv)
    konsola_utf8()

    typy, ust = wczytaj_typy(args.config), ustawienia(args.config)
    bledy, dzienniki = 0, {} if args.wyjasnij else None

    def zapisz(pdf: Path, wynik, blad) -> None:
        cel = args.output / pdf.relative_to(args.input).with_suffix(".json")
        cel.parent.mkdir(parents=True, exist_ok=True)
        dane = wynik[1] if wynik else {}
        cel.write_text(json.dumps(dane, ensure_ascii=False, indent=ust["liczby"]["WCIECIE_JSON"]), encoding="utf-8")

    for pdf, wynik, blad in przetworz_wszystkie(sorted(args.input.rglob("*.pdf")), typy, ust, dzienniki, zapisz):
        wzgledna = pdf.relative_to(args.input)
        typ, dane = wynik or (None, {})
        if blad is not None:
            bledy += 1
            print(f"błąd: {wzgledna.as_posix()}: {type(blad).__name__}: {blad} → {{}}")
        elif typ is None:
            print(f"nieznany typ: {wzgledna} → {{}}")
        else:
            print(f"{wzgledna} → {typ}")
        if dzienniki is not None and typ is not None:
            wyjasnij(dane, dzienniki.get(pdf, []))
        zapisz(pdf, wynik, blad)
    if bledy:
        print(f"Błędy: {bledy}. Pozostałe pliki zapisane.")
    return 1 if bledy else 0
