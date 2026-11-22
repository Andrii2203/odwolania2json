import io
import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

import pypdfium2 as pdfium
import streamlit as st
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from odwolania2json.pipeline import KONFIG, ROOT, przetworz_wszystkie, ustawienia, wczytaj_typy

PRZYKLADY = ROOT / "docs" / "przyklady"


def obrazy_stron(pdf: Path) -> list:
    dokument = pdfium.PdfDocument(str(pdf))
    try:
        return [strona.render().to_pil() for strona in dokument]
    finally:
        dokument.close()


@st.cache_data(show_spinner=False)
def przetworz(pliki: tuple[tuple[str, bytes], ...], nowe_typy: tuple[tuple[str, str], ...]) -> list[dict]:
    # wszystkie wgrane pliki to jedna sprawa: działa kontekst sprawy, jak w CLI dla jednego katalogu
    with tempfile.TemporaryDirectory() as katalog:
        config = KONFIG
        if nowe_typy:
            # nowy typ = dodatkowy plik YAML w kopii config/typy/, kod bez zmian (README, T21)
            config = Path(katalog) / "config"
            shutil.copytree(KONFIG, config)
            for nazwa, tekst in nowe_typy:
                (config / "typy" / nazwa).write_text(tekst, encoding="utf-8")
        typy, ust = wczytaj_typy(config), ustawienia(config)
        sciezki = []
        (Path(katalog) / "pdf").mkdir()
        for nazwa, zawartosc in pliki:
            sciezka = Path(katalog) / "pdf" / Path(nazwa).name
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


def panel_typow() -> tuple[tuple[str, str], ...]:
    st.sidebar.header("Typy dokumentów")
    st.sidebar.caption("Z `config/typy/`: " + ", ".join(p.stem for p in sorted((KONFIG / "typy").glob("*.yaml"))))
    wybrane = []
    for plik in sorted(PRZYKLADY.glob("*.yaml")):
        tekst = plik.read_text(encoding="utf-8")
        opis = yaml.safe_load(tekst).get("opis", plik.stem)
        if not st.sidebar.toggle(f"Nowy typ (przykład): {opis}", key=f"typ_{plik.name}"):
            continue
        with st.sidebar.expander("Plik typu: cały nowy typ to ten plik YAML, kod bez zmian", expanded=True):
            tekst = st.text_area(f"docs/przyklady/{plik.name}", tekst, key=f"yaml_{plik.name}", height="content")
        try:
            yaml.safe_load(tekst)
        except yaml.YAMLError as blad:
            st.sidebar.error(f"Niepoprawny YAML: {blad}")
            continue
        wybrane.append((plik.name, tekst))
    return tuple(wybrane)


def main() -> None:
    st.set_page_config(page_title="Odwołania2JSON", layout="wide")
    st.title("Odwołania2JSON")
    nowe_typy = panel_typow()

    wciecie = ustawienia()["liczby"]["WCIECIE_JSON"]
    pliki = st.file_uploader("Wgraj dokumenty jednej sprawy (PDF)", type=["pdf"], accept_multiple_files=True)
    if not pliki:
        st.info("Wybierz pliki PDF, aby rozpocząć analizę.")
        return

    with st.spinner("Przetwarzanie (skany: kilka sekund na stronę)..."):
        try:
            wyniki = przetworz(tuple((p.name, p.getvalue()) for p in pliki), nowe_typy)
        except Exception as blad:
            st.error(f"Błąd konfiguracji typu: {type(blad).__name__}: {blad}")
            return

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
            tekst = st.text_area("JSON (można poprawić ręcznie)", pierwotny, key=f"json_{w['nazwa']}_{hash(pierwotny)}",
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
