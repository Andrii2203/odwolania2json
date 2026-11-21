import argparse
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WZORZEC = {"odwolanie": "odwolanie.json", "pelnomocnictwo": "pelnomocnictwo.json",
           "potwierdzenie_przelewu": "przelew.json"}


def liscie(v, sciezka=""):
    if isinstance(v, dict):
        for k, x in v.items():
            yield from liscie(x, f"{sciezka}.{k}" if sciezka else k)
    elif isinstance(v, list):
        for i, x in enumerate(v):
            yield from liscie(x, f"{sciezka}[{i}]")
    else:
        yield sciezka, v


def porownaj(wzor, nasz):
    w, n = dict(liscie(wzor)), dict(liscie(nasz))
    for sciezka in w.keys() | n.keys():
        a, b = w.get(sciezka), n.get(sciezka)
        if a is None and b is None:
            continue
        if a is not None and a == b and type(a) is type(b):
            yield sciezka, "TP"
            continue
        if a is not None:
            yield sciezka, "FN"
        if b is not None:
            yield sciezka, "FP"


def main() -> int:
    ap = argparse.ArgumentParser(description="F1 na danych treningowych UZP (ADR-0003)")
    ap.add_argument("--dane", type=Path, default=ROOT / "data" / "uzp" / "dane")
    ap.add_argument("--top", type=int, default=12)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    with tempfile.TemporaryDirectory() as tmp:
        wyjscie = Path(tmp)
        subprocess.run([sys.executable, "-m", "odwolania2json", "--input", str(args.dane),
                        "--output", str(wyjscie)], cwd=ROOT, check=True, capture_output=True)
        suma, pola = Counter(), Counter()
        dokumenty = trafione_typy = 0
        for sprawa in sorted(p for p in args.dane.iterdir() if all((p / n).exists() for n in WZORZEC.values())):
            for nazwa_pdf, nazwa_wzoru in WZORZEC.items():
                wzor = json.loads((sprawa / nazwa_wzoru).read_text(encoding="utf-8"))
                plik = wyjscie / sprawa.name / f"{nazwa_pdf}.json"
                nasz = json.loads(plik.read_text(encoding="utf-8")) if plik.exists() else {}
                dokumenty += 1
                trafione_typy += nasz.keys() == wzor.keys()
                for sciezka, wynik in porownaj(wzor, nasz):
                    suma[wynik] += 1
                    pola[(nazwa_pdf, re.sub(r"\[\d+\]", "[]", sciezka), wynik)] += 1

    tp, fp, fn = suma["TP"], suma["FP"], suma["FN"]
    f1 = 2 * tp / (2 * tp + fp + fn) if tp + fp + fn else 0.0
    print(f"Dokumenty: {dokumenty} | typ poprawny: {trafione_typy}/{dokumenty}")
    print(f"F1 = {f1:.3f}  (TP {tp} | FP {fp} | FN {fn})")
    bledy = Counter()
    for (typ, pole, wynik), ile in pola.items():
        if wynik != "TP":
            bledy[(typ, pole)] += ile
    print("Najgorsze pola (FN+FP):")
    for (typ, pole), ile in bledy.most_common(args.top):
        print(f"  {typ:<22} {pole:<45} FN {pola[(typ, pole, 'FN')]:>3}  FP {pola[(typ, pole, 'FP')]:>3}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
