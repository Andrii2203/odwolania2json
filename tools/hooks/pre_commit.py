import subprocess
import sys
import unicodedata

from wspolne import KOD, ROOT, git


def z_cyrylica(tekst: str) -> bool:
    return any(unicodedata.name(znak, "").startswith("CYRILLIC") for znak in set(tekst))


def main() -> int:
    sys.stderr.reconfigure(encoding="utf-8")
    pliki = git("diff", "--cached", "--name-only", "--diff-filter=ACM").splitlines()
    bledne = [p for p in pliki if z_cyrylica(git("show", f":{p}"))]
    if bledne:
        print("Commit zablokowany: tekst nie po polsku (cyrylica) w: " + ", ".join(bledne), file=sys.stderr)
        return 1
    if any(p.endswith(KOD) for p in pliki):
        wynik = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x"], cwd=ROOT)
        if wynik.returncode != 0:
            print("Commit zablokowany: testy czerwone.", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
