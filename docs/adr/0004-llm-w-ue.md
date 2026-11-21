# ADR-0004: LLM – model z otwartymi wagami w UE

Status: przyjęte dla dostawcy OVHcloud (klucz działa od 21.11); model wybierzemy pomiarem F1. W OVH nie ma twardego limitu wydatków (`docs/badania/ovh-limity.md`), więc limit tokenów jest w programie (`config/ustawienia.yaml`).

## Kontekst

FAQ UZP: tylko modele open source, które można też zainstalować lokalnie; API u dostawcy, którego firma i serwer są w UE; dane nie opuszczają UE. Discord i README UZP, 21.11: firma musi mieć politykę prywatności z zakresem i miejscem przetwarzania danych; hosting modelu przez osobę prywatną (np. na własnym komputerze) jest zabroniony. OVHcloud to spełnia. Komputer testowy jest bez GPU, więc duży model lokalny odpada. Klucz API oddajemy razem z rozwiązaniem.

## Decyzja (propozycja, według `docs/badania/llm-ue.md`, aktualizacja 21.11)

- Dostawca: OVHcloud AI Endpoints (Francja). Zero data retention, 400 zapytań na minutę, structured output, 200 USD kredytu na start (wymagana metoda płatności). Scaleway odpada: rejestracja 21.11 zwraca HTTP 500.
- Model: wybieramy pomiarem F1 spośród dwóch (Apache 2.0, oba w OVHcloud):
  - `Mistral-Small-3.2-24B-Instruct-2506` (0,10 / 0,31 USD za 1 mln tokenów),
  - `Qwen3.5-9B` (0,12 / 0,18 USD), ta sama rodzina co lokalny Qwen3.5-4B.
- Dostawca zapasowy: IONOS (Niemcy, te same dwa modele).
- Mistral odpada w planie Free (domyślnie trenuje na zapytaniach) i nie ma już w API Mistral Small 3.2.
- Adres API, model i klucz w `.env`. Zmiana dostawcy to 3 linie, kod ten sam.
- F1 mierzymy przez to samo API co u jury: przebieg 60 spraw kosztuje ok. 0,05 EUR, a nasz F1 jest wtedy równy ich F1.
- Dane z badania sprawdzamy skryptem: z kluczem zapytanie `GET /v1/models` pokaże, jakie modele są dostępne.
- LLM wywołujemy tylko dla pól, których nie wyciągną reguły (ADR-0002).

## Do sprawdzenia przed przyjęciem

- Czy model ma otwarte wagi i jest obsługiwany w UE.
- Osobny klucz z limitem wydatków (klucz trafia do jury).

## Rozwój lokalnie

Tylko do eksperymentów; w rozwiązaniu dla jury model lokalny u osoby prywatnej jest zabroniony.

W `E:\call to ai` jest `tools\llama.cpp\llama-server.exe` (CUDA) i modele `models\brain\*.gguf`. Na RTX 5060 (8 GB):

```
llama-server.exe -m Qwen3.5-4B-Q8_0.gguf -ngl 99 --port 8080   ->   http://localhost:8080/v1
```

To samo API zgodne z OpenAI co u dostawcy. Różnica jest tylko w `.env`:

```
LLM_BASE_URL=http://localhost:8080/v1          (rozwój)
LLM_BASE_URL=https://api.<dostawca-UE>/v1      (jury)
```

- Klient własny, ok. 20 linii na `urllib`: z biblioteki `openai` potrzebne jest jedno zapytanie.
- Lokalny Qwen3.5-4B tylko do szybkich prób promptów; F1 mierzymy modelem z API.
- Wbudowanie modelu w rozwiązanie dla komputera jury (CPU) odpada: 4,5 GB i minuty na dokument.

## Konsekwencje

- Bez klucza program działa (tylko reguły); LLM tylko podnosi F1.
