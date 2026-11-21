import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KOD = (".py", ".yaml", ".txt", ".bat", ".yml")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    dane = json.loads(sys.stdin.read() or "{}")
    if dane.get("stop_hook_active"):
        return 0
    status = subprocess.run(["git", "status", "--porcelain", "-uall"], cwd=ROOT, capture_output=True, text=True).stdout
    kod = [linia[3:] for linia in status.splitlines() if linia[3:].endswith(KOD) and not linia[3:].startswith("docs/")]
    if not kod:
        return 0
    wynik = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x"], cwd=ROOT, capture_output=True, text=True)
    if wynik.returncode != 0:
        print("Testy czerwone. Napraw przed zakończeniem:\n" + "\n".join(wynik.stdout.splitlines()[-15:]), file=sys.stderr)
        return 2
    print(json.dumps({"systemMessage": "Testy zielone. Niezacommitowane: " + ", ".join(kod)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
