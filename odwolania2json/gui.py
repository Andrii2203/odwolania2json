import sys
import tempfile
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


def main() -> None:
    st.set_page_config(page_title="Odwołania2JSON", layout="wide")
    st.title("Odwołania2JSON")

    typy, ust = wczytaj_typy(), ustawienia()
    pliki = st.file_uploader(
        "Wgraj jeden lub kilka plików PDF",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if not pliki:
        st.info("Wybierz pliki PDF, aby rozpocząć analizę.")
        return

    with tempfile.TemporaryDirectory() as katalog:
        for plik in pliki:
            sciezka = Path(katalog) / Path(plik.name).name
            sciezka.write_bytes(plik.getvalue())

            st.subheader(plik.name)
            with st.spinner(f"Przetwarzanie pliku {plik.name}..."):
                obrazy = obrazy_stron(sciezka)
                dzienniki = {}
                _, wynik, blad = next(przetworz_wszystkie([sciezka], typy, ust, dzienniki))

            lewa, prawa = st.columns([1, 1])

            with lewa:
                for nr, obraz in enumerate(obrazy, start=1):
                    st.image(obraz, caption=f"Strona {nr}", use_container_width=True)

            with prawa:
                if blad is not None:
                    st.error(f"Błąd przetwarzania: {type(blad).__name__}: {blad}")
                elif wynik is None:
                    st.warning("Nieznany typ dokumentu: plik JSON z {}")
                else:
                    typ, dane = wynik
                    st.markdown(f"**Typ dokumentu:** `{typ}`")
                    st.json(dane)
                    with st.expander("Skąd każda wartość (reguła i fragment tekstu)"):
                        st.table([{"pole": w["pole"], "wartość": str(w["wartosc"]), "reguła": w["regula"],
                                   "tekst": w["fragment"]} for w in dzienniki.get(sciezka, [])])


if __name__ == "__main__":
    main()
