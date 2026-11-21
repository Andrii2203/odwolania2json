import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout


def main() -> int:
    sys.stderr.reconfigure(encoding="utf-8")
    dane = json.load(sys.stdin)
    sciezka = dane.get("tool_input", {}).get("file_path", "")
    try:
        wzgledna = Path(sciezka).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return 0
    if not wzgledna.startswith("tests/"):
        return 0
    opis_zmieniony = git("status", "--porcelain", "--", "docs/testy.md").strip()
    opis_w_ostatnim = "docs/testy.md" in git("diff", "--name-only", "HEAD~1", "HEAD").split()
    if opis_zmieniony or opis_w_ostatnim:
        return 0
    print("Najpierw opisz test w docs/testy.md (TDD). Test bez opisu nie powstaje.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
