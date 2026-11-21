import json
import sys
from pathlib import Path

from wspolne import ROOT, git


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    dane = json.load(sys.stdin)
    sciezka = dane.get("tool_input", {}).get("file_path", "")
    try:
        wzgledna = Path(sciezka).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return 0
    if not wzgledna.startswith("tests/"):
        return 0
    opis_zmieniony = git("status", "--porcelain", "--", "docs/testy.md").strip()
    opis_w_ostatnim = "docs/testy.md" in git("show", "--name-only", "--format=", "HEAD").splitlines()
    if opis_zmieniony or opis_w_ostatnim:
        return 0
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse", "permissionDecision": "deny",
        "permissionDecisionReason": "Najpierw opisz test w docs/testy.md (TDD). Test bez opisu nie powstaje."}},
        ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
