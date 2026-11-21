import argparse
import json
import sys
from pathlib import Path

from .pipeline import classify, extract, load_types, pdf_text

ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="odwolania2json",
                                 description="PDF (odwołanie, pełnomocnictwo, przelew) → JSON")
    ap.add_argument("--input", type=Path, default=ROOT / "input")
    ap.add_argument("--output", type=Path, default=ROOT / "output")
    ap.add_argument("--config", type=Path, default=ROOT / "config" / "typy")
    args = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    types = load_types(args.config)
    for pdf in sorted(args.input.rglob("*.pdf")):
        rel = pdf.relative_to(args.input)
        text = pdf_text(pdf)
        typ = classify(text, types)
        if typ is None:
            print(f"pominięto (nieznany typ): {rel}")
            continue
        dst = args.output / rel.with_suffix(".json")
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(json.dumps(extract(text, typ), ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{rel} → {typ['typ']}")
    return 0
