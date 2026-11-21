import argparse
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from statistics import harmonic_mean

import yaml

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
    ap.add_argument("--config", type=Path, default=ROOT / "config")
    ap.add_argument("--bez-pol", action="store_true", help="tylko wynik, bez listy pól z błędami")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    with tempfile.TemporaryDirectory() as tmp:
        wyjscie = Path(tmp)
        subprocess.run([sys.executable, "-m", "odwolania2json", "--input", str(args.dane),
                        "--output", str(wyjscie), "--config", str(args.config)], cwd=ROOT, check=True, capture_output=True)
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
        obce = list(args.dane.glob("negatywne/*.pdf"))
        obce_z_json = sum((wyjscie / "negatywne" / p.with_suffix(".json").name).exists() for p in obce)

    tp, fp, fn = suma["TP"], suma["FP"], suma["FN"]
    f1 = harmonic_mean([tp / (tp + fp), tp / (tp + fn)]) if tp else 0.0
    miejsca = yaml.safe_load((args.config / "ustawienia.yaml").read_text(encoding="utf-8"))["narzedzia"]["MIEJSCA_F1"]
    print(f"Dokumenty: {dokumenty} | typ poprawny: {trafione_typy}/{dokumenty}")
    print(f"Obce dokumenty z JSON: {obce_z_json}/{len(obce)}")
    print(f"F1 = {f1:.{miejsca}f}  (TP {tp} | FP {fp} | FN {fn})")
    bledy = Counter()
    for (typ, pole, wynik), ile in pola.items():
        if wynik != "TP":
            bledy[(typ, pole)] += ile
    if args.bez_pol or not bledy:
        return 0
    szer_typu, szer_pola = (max(len(klucz[i]) for klucz in bledy) for i in (0, 1))
    szer_liczby = len(str(max(pola.values())))
    print("Pola z błędami (FN+FP), od najgorszego:")
    for (typ, pole), ile in bledy.most_common():
        fn_pola, fp_pola = pola[(typ, pole, "FN")], pola[(typ, pole, "FP")]
        print(f"  {typ:<{szer_typu}}  {pole:<{szer_pola}}  FN {fn_pola:>{szer_liczby}}  FP {fp_pola:>{szer_liczby}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
