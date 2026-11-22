import io
import json
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

import pypdfium2 as pdfium
import streamlit as st
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from odwolania2json.kreator import jako_yaml, sprobuj, typ_z_formularza
from odwolania2json.pipeline import KONFIG, ROOT, przetworz_wszystkie, tekst_pdf, ustawienia, wczytaj_typy

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


def tabela_dziennika(dziennik: list[dict]) -> None:
    with st.expander("Skąd każda wartość (reguła i fragment tekstu)"):
        st.table([{"pole": z["pole"], "wartość": str(z["wartosc"]), "reguła": z["regula"], "tekst": z["fragment"]}
                  for z in dziennik])


@st.cache_data(show_spinner=False)
def tekst_dokumentu(nazwa: str, zawartosc: bytes) -> str:
    with tempfile.TemporaryDirectory() as katalog:
        pdf = Path(katalog) / Path(nazwa).name
        pdf.write_bytes(zawartosc)
        return tekst_pdf(pdf, ustawienia())


def kreator() -> None:
    rodzaje = ustawienia()["kreator"]["rodzaje"]
    st.markdown("Nowy typ dokumentu bez programowania: przykładowy PDF, nazwy pól i ich etykiety z dokumentu. "
                "Kreator składa plik typu (YAML) i od razu pokazuje wynik na przykładzie.")
    pdf = st.file_uploader("Przykładowy dokument nowego typu (PDF)", type=["pdf"], key="kreator_pdf")
    lewa, prawa = st.columns([1, 1])
    with lewa:
        nazwa = re.sub(r"\W", "_", st.text_input("Nazwa typu (np. wezwanie)", key="kreator_nazwa").strip().lower())
        opis = st.text_input("Opis", key="kreator_opis")
        znaczniki = [z.strip() for z in st.text_input("Słowa, po których program pozna ten typ (po przecinku)",
                                                      key="kreator_znaczniki").split(",") if z.strip()]
        wspolne = st.checkbox("Wspólne wykluczenia (wyrok KIO, ogłoszenie TED) dotyczą też tego typu", value=True,
                              key="kreator_wykluczenia")
        st.caption("Pole JSON: np. Nabywca.nazwa (kropka to zagnieżdżenie). Etykieta: jak pole jest podpisane "
                   "w dokumencie, kilka wariantów po średniku. Rodzaj: jak wygląda wartość.")
        tabela = st.data_editor([{"pole": "", "etykieta": "", "rodzaj": next(iter(rodzaje))}], num_rows="dynamic",
                                key="kreator_pola", width="stretch", column_config={
                                    "pole": st.column_config.TextColumn("Pole JSON"),
                                    "etykieta": st.column_config.TextColumn("Etykieta w dokumencie"),
                                    "rodzaj": st.column_config.SelectboxColumn("Rodzaj", options=list(rodzaje))})
    pola = [{"pole": w["pole"].strip(), "rodzaj": w["rodzaj"],
             "etykiety": [e.strip() for e in (w.get("etykieta") or "").split(";") if e.strip()]}
            for w in tabela if (w.get("pole") or "").strip() and w.get("rodzaj")]
    if not (nazwa and znaczniki and pola):
        prawa.info("Uzupełnij nazwę typu, słowa rozpoznające i co najmniej jedno pole.")
        return
    tekst_yaml = jako_yaml(typ_z_formularza(nazwa, opis or nazwa, znaczniki, pola, rodzaje, wspolne))
    with prawa:
        if pdf:
            try:
                wynik = sprobuj(tekst_yaml, tekst_dokumentu(pdf.name, pdf.getvalue()))
            except Exception as blad:
                st.error(f"Błąd typu: {type(blad).__name__}: {blad}")
            else:
                if wynik["rozpoznany"] == nazwa:
                    st.success("Przykład rozpoznany jako nowy typ.")
                else:
                    st.warning(f"Przykład rozpoznany jako: {wynik['rozpoznany'] or 'brak typu, {}'}. "
                               "Dodaj albo zmień słowa rozpoznające.")
                st.json(wynik["dane"])
                tabela_dziennika(wynik["dziennik"])
        else:
            st.info("Wgraj przykładowy PDF, żeby zobaczyć wynik.")
        st.code(tekst_yaml, language="yaml")
        st.download_button("Pobierz plik typu (YAML)", tekst_yaml, file_name=f"{nazwa}.yaml", mime="application/x-yaml")
        st.caption("Zapisz plik w config/typy/: od tej chwili CLI i GUI rozpoznają nowy typ, kod się nie zmienia.")


def main() -> None:
    st.set_page_config(page_title="Odwołania2JSON", layout="wide")
    st.title("Odwołania2JSON")
    nowe_typy = panel_typow()
    zakladka_analizy, zakladka_kreatora = st.tabs(["Analiza dokumentów", "Kreator nowego typu"])
    with zakladka_analizy:
        analiza(nowe_typy)
    with zakladka_kreatora:
        kreator()


def analiza(nowe_typy: tuple[tuple[str, str], ...]) -> None:
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
                tabela_dziennika(w["dziennik"])

    miejsce_zip.download_button(f"Pobierz wszystkie ({len(gotowe)} JSON, ZIP)", plik_zip(gotowe),
                                file_name="output.zip", mime="application/zip", disabled=not gotowe)


if __name__ == "__main__":
    main()
