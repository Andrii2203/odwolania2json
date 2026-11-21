import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KWANTYFIKATOR = re.compile(r"\{\d+(?:,\d*)?\}")


def _liczba(w: ast.AST) -> bool:
    if isinstance(w, ast.Constant) and type(w.value) in (int, float):
        return w.value not in (0, 1)
    if isinstance(w, ast.Constant) and isinstance(w.value, str):
        return bool(KWANTYFIKATOR.search(w.value))
    return isinstance(w, ast.FormattedValue) and w.format_spec is not None and bool(re.search(r"\d", ast.unparse(w.format_spec)))


def test_t5_liczby_w_jednym_pliku():
    typy_z_cyframi = [p.name for p in (ROOT / "config" / "typy").glob("*.yaml")
                      if re.search(r"\d", p.read_text(encoding="utf-8"))]

    liczby_w_kodzie = [f"{p.relative_to(ROOT).as_posix()}:{w.lineno} {ast.unparse(w)}"
                       for katalog in ("odwolania2json", "tools", "tests") for p in (ROOT / katalog).rglob("*.py")
                       for w in ast.walk(ast.parse(p.read_text(encoding="utf-8"))) if _liczba(w)]

    linie = (ROOT / "config" / "ustawienia.yaml").read_text(encoding="utf-8").splitlines()
    bez_pochodzenia = [linia for i, linia in enumerate(linie)
                       if re.search(r"\d", linia) and not linia.lstrip().startswith("#") and " #" not in linia
                       and not (i and linie[i - 1].lstrip().startswith("#"))]

    assert (typy_z_cyframi, liczby_w_kodzie, bez_pochodzenia) == ([], [], [])
