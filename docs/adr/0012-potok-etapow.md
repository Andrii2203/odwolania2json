# ADR-0012: Potok etapów z jedną bramką i dziennikiem

Status: przyjęte, 2026-11-21

## Kontekst

Pomiar na wariantach (ADR-0011) dał F1 0.9559. Błędy mają różne przyczyny: inna wielkość liter w nagłówku sekcji, inne etykiety, wartość sklejona z adresem i NIP-em, brak wartości. Jeden mechanizm (regex) wszystkiego nie naprawi, a dokładanie kolejnych mechanizmów bez porządku utrudni szukanie błędów.

## Decyzja

1. Program to potok 11 etapów opisany w `docs/potok.md`: wejście, tekst, widok do szukania, klasyfikacja, regex, bramka, wektory, LLM, kontekst sprawy, porządki, JSON z dziennikiem.
2. Każda wartość z każdego źródła przechodzi tę samą bramkę i musi być dosłownie w tekście.
3. Małe litery i brak polskich znaków tylko w widoku do szukania; wartość wycinamy z oryginału.
4. Etapy podłączamy po jednym. Każdy ma przełącznik w `config/ustawienia.yaml`. Etap zostaje, jeśli podnosi F1 (dane treningowe, skany, warianty) i nie daje JSON dla obcych dokumentów.
5. Dziennik: dla każdego pola etap, reguła i fragment tekstu. Pokazujemy go w GUI i przez `--wyjasnij`, nie w `output/`.
6. Stan etapów prowadzimy w tabeli w `docs/potok.md`.

## Konsekwencje

- Wiadomo, który etap dał wartość, więc błąd szukamy w jednym miejscu.
- UZP dostaje przejrzystość procesu (punktowana w README UZP) z tego samego dziennika.
- Etapy 6 (wektory) i 7 (LLM) zależą od pomiaru po etapach 2, 5 i 8; mogą nie zostać podłączone.
- Wektory: trzeba zapytać UZP, czy lokalny model embeddingów jest dozwolony i czy liczy się do średniej liczby parametrów.
