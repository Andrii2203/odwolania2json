import io
import json
import sys
import tempfile
import zipfile
from pathlib import Path

import pypdfium2 as pdfium
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from odwolania2json.pipeline import przetworz_wszystkie, ustawienia, wczytaj_typy


def obrazy_stron(pdf: Path) -> list:
    dokument = pdfium.PdfDocument(str(pdf))
    try:
        return [strona.render().to_pil() for strona in dokument]
    finally:
        dokument.close()


@st.cache_data(show_spinner=False)
def przetworz(pliki: tuple[tuple[str, bytes], ...]) -> list[dict]:
    # wszystkie wgrane pliki to jedna sprawa: działa kontekst sprawy, jak w CLI dla jednego katalogu
    typy, ust = wczytaj_typy(), ustawienia()
    with tempfile.TemporaryDirectory() as katalog:
        sciezki = []
        for nazwa, zawartosc in pliki:
            sciezka = Path(katalog) / Path(nazwa).name
            sciezka.write_bytes(zawartosc)
            sciezki.append(sciezka)
        dzienniki, wyniki = {}, []
        for pdf, wynik, blad in przetworz_wszystkie(sciezki, typy, ust, dzienniki):
            wyniki.append({"nazwa": pdf.name, "typ": wynik[0] if wynik else None, "dane": wynik[1] if wynik else {},
                           "blad": f"{type(blad).__name__}: {blad}" if blad else None,
                           "dziennik": dzienniki.get(pdf, []), "obrazy": obrazy_stron(pdf) if blad is None else []})
    return wyniki


def plik_zip(dokumenty: dict[str, str]) -> bytes:
    bufor = io.BytesIO()
    with zipfile.ZipFile(bufor, "w", zipfile.ZIP_DEFLATED) as archiwum:
        for nazwa, tekst in dokumenty.items():
            archiwum.writestr(nazwa, tekst)
    return bufor.getvalue()


def main() -> None:
    st.set_page_config(page_title="Odwołania2JSON", layout="wide")
    st.title("Odwołania2JSON")

    wciecie = ustawienia()["liczby"]["WCIECIE_JSON"]
    pliki = st.file_uploader("Wgraj dokumenty jednej sprawy (PDF)", type=["pdf"], accept_multiple_files=True)
    if not pliki:
        st.info("Wybierz pliki PDF, aby rozpocząć analizę.")
        return

    with st.spinner("Przetwarzanie (skany: kilka sekund na stronę)..."):
        wyniki = przetworz(tuple((p.name, p.getvalue()) for p in pliki))

    gotowe = {}
    miejsce_zip = st.empty()
    for w in wyniki:
        nazwa_json = Path(w["nazwa"]).with_suffix(".json").name
        st.subheader(w["nazwa"])
        lewa, prawa = st.columns([1, 1])
        with lewa:
            for nr, obraz in enumerate(w["obrazy"], start=1):
                st.image(obraz, caption=f"Strona {nr}", width="stretch")
        with prawa:
            if w["blad"]:
                st.error(f"Błąd przetwarzania: {w['blad']}")
            elif w["typ"] is None:
                st.warning("Nieznany typ dokumentu: plik JSON z {}")
            else:
                st.markdown(f"**Typ dokumentu:** `{w['typ']}`")
            pierwotny = json.dumps(w["dane"], ensure_ascii=False, indent=wciecie)
            tekst = st.text_area("JSON (można poprawić ręcznie)", pierwotny, key=f"json_{w['nazwa']}",
                                 height="content")
            try:
                dane = json.loads(tekst)
            except json.JSONDecodeError as blad:
                st.error(f"Niepoprawny JSON: {blad}")
            else:
                if dane != w["dane"]:
                    st.caption("Zmieniono ręcznie.")
                gotowe[nazwa_json] = json.dumps(dane, ensure_ascii=False, indent=wciecie)
                st.download_button("Pobierz JSON", gotowe[nazwa_json], file_name=nazwa_json,
                                   mime="application/json", key=f"pobierz_{w['nazwa']}")
            if w["dziennik"]:
                with st.expander("Skąd każda wartość (reguła i fragment tekstu)"):
                    st.table([{"pole": z["pole"], "wartość": str(z["wartosc"]), "reguła": z["regula"],
                               "tekst": z["fragment"]} for z in w["dziennik"]])

    miejsce_zip.download_button(f"Pobierz wszystkie ({len(gotowe)} JSON, ZIP)", plik_zip(gotowe),
                                file_name="output.zip", mime="application/zip", disabled=not gotowe)


if __name__ == "__main__":
    main()
