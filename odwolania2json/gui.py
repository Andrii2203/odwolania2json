import sys
import tempfile
from pathlib import Path

import pypdfium2 as pdfium
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from odwolania2json.pipeline import load_types, process


def render_pages(pdf_path: Path) -> list:
    doc = pdfium.PdfDocument(str(pdf_path))
    try:
        return [page.render().to_pil() for page in doc]
    finally:
        doc.close()


def main() -> None:
    st.set_page_config(page_title="Odwołania2JSON", layout="wide")
    st.title("Odwołania2JSON")

    typy = load_types()
    pliki = st.file_uploader(
        "Wgraj jeden lub kilka plików PDF",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if not pliki:
        st.info("Wybierz pliki PDF, aby rozpocząć analizę.")
        return

    with tempfile.TemporaryDirectory() as tmp_dir:
        for plik in pliki:
            sciezka = Path(tmp_dir) / Path(plik.name).name
            sciezka.write_bytes(plik.getvalue())

            st.subheader(plik.name)
            with st.spinner(f"Przetwarzanie pliku {plik.name}..."):
                obrazy = render_pages(sciezka)
                wynik = process(sciezka, typy)

            lewa, prawa = st.columns([1, 1])

            with lewa:
                for idx, obraz in enumerate(obrazy, start=1):
                    st.image(obraz, caption=f"Strona {idx}", use_container_width=True)

            with prawa:
                if wynik is None:
                    st.warning("Nieznany typ dokumentu")
                else:
                    typ, dane = wynik
                    st.markdown(f"**Typ dokumentu:** `{typ}`")
                    st.json(dane)


if __name__ == "__main__":
    main()
