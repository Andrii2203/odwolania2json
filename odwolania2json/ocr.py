import re
from functools import cache
from math import atan2, tan
from pathlib import Path
from statistics import median

import pypdfium2 as pdfium


@cache
def _silnik():
    from rapidocr import RapidOCR
    return RapidOCR(params={"Global.log_level": "error"})


def _srodek(ramka) -> tuple[float, float]:
    return sum(p[0] for p in ramka) / len(ramka), sum(p[1] for p in ramka) / len(ramka)


def _wiersze(ramki, teksty, tolerancja: float) -> str:
    # skan bywa przekrzywiony: y liczymy wzdłuż nachylenia linii tekstu
    nachylenie = tan(median(atan2(pg[1] - lg[1], pg[0] - lg[0]) for lg, pg, _, _ in ramki))
    elementy = []
    for ramka, tekst in zip(ramki, teksty):
        x, y = _srodek(ramka)
        lg, _, _, ld = ramka
        elementy.append((y - x * nachylenie, ld[1] - lg[1], lg[0], tekst))
    wiersze = []
    for y, wysokosc, x, tekst in sorted(elementy):
        if wiersze and y - wiersze[-1][0] <= wysokosc * tolerancja:
            wiersze[-1][1].append((x, tekst))
        else:
            wiersze.append((y, [(x, tekst)]))
    return "\n".join(" ".join(t for _, t in sorted(w)) for _, w in wiersze)


def _popraw(tekst: str, poprawki: list) -> str:
    for wzorzec, zamiana in poprawki:
        tekst = re.sub(wzorzec, zamiana, tekst)
    return tekst


def tekst_skanu(pdf: Path, strony: list[int], ust: dict) -> list[str]:
    liczby = ust["liczby"]
    dokument = pdfium.PdfDocument(pdf)
    try:
        wyniki = []
        for nr in strony:
            obraz = dokument[nr].render(scale=liczby["OCR_DPI"] / liczby["PUNKTY_NA_CAL"]).to_numpy()
            wynik = _silnik()(obraz)
            tekst = _wiersze(wynik.boxes, wynik.txts, liczby["TOLERANCJA_WIERSZA"]) if wynik.txts else ""
            wyniki.append(_popraw(tekst, ust["poprawki_ocr"]))
        return wyniki
    finally:
        dokument.close()
