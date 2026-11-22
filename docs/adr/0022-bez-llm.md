# ADR-0022: Bez LLM w potoku

Status: przyjęte, 2026-11-22; dotyczy etapu 7 z ADR-0012

## Kontekst

Klucz OVHcloud (Mistral-Small 24B, serwery w UE, ADR-0004) działa. Reguły z YAML dają F1 0.9990 na danych treningowych, 0.9508 na skanach UZP, 0.9902 na nowym typie (TED, ADR-0020). Mały model NER (GLiNER2) dał 0.551 (`docs/badania/gliner2.md`). LLM nie mierzyliśmy.

## Decyzja

LLM nie używamy. Powody:

1. „Niczego nie wymyślamy”: LLM może zwrócić wartość, której nie ma w dokumencie.
2. Przejrzystość (premiowana przez UZP): dla każdej wartości reguła i fragment tekstu (`--wyjasnij`, GUI).
3. Punkty za model: README UZP: same lokalne modele w oczekiwanym czasie = 20 pkt; model przez API liczony według parametrów.
4. Ocena na maszynie UZP bez nas: bez sieci, limitów API i zmienności odpowiedzi; ten sam wejściowy PDF daje zawsze ten sam JSON (testy).
5. Lokalnie się nie da: 2 vCPU bez GPU, hosting modelu przez osobę prywatną zabroniony.

## Konsekwencje

- Jedyny model to OCR (RapidOCR, lokalnie).
- Możliwe użycie później (bez pomiaru nie włączamy): pola puste po regułach, tylko gdy wartość jest dosłownie w tekście; mianownik imion i nazwisk.
