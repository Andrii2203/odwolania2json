import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from statistics import harmonic_mean

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from odwolania2json.cli import konsola_utf8
from odwolania2json.pipeline import KONFIG, ROOT, przetworz, ustawienia, wczytaj_typy


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
    ap.add_argument("--config", type=Path, default=KONFIG)
    ap.add_argument("--bez-pol", action="store_true", help="tylko wynik, bez listy pól z błędami")
    args = ap.parse_args()
    konsola_utf8()

    typy = wczytaj_typy(args.config)
    typ_wzoru = {frozenset(t["szablon"]): t["typ"] for t in typy}
    suma, pola = Counter(), Counter()
    dokumenty = trafione_typy = obce = obce_z_json = 0

    def licz(typ, pary):
        for sciezka, wynik in pary:
            suma[wynik] += 1
            pola[(typ, re.sub(r"\[\d+\]", "[]", sciezka), wynik)] += 1

    for sprawa in sorted(p for p in args.dane.iterdir() if p.is_dir()):
        nasze = {}
        for pdf in sorted(sprawa.glob("*.pdf")):
            if wynik := przetworz(pdf, typy):
                nasze.setdefault(wynik[0], []).append(wynik[1])
        wzory = sorted(sprawa.glob("*.json"))
        if not wzory:
            obce += len(list(sprawa.glob("*.pdf")))
            obce_z_json += sum(map(len, nasze.values()))
            continue
        for plik in wzory:
            wzor = json.loads(plik.read_text(encoding="utf-8"))
            typ = typ_wzoru.get(frozenset(wzor), plik.stem)
            nasz = nasze[typ].pop(0) if nasze.get(typ) else {}
            dokumenty += 1
            trafione_typy += bool(nasz)
            licz(typ, porownaj(wzor, nasz))
        for typ, nadmiarowe in nasze.items():
            for nasz in nadmiarowe:
                licz(typ, porownaj({}, nasz))

    tp, fp, fn = suma["TP"], suma["FP"], suma["FN"]
    f1 = harmonic_mean([tp / (tp + fp), tp / (tp + fn)]) if tp else 0.0
    miejsca = ustawienia(args.config)["narzedzia"]["MIEJSCA_F1"]
    print(f"Dokumenty: {dokumenty} | typ poprawny: {trafione_typy}/{dokumenty}")
    print(f"Obce dokumenty z JSON: {obce_z_json}/{obce}")
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
