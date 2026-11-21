import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from statistics import harmonic_mean

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from odwolania2json.cli import konsola_utf8
from odwolania2json.pipeline import KONFIG, ROOT, przetworz_wszystkie, ustawienia, wczytaj_typy

UZP = ROOT / "data" / "uzp"
DANE = UZP / "dane"


def liscie(v, sciezka=""):
    if isinstance(v, dict):
        for k, x in v.items():
            yield from liscie(x, f"{sciezka}.{k}" if sciezka else k)
    elif isinstance(v, list):
        for i, x in enumerate(v):
            yield from liscie(x, f"{sciezka}[{i}]")
    else:
        yield sciezka, v


def bez_prefiksu(v, ust: dict):
    b = ust["narzedzia"]["bez_prefiksu"]
    if isinstance(v, dict):
        return {k: x.removeprefix(b["prefiks"]) if k in b["pola"] and isinstance(x, str) else bez_prefiksu(x, ust) for k, x in v.items()}
    if isinstance(v, list):
        return [bez_prefiksu(x, ust) for x in v]
    return v


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


def ocena(katalogi: list[Path], typy: list[dict], ust: dict) -> tuple[float, Counter, Counter, Counter]:
    typ_wzoru = {frozenset(t["szablon"]): t["typ"] for t in typy}
    suma, pola, licznik = Counter(), Counter(), Counter()

    def licz(typ, pary):
        for sciezka, wynik in pary:
            suma[wynik] += 1
            pola[(typ, re.sub(r"\[\d+\]", "[]", sciezka), wynik)] += 1

    for sprawa in sorted(p for dane in katalogi for p in dane.iterdir() if p.is_dir()):
        nasze = {}
        for _, wynik, blad in przetworz_wszystkie(sorted(sprawa.glob("*.pdf")), typy, ust):
            licznik["bledy"] += blad is not None
            if wynik:
                nasze.setdefault(wynik[0], []).append(wynik[1])
        wzory = sorted(sprawa.glob("*.json"))
        if not wzory:
            licznik["obce"] += len(list(sprawa.glob("*.pdf")))
            licznik["obce_z_json"] += sum(map(len, nasze.values()))
            continue
        for plik in wzory:
            wzor = json.loads(plik.read_text(encoding="utf-8"))
            typ = typ_wzoru.get(frozenset(wzor), plik.stem)
            nasz = nasze[typ].pop(0) if nasze.get(typ) else {}
            licznik["dokumenty"] += 1
            licznik["trafione_typy"] += bool(nasz)
            licz(typ, porownaj(bez_prefiksu(wzor, ust), bez_prefiksu(nasz, ust)))
        for typ, nadmiarowe in nasze.items():
            for nasz in nadmiarowe:
                licz(typ, porownaj({}, nasz))

    tp, fp, fn = suma["TP"], suma["FP"], suma["FN"]
    f1 = harmonic_mean([tp / (tp + fp), tp / (tp + fn)]) if tp else 0.0
    return f1, suma, pola, licznik


def main() -> int:
    ap = argparse.ArgumentParser(description="F1 na danych treningowych UZP (ADR-0003)")
    ap.add_argument("--dane", type=Path, nargs="+", default=[DANE], help="katalogi ze sprawami (np. skany: dane/skany/*)")
    ap.add_argument("--config", type=Path, default=KONFIG)
    ap.add_argument("--bez-pol", action="store_true", help="tylko wynik, bez listy pól z błędami")
    args = ap.parse_args()
    konsola_utf8()

    ust = ustawienia(args.config)
    f1, suma, pola, licznik = ocena(args.dane, wczytaj_typy(args.config), ust)
    tp, fp, fn = suma["TP"], suma["FP"], suma["FN"]
    miejsca = ust["narzedzia"]["MIEJSCA_F1"]
    print(f"Dokumenty: {licznik['dokumenty']} | typ poprawny: {licznik['trafione_typy']}/{licznik['dokumenty']}")
    print(f"Obce dokumenty z JSON: {licznik['obce_z_json']}/{licznik['obce']}")
    if licznik["bledy"]:
        print(f"Błędy przetwarzania: {licznik['bledy']}")
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
