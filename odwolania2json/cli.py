import argparse
import json
import sys
from pathlib import Path

from .pipeline import load_types, process

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
        result = process(pdf, types)
        if result is None:
            print(f"pominięto (nieznany typ): {rel}")
            continue
        typ, data = result
        dst = args.output / rel.with_suffix(".json")
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{rel} → {typ}")
    return 0
