# ADR-0017: Uruchomienie na maszynie UZP (Ubuntu, 2 vCPU)

Status: przyjęte, 2026-11-22

## Kontekst

UZP ocenia na swojej maszynie wirtualnej (`data/uzp/VM.md`): Ubuntu 24.04, 2 vCPU, 16 GB, bez GPU, Python 3.12, internet jest. Oceniający uruchamia komendę z `/opt/solution/RUN.md` z `sudo`, bez nas. Wszystko ma być w `/opt/solution`, modele pobrane wcześniej. README UZP wymaga Pythona 3.13+.

## Decyzja

1. `instaluj.sh`: `uv` (MIT/Apache) z PyPI w osobnym `.narzedzia/`, Python 3.13 z `uv` do `.python/`, zależności do `.venv/`; na końcu raz tworzymy silnik OCR, żeby pobrał modele. Wszystko w katalogu projektu.
2. `uruchom.sh`: `input/` -> `output/`; bez usług w tle, więc restart maszyny nic nie zmienia. `RUN.md` podaje komendę `sh uruchom.sh`.
3. CI: drugie zadanie na `ubuntu-24.04` z systemowym Pythonem 3.12, tak jak na maszynie UZP: `instaluj.sh`, testy, `uruchom.sh` na danych UZP, czas.
4. `.gitattributes`: `*.sh` zawsze z końcem linii LF (repozytorium powstaje na Windows).

## Konsekwencje

- Na maszynie: `git clone`, `sh instaluj.sh`, próba jak u UZP (czyste `output/`, komenda z `RUN.md`, także po `sudo reboot`).
- Bez Dockera: mniej warstw, ale Python zależy od pobrania `uv` i Pythona przy instalacji (internet jest).

## Aktualizacja 2026-11-22

- Wdrożenie: `tools/zapisz.sh` po push robi na maszynie `git pull --ff-only` i `sh instaluj.sh` (adres i klucz w `.env`: `VM_SSH`, `VM_KLUCZ`; bez nich krok pomijany). Bez crona na maszynie: po 11:00 nic się tam nie zmienia.
- GUI na maszynie: `gui.sh` (port `PORT_GUI`), start po restarcie przez `@reboot` w crontab konta zespołu (bez `sudo`).
