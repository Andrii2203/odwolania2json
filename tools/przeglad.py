import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from odwolania2json.cli import konsola_utf8
from odwolania2json.pipeline import KONFIG, ROOT, USTAWIENIA, ustawienia


def main() -> int:
    ap = argparse.ArgumentParser(description="F1 i klasyfikacja dla kilku wartości jednej liczby z config/ustawienia.yaml")
    ap.add_argument("liczba", help="nazwa z sekcji liczby, np. OKNO_WARTOSCI")
    ap.add_argument("wartosci", nargs="+", type=float)
    ap.add_argument("--dane", nargs="+", default=[], help="katalogi dla ocena_f1.py (domyślnie dane treningowe)")
    args = ap.parse_args()
    konsola_utf8()

    for wartosc in args.wartosci:
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "config"
            shutil.copytree(KONFIG, config)
            ust = ustawienia(config)
            ust["liczby"][args.liczba] = int(wartosc) if wartosc.is_integer() else wartosc
            (config / USTAWIENIA).write_text(yaml.safe_dump(ust, allow_unicode=True), encoding="utf-8")
            dane = ["--dane", *args.dane] if args.dane else []
            wynik = subprocess.run([sys.executable, str(ROOT / "tools" / "ocena_f1.py"), "--config", str(config),
                                    "--bez-pol", *dane], capture_output=True, text=True, encoding="utf-8").stdout
            print(f"{args.liczba} = {ust['liczby'][args.liczba]}: " + " | ".join(wynik.splitlines()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
