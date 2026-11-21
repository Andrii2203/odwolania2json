import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CYRYLICA = re.compile("[" + chr(0x400) + "-" + chr(0x4FF) + "]")
KOD = (".py", ".yaml", ".txt", ".bat", ".yml")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout


def main() -> int:
    sys.stderr.reconfigure(encoding="utf-8")
    pliki = git("diff", "--cached", "--name-only", "--diff-filter=ACM").split()
    z_cyrylica = [p for p in pliki if CYRYLICA.search(git("show", f":{p}"))]
    if z_cyrylica:
        print("Commit zablokowany: tekst nie po polsku (cyrylica) w: " + ", ".join(z_cyrylica), file=sys.stderr)
        return 1
    if any(p.endswith(KOD) for p in pliki):
        wynik = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x"], cwd=ROOT)
        if wynik.returncode != 0:
            print("Commit zablokowany: testy czerwone.", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
