import json
import subprocess
import sys

from wspolne import KOD, ROOT, git


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    dane = json.loads(sys.stdin.read() or "{}")
    if dane.get("stop_hook_active"):
        return 0
    if git("log", "--oneline", "@{u}..HEAD").strip():
        git("push", "-q")
    zmienione = git("diff", "--name-only", "HEAD").splitlines() + git("ls-files", "--others", "--exclude-standard").splitlines()
    kod = [p for p in zmienione if p.endswith(KOD) and not p.startswith("docs/")]
    if not kod:
        return 0
    wynik = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "--tb=line"], cwd=ROOT, capture_output=True, text=True)
    if wynik.returncode != 0:
        print(json.dumps({"decision": "block", "reason": "Testy czerwone. Napraw przed zakończeniem:\n" + wynik.stdout},
                         ensure_ascii=False))
        return 0
    print(json.dumps({"systemMessage": "Testy zielone. Niezacommitowane: " + ", ".join(kod)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
