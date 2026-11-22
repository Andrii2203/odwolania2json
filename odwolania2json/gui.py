import io
import json
import re
import sys
import tempfile
import zipfile
from pathlib import Path

import streamlit as st
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from odwolania2json.kreator import jako_yaml, pole_z_przykladu, sprobuj, typ_z_formularza
from odwolania2json.pipeline import ROOT, przetworz_wszystkie, przygotuj_typ, tekst_pdf, ustawienia, wczytaj_typy, wyciagnij
from odwolania2json.podglad import podglad

PRZYKLADY = ROOT / "docs" / "przyklady"
PRZYKLAD_KREATORA = PRZYKLADY / "kreator" / "faktura.yaml"
PRZYKLAD_SPRAWY = ROOT / "data" / "uzp" / "dane" / "przyklad_01"
KROKI = [("1. Wgraj", "PDF jednej sprawy: odwołanie, pełnomocnictwo, potwierdzenie przelewu. Można kilka naraz."),
         ("2. Sprawdź", "Odczytane dane są podświetlone w dokumencie, a obok jest ich lista."),
         ("3. Pobierz", "JSON dla każdego pliku albo wszystkie naraz w ZIP.")]
OK, BRAK, UWAGA, WPISZ = (":green[:material/check_circle:]", ":red[:material/cancel:]", ":orange[:material/warning:]",
                          ":blue[:material/edit:]")
LEGENDA = ("Na żółto etykieta, na pomarańczowo odczytana wartość. Numer to wiersz w „Skąd te wartości”. "
           "Skan (PDF bez tekstu) jest bez podświetlenia.")


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
            dziennik = dzienniki.get(pdf, [])
            obrazy = podglad(pdf.read_bytes(), [(z["fragment"], z["wartosc"]) for z in dziennik], ust) if blad is None else []
            wyniki.append({"nazwa": pdf.name, "typ": wynik and opisy[wynik[0]], "dane": wynik[1] if wynik else {},
                           "blad": f"{type(blad).__name__}: {blad}" if blad else None, "dziennik": dziennik, "obrazy": obrazy})
    return wyniki


@st.cache_data(show_spinner=False)
def podglad_dokumentu(zawartosc: bytes, zrodla: tuple[tuple[str, str], ...]) -> list:
    return podglad(zawartosc, list(zrodla), ustawienia())


@st.cache_data(show_spinner=False)
def tekst_dokumentu(nazwa: str, zawartosc: bytes) -> str:
    with tempfile.TemporaryDirectory() as katalog:
        pdf = Path(katalog) / Path(nazwa).name
        pdf.write_bytes(zawartosc)
        return tekst_pdf(pdf, ustawienia())


def plik_zip(dokumenty: dict[str, str]) -> bytes:
    bufor = io.BytesIO()
    with zipfile.ZipFile(bufor, "w", zipfile.ZIP_DEFLATED) as archiwum:
        for nazwa, tekst in dokumenty.items():
            archiwum.writestr(nazwa, tekst)
    return bufor.getvalue()


def strony(obrazy: list) -> None:
    lista = list(enumerate(obrazy, start=1))
    for nr, obraz in lista[:1]:
        st.image(obraz, caption=f"Strona {nr} z {len(lista)}", width="stretch")
    if lista[1:]:
        with st.expander("Pozostałe strony"):
            for nr, obraz in lista[1:]:
                st.image(obraz, caption=f"Strona {nr}", width="stretch")


def tabela_dziennika(dziennik: list[dict]) -> None:
    with st.expander("Skąd te wartości (numery jak w podglądzie dokumentu)"):
        st.dataframe([{"nr": nr, "pole": z["pole"], "wartość": str(z["wartosc"]), "reguła": z["regula"],
                       "fragment dokumentu": z["fragment"]} for nr, z in enumerate(dziennik, start=1)], hide_index=True)


def wybor_typow() -> tuple[str, ...]:
    opisy = [t.get("opis", t["typ"]) for t in wczytaj_typy()]
    st.caption(f"Rozpoznaje: {' · '.join(opisy)}. Każdy inny dokument dostaje pusty JSON: {{}}")
    z_kreatora = st.session_state.get("typy_z_kreatora", {})
    zrodla = {**{p.stem: p.read_text(encoding="utf-8") for p in sorted(PRZYKLADY.glob("*.yaml"))}, **z_kreatora}
    wybrane = []
    for kolumna, (klucz, tekst) in zip(st.columns(len(zrodla)), zrodla.items()):
        opis = yaml.safe_load(tekst).get("opis", klucz)
        if kolumna.toggle(f"Rozpoznawaj też: {opis}", value=klucz in z_kreatora, key=f"typ_{klucz}",
                          help="Dodatkowy typ dokumentu: jeden plik YAML, bez zmiany kodu. "
                               "Nowy typ można zrobić w zakładce „Dodaj nowy typ dokumentu”."):
            wybrane.append(tekst)
    return tuple(wybrane)


def dokument(w: dict, wciecie: int, gotowe: dict) -> None:
    nazwa_json = Path(w["nazwa"]).with_suffix(".json").name
    with st.container(border=True):
        if w["blad"]:
            st.error(f"**{w['nazwa']}**: nie udało się odczytać pliku. Zapisany będzie pusty JSON: {{}}")
            st.caption(w["blad"])
        elif w["typ"] is None:
            st.warning(f"**{w['nazwa']}**: to nie jest żaden z rozpoznawanych dokumentów. Zapisany będzie pusty JSON: {{}}")
        else:
            st.markdown(f"### {w['nazwa']}  \n{OK} {w['typ']}")
        lewa, prawa = st.columns([1, 1])
        with lewa:
            strony(w["obrazy"])
            if w["dziennik"]:
                st.caption(LEGENDA)
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


def analiza() -> None:
    wciecie = ustawienia()["liczby"]["WCIECIE_JSON"]
    for kolumna, (tytul, opis) in zip(st.columns(len(KROKI)), KROKI):
        with kolumna.container(border=True):
            st.markdown(f"**{tytul}**  \n{opis}")
    nowe_typy = wybor_typow()
    pliki = st.file_uploader("Wgraj pliki jednej sprawy: tylko PDF (z tekstem albo skan)", type=["pdf"],
                             accept_multiple_files=True)
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


def dodaj_wiersz() -> None:
    s = st.session_state
    s["kreator_nastepny"] = s.get("kreator_nastepny", 0) + 1
    s["kreator_wiersze"] = s.get("kreator_wiersze", []) + [s["kreator_nastepny"]]


def usun_wiersz(i: int) -> None:
    st.session_state["kreator_wiersze"] = [w for w in st.session_state["kreator_wiersze"] if w != i]


def wczytaj_przyklad_kreatora() -> None:
    przyklad, s = yaml.safe_load(PRZYKLAD_KREATORA.read_text(encoding="utf-8")), st.session_state
    s.update({"kreator_nazwa": przyklad["nazwa"], "kreator_znaczniki": przyklad["znaczniki"],
              "kreator_przyklad_pdf": str(ROOT / przyklad["pdf"]), "kreator_wiersze": []})
    for p in przyklad["pola"]:
        dodaj_wiersz()
        s[f"pole_{s['kreator_nastepny']}"], s[f"wartosc_{s['kreator_nastepny']}"] = p["pole"], p["wartosc"]


def pole_z_wiersza(i: int, tekst: str, rodzaje: dict, ust: dict) -> tuple[dict | None, str, str]:
    # (pole do typu albo None, krótki wynik, opis w okienku „popraw”)
    s = st.session_state
    pole = re.sub(r"\s+", "_", (s.get(f"pole_{i}") or "").strip())
    wartosc = (s.get(f"wartosc_{i}") or "").strip()
    etykieta, rodzaj = (s.get(f"etykieta_{i}") or "").strip() or None, s.get(f"rodzaj_{i}")
    if not (pole or wartosc):
        return None, "", ""
    if not pole:
        return None, f"{WPISZ} wpisz nazwę pola", "Nazwa pola to klucz w JSON, np. numer_faktury."
    if not wartosc:
        if etykieta and rodzaj:
            return {"pole": pole, "etykiety": [etykieta], "rodzaj": rodzaj}, f"{OK} ręcznie", "Etykieta i rodzaj ustawione ręcznie."
        return None, f"{WPISZ} wklej wartość", "Skopiuj wartość z tekstu dokumentu (pod podglądem)."
    znalezione = pole_z_przykladu(pole, wartosc, tekst, rodzaje, ust, etykieta, rodzaj)
    if znalezione is None:
        return None, f"{BRAK} brak w dokumencie", "Tej wartości nie ma w tekście dokumentu. Skopiuj ją z tekstu pod podglądem."
    opis = f"Etykieta: „{'; '.join(znalezione['etykiety']) or 'brak'}”."
    if znalezione["rodzaj"] is None:
        return None, f"{UWAGA} wybierz rodzaj", f"{opis} Żaden rodzaj nie odczytuje tej wartości: wybierz rodzaj albo zmień etykietę."
    return {**znalezione, "przyklad": wartosc}, f"{OK} {znalezione['rodzaj']}", f"{opis} Rodzaj: {znalezione['rodzaj']}."


def wiersze_pol(tekst: str, rodzaje: dict, ust: dict) -> list[dict]:
    if not st.session_state.get("kreator_wiersze"):
        dodaj_wiersz()
    pola = []
    for n, i in enumerate(st.session_state["kreator_wiersze"]):
        pole, krotko, opis = pole_z_wiersza(i, tekst, rodzaje, ust)
        k_pole, k_wartosc, k_wynik, k_usun = st.columns(ust["gui"]["kolumny_pola"], vertical_alignment="bottom")
        widoczne = "collapsed" if n else "visible"
        k_pole.text_input("Nazwa pola", placeholder="np. numer_faktury", key=f"pole_{i}", label_visibility=widoczne,
                          help="Klucz w JSON. Kropka tworzy grupę: Sprzedawca.nip -> {\"Sprzedawca\": {\"nip\": ...}}")
        k_wartosc.text_input("Wartość skopiowana z dokumentu", placeholder="np. FV/2026/04/117", key=f"wartosc_{i}",
                             label_visibility=widoczne, help="Skopiuj z tekstu dokumentu: program sam znajdzie etykietę i rodzaj.")
        with k_wynik.popover(krotko or "Wynik", disabled=not krotko, width="stretch"):
            st.markdown(opis)
            st.text_input("Etykieta (napis przed wartością)", placeholder="np. Numer faktury", key=f"etykieta_{i}",
                          help="Puste: program znajdzie sam.")
            st.selectbox("Rodzaj wartości", [None, *rodzaje], key=f"rodzaj_{i}",
                         format_func=lambda r: "program wybierze sam" if r is None else r)
        k_usun.button(":material/delete:",key=f"usun_{i}", on_click=usun_wiersz, args=(i,), help="Usuń to pole")
        if pole:
            pola.append(pole)
    st.button("Dodaj pole", icon=":material/add:",on_click=dodaj_wiersz)
    return pola


def typ_dla_przykladu(typ_id: str, nazwa: str, znaczniki: list[str], pola: list[dict], rodzaje: dict,
                      tekst: str) -> tuple[str, dict]:
    # wspólne wykluczenia (wyrok KIO, TED, inne pisma z akt) zostają, chyba że przez nie typ nie rozpoznaje
    # własnego przykładu: wtedy nowy typ to jeden z tych dokumentów
    proby = []
    for wspolne in (True, False):
        tekst_yaml = jako_yaml(typ_z_formularza(typ_id, nazwa, znaczniki, pola, rodzaje, wspolne))
        proby.append((tekst_yaml, sprobuj(tekst_yaml, tekst)))
        if proby[-1][-1]["rozpoznany"] == typ_id:
            return proby[-1]
    return proby[0]


def kreator() -> None:
    ust = ustawienia()
    rodzaje = ust["kreator"]["rodzaje"]
    st.markdown("Naucz program nowego rodzaju dokumentu, bez programowania. Wystarczy jeden przykładowy PDF.")
    st.button("Pokaż na przykładzie (faktura)", on_click=wczytaj_przyklad_kreatora)

    st.subheader("1. Wgraj przykładowy dokument")
    pdf = st.file_uploader("Jeden plik PDF nowego typu (z tekstem albo skan)", type=["pdf"], key="kreator_pdf")
    if pdf:
        zrodlo = (pdf.name, pdf.getvalue())
    elif przyklad := st.session_state.get("kreator_przyklad_pdf"):
        zrodlo = (Path(przyklad).name, Path(przyklad).read_bytes())
        st.caption(f"Przykładowy dokument: {zrodlo[0]}")
    else:
        st.info("Zacznij od wgrania jednego przykładowego dokumentu albo kliknij „Pokaż na przykładzie”.")
        return
    tekst = tekst_dokumentu(*zrodlo)

    lewa, prawa = st.columns([1, 1])
    with lewa:
        st.subheader("2. Nazwij typ")
        nazwa = st.text_input("Nazwa typu", placeholder="np. Faktura VAT", key="kreator_nazwa").strip()
        znaczniki = [z.strip() for z in st.text_input(
            "Słowa, po których program rozpozna ten dokument", placeholder="np. faktura VAT, sprzedawca, nabywca",
            help="Słowa, które są w każdym takim dokumencie, a w innych nie. Oddziel przecinkami.",
            key="kreator_znaczniki").split(",") if z.strip()]

        st.subheader("3. Wskaż dane do odczytania")
        st.markdown("Dla każdej danej: wymyśl **nazwę pola** i wklej **wartość skopiowaną z dokumentu**. "
                    "Program sam znajdzie ją w dokumencie i podświetli w podglądzie obok.")
        pola = wiersze_pol(tekst, rodzaje, ust)

    dziennik = []
    if pola:
        wyciagnij(tekst, przygotuj_typ(typ_z_formularza("podglad", "", [], pola, rodzaje), ust), dziennik)
    fragmenty = {z["pole"]: z["fragment"] for z in dziennik}
    with prawa:
        st.subheader("Podgląd dokumentu")
        strony(podglad_dokumentu(zrodlo[1], tuple((fragmenty.get(p["pole"], ""), p.get("przyklad", "")) for p in pola)))
        st.caption("Na pomarańczowo odczytane wartości; numer to kolejne pole z kroku 3.")
        with st.expander("Tekst dokumentu: stąd kopiuj wartości"):
            st.code(tekst, language=None, wrap_lines=True)

    with lewa:
        st.subheader("4. Sprawdź wynik i zapisz")
        if not (nazwa and znaczniki and pola):
            st.info("Uzupełnij krok 2 (nazwa i słowa rozpoznające) i co najmniej jedno pole w kroku 3.")
            return
        typ_id = re.sub(r"\W+", "_", nazwa.lower()).strip("_")
        try:
            tekst_yaml, wynik = typ_dla_przykladu(typ_id, nazwa, znaczniki, pola, rodzaje, tekst)
        except Exception as blad:
            st.error(f"Błąd typu: {type(blad).__name__}: {blad}")
            return
        if wynik["rozpoznany"] == typ_id:
            st.success("Program rozpoznaje przykład jako nowy typ.")
        else:
            st.warning(f"Program rozpoznaje przykład jako: {wynik['rozpoznany'] or 'nieznany dokument'}. "
                       "Dodaj w kroku 2 słowa, które są tylko w tym dokumencie.")
        st.markdown("**Odczytane dane**")
        st.json(wynik["dane"])
        przyciski = st.columns([1, 1])
        przyciski[0].download_button("Pobierz plik typu (YAML)", tekst_yaml, file_name=f"{typ_id}.yaml",
                                     mime="application/x-yaml", type="primary", width="stretch")
        if przyciski[-1].button("Użyj w zakładce „Zamień PDF na JSON”", width="stretch"):
            st.session_state.setdefault("typy_z_kreatora", {})[typ_id] = tekst_yaml
            st.session_state.pop(f"typ_{typ_id}", None)
            st.rerun()
        if st.session_state.get("typy_z_kreatora", {}).get(typ_id) == tekst_yaml:
            st.success("Ten typ jest włączony w zakładce „Zamień PDF na JSON”.")
        st.caption("Na stałe (także w CLI): zapisz pobrany plik w folderze config/typy/. Kod się nie zmienia.")
        with st.expander("Plik typu (YAML)"):
            st.code(tekst_yaml, language="yaml")


def main() -> None:
    st.set_page_config(page_title="Odwołania2JSON", page_icon=":material/description:", layout="wide")
    st.title("Odwołania2JSON")
    st.caption("Zamienia dokumenty sprawy odwoławczej do KIO (PDF, także skany) na dane JSON.")
    zakladka_analizy, zakladka_kreatora = st.tabs([":material/description: Zamień PDF na JSON",
                                                       ":material/add_circle: Dodaj nowy typ dokumentu"])
    with zakladka_analizy:
        analiza()
    with zakladka_kreatora:
        kreator()


if __name__ == "__main__":
    main()
