import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser(description="F1 i klasyfikacja dla kilku wartości jednej liczby z config/ustawienia.yaml")
    ap.add_argument("liczba", help="nazwa z sekcji liczby, np. OKNO_WARTOSCI")
    ap.add_argument("wartosci", nargs="+", type=float)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    for wartosc in args.wartosci:
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "config"
            shutil.copytree(ROOT / "config", config)
            plik = config / "ustawienia.yaml"
            ust = yaml.safe_load(plik.read_text(encoding="utf-8"))
            ust["liczby"][args.liczba] = int(wartosc) if wartosc.is_integer() else wartosc
            plik.write_text(yaml.safe_dump(ust, allow_unicode=True), encoding="utf-8")
            wynik = subprocess.run([sys.executable, str(ROOT / "tools" / "ocena_f1.py"), "--config", str(config),
                                    "--bez-pol"], capture_output=True, text=True, encoding="utf-8").stdout
            print(f"{args.liczba} = {ust['liczby'][args.liczba]}: " + " | ".join(wynik.splitlines()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
