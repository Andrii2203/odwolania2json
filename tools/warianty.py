import argparse
import json
import random
import re
import string
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from odwolania2json.cli import konsola_utf8
from odwolania2json.kontekst import cyfry_w_tekscie
from odwolania2json.pipeline import KONFIG, dokument_z_tekstu, kontekst_sprawy, tekst_pdf, ustawienia, wczytaj_typy
from ocena_f1 import DANE, bez_prefiksu, liscie, miara_f1, pole_ogolne, porownaj, typy_wzorow

def _mapuj(v, f):
    if isinstance(v, dict):
        return {k: _mapuj(x, f) for k, x in v.items()}
    if isinstance(v, list):
        return [_mapuj(x, f) for x in v]
    return f(v) if isinstance(v, str) else v


def _napisy(wzor) -> list[tuple[str, str]]:
    return [(s, v) for s, v in liscie(wzor) if isinstance(v, str)]


def _cyfry_w_tekscie(cyfry: str, ust: dict) -> re.Pattern:
    return cyfry_w_tekscie(cyfry, ust["wzorce"]["ROZDZIELNIK_CYFR"])


def _podmien_cyfry(stare: str, nowe: str) -> str:
    cyfry = iter(nowe)
    return re.sub(r"\d", lambda _: next(cyfry), stare)


def _data(s: str) -> date | None:
    try:
        return date.fromisoformat(s)
    except ValueError:
        return None


def _przebiegi(tekst: str, wzor, w: dict, ust: dict) -> list[str]:
    runy = {r for _, v in _napisy(wzor) for r in re.findall(r"\d+", v) if len(r) >= w["MIN_CYFR"]}
    return sorted(r for r in runy if _cyfry_w_tekscie(r, ust).search(tekst))


def wartosci(tekst, wzor, rng, w, ust):
    zamiana = {}
    for r in _przebiegi(tekst, wzor, w, ust):
        nowy = "".join(rng.choice(string.digits) for _ in r)
        zamiana[r] = nowy
        tekst = _cyfry_w_tekscie(r, ust).sub(lambda m: _podmien_cyfry(m[0], nowy), tekst)
    return tekst, _mapuj(wzor, lambda s: re.sub(r"\d+", lambda m: zamiana.get(m[0], m[0]), s))


def braki(tekst, wzor, rng, w, ust):
    r = rng.choice(_przebiegi(tekst, wzor, w, ust) or [None])
    if r is None:
        return None
    tekst = _cyfry_w_tekscie(r, ust).sub(rng.choice(w["braki"]), tekst)
    return tekst, _mapuj(wzor, lambda s: None if r in s else s)


def nazwy(tekst, wzor, rng, w, ust):
    znane = set(re.findall(r"\w+", w["konfiguracja"]))
    slowa = {s for sciezka, v in _napisy(wzor) if sciezka.endswith(w["pole_nazwy"]) for s in re.findall(r"\w+", v)
             if s.isalpha() and s[0].isupper() and s.lower() not in znane}
    zamiana = {}
    for s in sorted(slowa):
        litery = list(s.lower())
        rng.shuffle(litery)
        nowe = "".join(litery)
        zamiana[s] = nowe.upper() if s.isupper() else nowe.capitalize()
        zamiana[s.upper()] = nowe.upper()
    if not zamiana:
        return None
    wzorzec = re.compile(r"\b(" + "|".join(map(re.escape, sorted(zamiana, key=len, reverse=True))) + r")\b")
    zamien = lambda s: wzorzec.sub(lambda m: zamiana[m[0]], s)
    return zamien(tekst), _mapuj(wzor, zamien)


def daty(tekst, wzor, rng, w, ust):
    stare = sorted({v for _, v in _napisy(wzor) if "-" in v and _data(v)})
    przesun = timedelta(days=rng.randint(-w["ZAKRES_DNI"], w["ZAKRES_DNI"]))
    miesiace = ust["miesiace"]

    def zapisy(d: date) -> list[str]:
        cyfrowe = [d.strftime(f) for f in ust["formaty_daty"]]
        return cyfrowe + [f"{d.day} {miesiace[d.month - 1]} {d.year}", d.strftime("%d ") + f"{miesiace[d.month - 1]} {d.year}"]

    zamiana, nowy_tekst = {}, tekst
    for s in stare:
        d = date.fromisoformat(s)
        for a, b in zip(zapisy(d), zapisy(d + przesun)):
            if re.search(rf"(?<!\d){re.escape(a)}(?!\d)", nowy_tekst):
                nowy_tekst = re.sub(rf"(?<!\d){re.escape(a)}(?!\d)", b, nowy_tekst)
                zamiana[s] = (d + przesun).isoformat()
    if not zamiana:
        return None
    return nowy_tekst, _mapuj(wzor, lambda s: zamiana.get(s, s))


def laczenie_linii(tekst, wzor, rng, w, ust):
    return re.sub(r"\n", lambda m: " " if rng.random() < w["P_LACZENIA"] else "\n", tekst), wzor


def lamanie_linii(tekst, wzor, rng, w, ust):
    szerokosc = int(max(map(len, tekst.splitlines())) * w["CZESC_SZEROKOSCI"])
    linie = []
    for linia in tekst.splitlines():
        while len(linia) > szerokosc and (ciecie := linia.rfind(" ", 0, szerokosc)) > 0:
            linie.append(linia[:ciecie])
            linia = linia[ciecie + 1:]
        linie.append(linia)
    return "\n".join(linie), wzor


LOSOWE = {"wartosci": wartosci, "braki": braki, "nazwy": nazwy, "daty": daty,
          "laczenie_linii": laczenie_linii, "lamanie_linii": lamanie_linii}


def etykiety(tekst, w):
    for wzorzec, zamiany in w["etykiety"].items():
        if re.search(wzorzec, tekst, re.MULTILINE):
            for z in zamiany:
                yield f"etykieta {wzorzec} -> {z}", re.sub(wzorzec, z.replace("\\", "\\\\"), tekst, flags=re.MULTILINE)


def bloki(tekst, w):
    for naglowki in w["bloki"]:
        poz = [m.start() for n in naglowki if (m := re.search(n, tekst, re.MULTILINE))]
        if len(poz) == len(naglowki) and poz == sorted(poz):
            czesci = [tekst[a:b] for a, b in zip(poz, poz[1:])]
            yield f"bloki {' / '.join(naglowki[:-1])}", tekst[:poz[0]] + "".join(reversed(czesci)) + tekst[poz[-1]:]


def warianty(tekst, wzor, pdf, w, ust):
    for rodzaj, f in LOSOWE.items():
        for k in range(w["WARIANTY"]):
            wynik = f(tekst, wzor, random.Random(f"{pdf.as_posix()}|{rodzaj}|{k}"), w, ust)
            if wynik:
                yield rodzaj, *wynik
    for rodzaj, t in [*etykiety(tekst, w), *bloki(tekst, w)]:
        yield rodzaj, t, wzor


def main() -> int:
    ap = argparse.ArgumentParser(description="F1 na wariantach dokumentów treningowych (ADR-0011)")
    ap.add_argument("--dane", type=Path, nargs="+", default=[DANE])
    ap.add_argument("--config", type=Path, default=KONFIG)
    ap.add_argument("--przyklady", action="store_true", help="dla najgorszych pól pokaż jeden przykład")
    args = ap.parse_args()
    konsola_utf8()
    ust = ustawienia(args.config)
    typy = wczytaj_typy(args.config)
    w = ust["narzedzia"]["warianty"]
    w["konfiguracja"] = " ".join(p.read_text(encoding="utf-8") for p in args.config.rglob("*.yaml")).lower()
    typ_wzoru = typy_wzorow(typy)

    suma, pola, licznik, przyklady = Counter(), Counter(), Counter(), {}
    dokumenty = []
    for sprawa in sorted(p for d in args.dane for p in d.iterdir() if p.is_dir()):
        wzory = {typ_wzoru[frozenset(j)]: j for j in (json.loads(p.read_text(encoding="utf-8")) for p in sprawa.glob("*.json"))}
        for pdf in sorted(sprawa.glob("*.pdf")):
            d = {"pdf": pdf, **dokument_z_tekstu(tekst_pdf(pdf, ust), typy, ust, [])}
            if d["typ"] in wzory:
                dokumenty.append((d, wzory[d["typ"]]))
    po_typie = {t["typ"]: t for t in typy}
    for oryginal, wzor in dokumenty:
        pdf, oczekiwany = oryginal["pdf"], oryginal["typ"]
        inne = [d for d, _ in dokumenty if d["pdf"].parent == pdf.parent and d is not oryginal]
        for rodzaj, t, wz in warianty(oryginal["tekst"], wzor, pdf, w, ust):
            wariant = dokument_z_tekstu(t, typy, ust, [])
            nasz = wariant["dane"] if wariant["typ"] == oczekiwany else {}
            if nasz:
                kontekst_sprawy([wariant, *inne], po_typie, ust)
            licznik[rodzaj, "warianty"] += 1
            licznik[rodzaj, "zly_typ"] += not nasz
            wyniki = dict(liscie(nasz))
            for sciezka, wynik in porownaj(bez_prefiksu(wz, ust), bez_prefiksu(nasz, ust)):
                rodzina = rodzaj.split(" ")[0]
                suma[rodzaj, wynik] += 1
                suma["razem", wynik] += 1
                if wynik != "TP":
                    pole = (rodzina, oczekiwany, pole_ogolne(sciezka))
                    pola[pole] += 1
                    przyklady.setdefault(pole, (pdf, rodzaj, dict(liscie(wz)).get(sciezka), wyniki.get(sciezka)))

    miejsca = ust["narzedzia"]["MIEJSCA_F1"]

    def f1(r):
        return miara_f1(*(suma[r, x] for x in ("TP", "FP", "FN")))

    rodzaje = sorted({r for r, _ in licznik}, key=f1)
    print(f"Warianty: {sum(licznik[r, 'warianty'] for r in rodzaje)} | F1 razem = {f1('razem'):.{miejsca}f}")
    for r in rodzaje:
        print(f"  F1 {f1(r):.{miejsca}f}  warianty {licznik[r, 'warianty']}  zły typ {licznik[r, 'zly_typ']}  {r}")
    print("Najgorsze pola (rodzina, typ, pole, FN+FP):")
    for pole, ile in pola.most_common(w["NAJGORSZE"]):
        print(f"  {ile}  {' '.join(pole)}")
        if args.przyklady:
            pdf, rodzaj, oczek, nasze = przyklady[pole]
            print(f"      {pdf.parent.name}/{pdf.name} [{rodzaj}] wzór: {oczek!r} | nasze: {nasze!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
