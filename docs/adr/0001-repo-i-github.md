# ADR-0001: Co jest w repozytorium, a co trafia na GitHub

Status: przyjęte, 2026-11-21

## Kontekst

W `e:\hacknation` leżą materiały wszystkich 15 zadań hackathonu, dane treningowe UZP (19 MB PDF) i będzie klucz API. Link do GitHuba jest potrzebny do szkicu i oddania.

## Decyzja

- Katalog główny repozytorium: `e:\hacknation`.
- `docs/<KOD>/` (materiały zadań) tylko lokalnie, w `.gitignore`. Z `docs/` do git trafiają tylko nasze pliki: `adr/`, `badania/`, `testy.md`, `STAN.md`.
- `data/uzp/` to klon publicznego repozytorium UZP; nie commitujemy go, instrukcja klonowania jest w `AGENTS.md`.
- `input/` i `output/` w katalogu głównym (wymóg UZP), zawartości nie commitujemy.
- Klucz API w `.env`, nie commitujemy.

## Konsekwencje

- Repozytorium jest małe, bez cudzych materiałów i sekretów.
- Testy wymagające danych są pomijane, jeśli nie ma `data/uzp` (z wyjaśnieniem).
