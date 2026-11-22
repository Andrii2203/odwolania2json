import io
import json
import re
import sys
import tempfile
import zipfile
from pathlib import Path

import pypdfium2 as pdfium
import streamlit as st
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from odwolania2json.kreator import jako_yaml, pole_z_przykladu, sprobuj, typ_z_formularza
from odwolania2json.pipeline import ROOT, przetworz_wszystkie, tekst_pdf, ustawienia, wczytaj_typy

PRZYKLADY = ROOT / "docs" / "przyklady"
PRZYKLAD_KREATORA = PRZYKLADY / "kreator" / "ogloszenie_ted.yaml"
PRZYKLAD_SPRAWY = ROOT / "data" / "uzp" / "dane" / "przyklad_01"
KROKI = [("1. Wgraj", "PDF jednej sprawy: odwołanie, pełnomocnictwo, potwierdzenie przelewu. Można kilka naraz."),
         ("2. Sprawdź", "Obok podglądu dokumentu widać odczytane dane i skąd pochodzi każda wartość."),
         ("3. Pobierz", "JSON dla każdego pliku albo wszystkie naraz w ZIP.")]


def obrazy_stron(pdf: Path) -> list:
    dokument = pdfium.PdfDocument(str(pdf))
    try:
        return [strona.render().to_pil() for strona in dokument]
    finally:
        dokument.close()


@st.cache_data(show_spinner=False)
def przetworz(pliki: tuple[tuple[str, bytes], ...], nowe_typy: tuple[str, ...]) -> list[dict]:
    # wszystkie wgrane pliki to jedna sprawa: działa kontekst sprawy, jak w CLI dla jednego katalogu
    typy, ust = wczytaj_typy(dodatkowe=nowe_typy), ustawienia()
    opisy = {t["typ"]: t.get("opis", t["typ"]) for t in typy}
    with tempfile.TemporaryDirectory() as katalog:
        sciezki = []
        for nazwa, zawartosc in pliki:
            sciezka = Path(katalog) / Path(nazwa).name
            sciezka.write_bytes(zawartosc)
            sciezki.append(sciezka)
        dzienniki, wyniki = {}, []
        for pdf, wynik, blad in przetworz_wszystkie(sciezki, typy, ust, dzienniki):
            wyniki.append({"nazwa": pdf.name, "typ": wynik and opisy[wynik[0]], "dane": wynik[1] if wynik else {},
                           "blad": f"{type(blad).__name__}: {blad}" if blad else None,
                           "dziennik": dzienniki.get(pdf, []), "obrazy": obrazy_stron(pdf) if blad is None else []})
    return wyniki


def plik_zip(dokumenty: dict[str, str]) -> bytes:
    bufor = io.BytesIO()
    with zipfile.ZipFile(bufor, "w", zipfile.ZIP_DEFLATED) as archiwum:
        for nazwa, tekst in dokumenty.items():
            archiwum.writestr(nazwa, tekst)
    return bufor.getvalue()


def panel_typow() -> tuple[str, ...]:
    st.sidebar.header("Rozpoznawane dokumenty")
    st.sidebar.markdown("\n".join(f"- {t.get('opis', t['typ'])}" for t in wczytaj_typy()))
    st.sidebar.caption("Każdy inny dokument dostaje pusty JSON: {}")
    st.sidebar.subheader("Dodatkowe typy")
    st.sidebar.caption("Włącz, aby program rozpoznawał też te dokumenty. Każdy typ to jeden plik YAML, kod się nie zmienia.")
    z_kreatora = st.session_state.get("typy_z_kreatora", {})
    zrodla = {**{p.stem: p.read_text(encoding="utf-8") for p in sorted(PRZYKLADY.glob("*.yaml"))}, **z_kreatora}
    wybrane = []
    for klucz, tekst in zrodla.items():
        opis = yaml.safe_load(tekst).get("opis", klucz)
        if not st.sidebar.toggle(opis + (" (z kreatora)" if klucz in z_kreatora else ""), value=klucz in z_kreatora,
                                 key=f"typ_{klucz}"):
            continue
        with st.sidebar.expander("Plik typu (YAML), można zmienić"):
            tekst = st.text_area(klucz, tekst, key=f"yaml_{klucz}", height="content", label_visibility="collapsed")
        try:
            yaml.safe_load(tekst)
        except yaml.YAMLError as blad:
            st.sidebar.error(f"Niepoprawny YAML: {blad}")
            continue
        wybrane.append(tekst)
    return tuple(wybrane)


def tabela_dziennika(dziennik: list[dict]) -> None:
    with st.expander("Skąd te wartości (reguła i fragment dokumentu)"):
        st.dataframe([{"pole": z["pole"], "wartość": str(z["wartosc"]), "reguła": z["regula"], "fragment": z["fragment"]}
                      for z in dziennik], hide_index=True)


@st.cache_data(show_spinner=False)
def tekst_dokumentu(nazwa: str, zawartosc: bytes) -> str:
    with tempfile.TemporaryDirectory() as katalog:
        pdf = Path(katalog) / Path(nazwa).name
        pdf.write_bytes(zawartosc)
        return tekst_pdf(pdf, ustawienia())


def pole_z_wiersza(w: dict, tekst: str, rodzaje: dict, ust: dict) -> tuple[dict | None, str]:
    pole, wartosc = (w.get("pole") or "").strip(), (w.get("wartosc") or "").strip()
    etykieta, rodzaj = (w.get("etykieta") or "").strip() or None, w.get("rodzaj") or None
    if not wartosc:
        if rodzaj:
            return {"pole": pole, "etykiety": [etykieta] if etykieta else [], "rodzaj": rodzaj}, "ustawione ręcznie"
        return None, "❌ wklej wartość z dokumentu"
    znalezione = pole_z_przykladu(pole, wartosc, tekst, rodzaje, ust, etykieta, rodzaj)
    if znalezione is None:
        return None, "❌ nie ma tej wartości w dokumencie: skopiuj ją z tekstu dokumentu"
    if znalezione["rodzaj"] is None:
        if rodzaj:
            return {**znalezione, "rodzaj": rodzaj}, "⚠️ ten rodzaj nie odczytuje tej wartości"
        return None, "⚠️ wybierz rodzaj wartości"
    return znalezione, "✅ odczytane"


def wczytaj_przyklad_kreatora() -> None:
    przyklad = yaml.safe_load(PRZYKLAD_KREATORA.read_text(encoding="utf-8"))
    st.session_state.update({"kreator_nazwa": przyklad["nazwa"], "kreator_znaczniki": przyklad["znaczniki"],
                             "kreator_wykluczenia": przyklad["wspolne_wykluczenia"],
                             "kreator_przyklad_pdf": str(ROOT / przyklad["pdf"]), "kreator_wiersze": przyklad["pola"],
                             "kreator_wersja": st.session_state.get("kreator_wersja", 0) + 1})


def kreator() -> None:
    ust = ustawienia()
    rodzaje = ust["kreator"]["rodzaje"]
    st.markdown("Naucz program nowego rodzaju dokumentu, bez programowania. Wystarczy jeden przykładowy PDF.")
    st.button("Pokaż na przykładzie (ogłoszenie TED)", on_click=wczytaj_przyklad_kreatora)

    st.subheader("1. Wgraj przykładowy dokument")
    pdf = st.file_uploader("Jeden PDF nowego typu", type=["pdf"], key="kreator_pdf")
    if pdf:
        zrodlo = (pdf.name, pdf.getvalue())
    elif przyklad := st.session_state.get("kreator_przyklad_pdf"):
        zrodlo = (Path(przyklad).name, Path(przyklad).read_bytes())
        st.caption(f"Przykładowy dokument: {zrodlo[0]}")
    else:
        st.info("Zacznij od wgrania jednego przykładowego dokumentu albo kliknij „Pokaż na przykładzie”.")
        return
    tekst = tekst_dokumentu(*zrodlo)
    with st.expander("Tekst dokumentu: stąd kopiuj wartości do kroku 3"):
        st.code(tekst, language=None, wrap_lines=True)

    st.subheader("2. Nazwij typ")
    lewa, prawa = st.columns([1, 1])
    nazwa = lewa.text_input("Nazwa typu", placeholder="np. Faktura VAT", key="kreator_nazwa").strip()
    znaczniki = [z.strip() for z in prawa.text_input(
        "Słowa, po których program rozpozna ten dokument", placeholder="np. faktura VAT, sprzedawca, nabywca",
        help="Słowa, które są w każdym takim dokumencie, a w innych nie. Oddziel przecinkami.",
        key="kreator_znaczniki").split(",") if z.strip()]

    st.subheader("3. Wskaż dane do odczytania")
    st.markdown("W każdym wierszu: **nazwa pola** i **wartość skopiowana z dokumentu**. "
                "Etykietę i rodzaj wartości program znajdzie sam; można je poprawić.")
    st.caption("Przykład wiersza: `Faktura.numer` | `FV/12/2026`. Kropka tworzy grupę w JSON: "
               "{\"Faktura\": {\"numer\": \"FV/12/2026\"}}.")
    wiersze = st.data_editor(
        [{"pole": "", "wartosc": "", "etykieta": None, "rodzaj": None, **w}
         for w in st.session_state.get("kreator_wiersze", [{}])], num_rows="dynamic", width="stretch",
        key=f"kreator_pola_{st.session_state.get('kreator_wersja', 0)}",
        column_order=["pole", "wartosc", "etykieta", "rodzaj"], column_config={
            "pole": st.column_config.TextColumn("Nazwa pola w JSON", help="np. Faktura.numer"),
            "wartosc": st.column_config.TextColumn("Wartość z dokumentu", help="Skopiuj z tekstu dokumentu (krok 1)"),
            "etykieta": st.column_config.TextColumn("Etykieta (opcjonalnie)",
                                                    help="Napis przed wartością w dokumencie, np. „Numer faktury”"),
            "rodzaj": st.column_config.SelectboxColumn("Rodzaj (opcjonalnie)", options=list(rodzaje))})
    wykryte = [(w, *pole_z_wiersza(w, tekst, rodzaje, ust)) for w in wiersze if (w.get("pole") or "").strip()]
    if wykryte:
        st.dataframe([{"pole": w["pole"], "etykieta": "; ".join(p["etykiety"]) if p and p["etykiety"] else "",
                       "rodzaj": p["rodzaj"] if p else "", "wynik": status} for w, p, status in wykryte],
                     hide_index=True, width="stretch")
    pola = [p for _, p, _ in wykryte if p]

    st.subheader("4. Sprawdź wynik i zapisz")
    if not (nazwa and znaczniki and pola):
        st.info("Uzupełnij krok 2 (nazwa i słowa rozpoznające) i co najmniej jedno pole w kroku 3.")
        return
    st.session_state.setdefault("kreator_wykluczenia", True)
    with st.expander("Ustawienia zaawansowane"):
        wspolne = st.checkbox("Nie rozpoznawaj jako ten typ wyroków KIO, ogłoszeń TED i innych pism z akt (zalecane)",
                              key="kreator_wykluczenia")
    typ_id = re.sub(r"\W+", "_", nazwa.lower()).strip("_")
    tekst_yaml = jako_yaml(typ_z_formularza(typ_id, nazwa, znaczniki, pola, rodzaje, wspolne))
    try:
        wynik = sprobuj(tekst_yaml, tekst)
    except Exception as blad:
        st.error(f"Błąd typu: {type(blad).__name__}: {blad}")
        return
    if wynik["rozpoznany"] == typ_id:
        st.success("Program rozpoznaje przykład jako nowy typ.")
    else:
        st.warning(f"Program rozpoznaje przykład jako: {wynik['rozpoznany'] or 'nieznany dokument'}. "
                   "Dodaj w kroku 2 słowa, które są tylko w tym dokumencie.")
    lewa, prawa = st.columns([1, 1])
    with lewa:
        st.markdown("**Odczytane dane**")
        st.json(wynik["dane"])
        tabela_dziennika(wynik["dziennik"])
    with prawa:
        st.download_button("Pobierz plik typu (YAML)", tekst_yaml, file_name=f"{typ_id}.yaml", mime="application/x-yaml",
                           type="primary")
        if st.button("Użyj tego typu w zakładce „Zamień PDF na JSON”"):
            st.session_state.setdefault("typy_z_kreatora", {})[typ_id] = tekst_yaml
            st.session_state.pop(f"typ_{typ_id}", None)
            st.rerun()
        st.caption("Na stałe (także w CLI): zapisz pobrany plik w folderze config/typy/. Kod się nie zmienia.")
        with st.expander("Plik typu (YAML)"):
            st.code(tekst_yaml, language="yaml")


def dokument(w: dict, wciecie: int, gotowe: dict) -> None:
    nazwa_json = Path(w["nazwa"]).with_suffix(".json").name
    with st.container(border=True):
        if w["blad"]:
            st.error(f"**{w['nazwa']}**: nie udało się odczytać pliku. Zapisany będzie pusty JSON: {{}}")
            st.caption(w["blad"])
        elif w["typ"] is None:
            st.warning(f"**{w['nazwa']}**: to nie jest żaden z rozpoznawanych dokumentów. "
                       "Zapisany będzie pusty JSON: {}")
        else:
            st.markdown(f"### {w['nazwa']}  \n✅ {w['typ']}")
        lewa, prawa = st.columns([1, 1])
        with lewa:
            strony = list(enumerate(w["obrazy"], start=1))
            for nr, obraz in strony[:1]:
                st.image(obraz, caption=f"Strona {nr} z {len(strony)}", width="stretch")
            if strony[1:]:
                with st.expander("Pozostałe strony"):
                    for nr, obraz in strony[1:]:
                        st.image(obraz, caption=f"Strona {nr}", width="stretch")
        with prawa:
            st.markdown("**Odczytane dane**")
            miejsce_danych, miejsce_pobrania = st.empty(), st.empty()
            if w["dziennik"]:
                tabela_dziennika(w["dziennik"])
            pierwotny = json.dumps(w["dane"], ensure_ascii=False, indent=wciecie)
            with st.expander("Popraw dane ręcznie"):
                tekst = st.text_area("JSON", pierwotny, key=f"json_{w['nazwa']}_{hash(pierwotny)}", height="content",
                                     label_visibility="collapsed")
            try:
                dane = json.loads(tekst)
            except json.JSONDecodeError as blad:
                st.error(f"Niepoprawny JSON: {blad}")
                dane = w["dane"]
            miejsce_danych.json(dane)
            if dane != w["dane"]:
                st.caption("Zmieniono ręcznie.")
            gotowe[nazwa_json] = json.dumps(dane, ensure_ascii=False, indent=wciecie)
            miejsce_pobrania.download_button(f"Pobierz {nazwa_json}", gotowe[nazwa_json], file_name=nazwa_json,
                                             mime="application/json", key=f"pobierz_{w['nazwa']}")


def analiza(nowe_typy: tuple[str, ...]) -> None:
    wciecie = ustawienia()["liczby"]["WCIECIE_JSON"]
    for kolumna, (tytul, opis) in zip(st.columns(len(KROKI)), KROKI):
        with kolumna.container(border=True):
            st.markdown(f"**{tytul}**  \n{opis}")
    pliki = st.file_uploader("Wgraj pliki PDF jednej sprawy", type=["pdf"], accept_multiple_files=True)
    if pliki:
        wejscie = [(p.name, p.getvalue()) for p in pliki]
    elif PRZYKLAD_SPRAWY.is_dir() and (st.session_state.get("przyklad_sprawy") or st.button("Pokaż na przykładowej sprawie UZP")):
        st.session_state["przyklad_sprawy"] = True
        wejscie = [(p.name, p.read_bytes()) for p in sorted(PRZYKLAD_SPRAWY.glob("*.pdf"))]
        st.caption(f"Przykładowa sprawa: {', '.join(n for n, _ in wejscie)}")
    else:
        return

    with st.spinner("Odczytywanie dokumentów (skany: kilka sekund na stronę)..."):
        try:
            wyniki = przetworz(tuple(wejscie), nowe_typy)
        except Exception as blad:
            st.error(f"Błąd w pliku dodatkowego typu: {type(blad).__name__}: {blad}")
            return

    rozpoznane = sum(w["typ"] is not None for w in wyniki)
    st.success(f"Gotowe. Rozpoznane dokumenty: {rozpoznane} z {len(wyniki)}.")
    miejsce_zip, gotowe = st.empty(), {}
    for w in wyniki:
        dokument(w, wciecie, gotowe)
    miejsce_zip.download_button(f"Pobierz wszystkie JSON (ZIP, plików: {len(gotowe)})", plik_zip(gotowe),
                                file_name="output.zip", mime="application/zip", type="primary", disabled=not gotowe)


def main() -> None:
    st.set_page_config(page_title="Odwołania2JSON", page_icon="📄", layout="wide")
    st.title("Odwołania2JSON")
    st.caption("Zamienia dokumenty sprawy odwoławczej do KIO (PDF, także skany) na dane JSON.")
    nowe_typy = panel_typow()
    zakladka_analizy, zakladka_kreatora = st.tabs(["📄 Zamień PDF na JSON", "➕ Dodaj nowy typ dokumentu"])
    with zakladka_analizy:
        analiza(nowe_typy)
    with zakladka_kreatora:
        kreator()


if __name__ == "__main__":
    main()
