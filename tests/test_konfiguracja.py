import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_t5_liczby_w_jednym_pliku():
    typy_z_cyframi = [p.name for p in (ROOT / "config" / "typy").glob("*.yaml")
                      if re.search(r"\d", p.read_text(encoding="utf-8"))]

    liczby_w_kodzie = [f"{p.name}:{w.lineno} {w.value}" for p in (ROOT / "odwolania2json").glob("*.py")
                       for w in ast.walk(ast.parse(p.read_text(encoding="utf-8")))
                       if isinstance(w, ast.Constant) and type(w.value) in (int, float) and w.value not in (0, 1)]

    linie = (ROOT / "config" / "ustawienia.yaml").read_text(encoding="utf-8").splitlines()
    bez_pochodzenia = [linia for i, linia in enumerate(linie)
                       if re.search(r"\d", linia) and not linia.lstrip().startswith("#") and " #" not in linia
                       and not (i and linie[i - 1].lstrip().startswith("#"))]

    assert (typy_z_cyframi, liczby_w_kodzie, bez_pochodzenia) == ([], [], [])
