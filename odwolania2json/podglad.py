import re

import pypdfium2 as pdfium
from PIL import Image, ImageDraw, ImageFont

Prostokat = tuple[float, float, float, float]


def _bez_odstepow(s: str) -> str:
    return re.sub(r"\s+", "", s)


def _strony(dokument: pdfium.PdfDocument) -> list[tuple]:
    # tekst strony bez odstępów i numery znaków w pdfium: tekst z pypdf i z pdfium łamie się inaczej
    strony = []
    for strona in dokument:
        tekst = strona.get_textpage()
        znaki = [i for i, z in enumerate(tekst.get_text_range()) if not z.isspace()]
        strony.append((strona, tekst, znaki, _bez_odstepow(tekst.get_text_range())))
    return strony


def _linie(tekst: pdfium.PdfTextPage, indeksy: list[int]) -> list[Prostokat]:
    # ramki znaków -> jeden prostokąt na linię (left, bottom, right, top w punktach PDF)
    linie = []
    for i in indeksy:
        l, b, r, t = tekst.get_charbox(i)
        if linie:
            lewo, dol, prawo, gora = linie[-1]
            if b < gora and t > dol and l >= lewo:
                linie[-1] = (lewo, min(dol, b), max(prawo, r), max(gora, t))
                continue
        linie.append((l, b, r, t))
    return linie


def _szukaj(strony: list[tuple], fragment: str, wartosc) -> tuple[int, list[Prostokat], list[Prostokat]] | None:
    igla, w = _bez_odstepow(fragment or ""), _bez_odstepow("" if wartosc is None else str(wartosc))
    if not igla:
        return None
    for nr, (_, tekst, znaki, plaski) in enumerate(strony):
        if (p := plaski.find(igla)) < 0:
            continue
        q = igla.find(w) if w else -1
        return nr, _linie(tekst, znaki[p:p + len(igla)]), _linie(tekst, znaki[p + q:p + q + len(w)]) if q >= 0 else []
    return None


def miejsce(pdf: bytes, fragment: str, wartosc) -> tuple[int, list[Prostokat], list[Prostokat]] | None:
    # pierwsze wystąpienie fragmentu: strona, prostokąty fragmentu, prostokąty wartości w nim
    dokument = pdfium.PdfDocument(pdf)
    try:
        return _szukaj(_strony(dokument), fragment, wartosc)
    finally:
        dokument.close()


def podglad(pdf: bytes, zrodla: list[tuple[str, object]], ust: dict) -> list[Image.Image]:
    # strony jako obrazy; fragment z dziennika na żółto, wartość na pomarańczowo, numer jak pozycja w dzienniku
    kolory, liczby = ust["gui"], ust["liczby"]
    skala = liczby["PODGLAD_DPI"] / liczby["PUNKTY_NA_CAL"]
    czcionka, odstep = ImageFont.load_default(size=liczby["ROZMIAR_NUMERU"]), liczby["ODSTEP_NUMERU"]
    dokument = pdfium.PdfDocument(pdf)
    try:
        strony = _strony(dokument)
        obrazy = [s.render(scale=skala).to_pil().convert("RGBA") for s, *_ in strony]
        warstwy = [Image.new("RGBA", o.size) for o in obrazy]
        for nr, (fragment, wartosc) in enumerate(zrodla, start=1):
            if not (trafienie := _szukaj(strony, fragment, wartosc)):
                continue
            s, ramki_fragmentu, ramki_wartosci = trafienie
            wysokosc, rysuj = strony[s][0].get_height(), ImageDraw.Draw(warstwy[s])

            def piksele(r: Prostokat) -> Prostokat:
                lewo, dol, prawo, gora = r
                return lewo * skala, (wysokosc - gora) * skala, prawo * skala, (wysokosc - dol) * skala

            for r in ramki_fragmentu:
                rysuj.rectangle(piksele(r), fill=kolory["kolor_fragmentu"])
            for r in ramki_wartosci:
                rysuj.rectangle(piksele(r), fill=kolory["kolor_wartosci"])
            x, y, *_ = piksele(ramki_fragmentu[0])
            l, g, p, d = rysuj.textbbox((x - odstep, y), str(nr), font=czcionka, anchor="rb")
            rysuj.rectangle((l - odstep, g - odstep, p + odstep, d + odstep), fill=kolory["kolor_numeru"])
            rysuj.text((x - odstep, y), str(nr), font=czcionka, anchor="rb", fill=kolory["kolor_tekstu_numeru"])
        return [Image.alpha_composite(o, w).convert("RGB") for o, w in zip(obrazy, warstwy)]
    finally:
        dokument.close()
