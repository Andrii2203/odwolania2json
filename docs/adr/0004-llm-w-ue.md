# ADR-0004: LLM – model z otwartymi wagami w UE

Status: zaproponowane (potrzebny klucz; rejestracja w Scaleway 21.11 zwraca HTTP 500)

## Kontekst

FAQ UZP: tylko modele open source, które można też zainstalować lokalnie; API u dostawcy, którego firma i serwer są w UE; dane nie opuszczają UE. Komputer testowy jest bez GPU, więc duży model lokalny odpada. Klucz API oddajemy razem z rozwiązaniem.

## Decyzja (propozycja, według `docs/badania/llm-ue.md`)

- Dostawca: Scaleway (Francja). Zapytania nie są przechowywane ani używane do trenowania; 1 mln tokenów za darmo (wymagana karta).
- Model: `mistral-small-3.2-24b-instruct` (Apache 2.0). Jest też w OVHcloud i IONOS; to dostawcy zapasowi z tym samym modelem.
- Mistral Free odpada: domyślnie trenuje na zapytaniach. Mistral tylko w planie płatnym.
- Adres API, model i klucz w `.env`. Zmiana dostawcy to 3 linie, kod ten sam.
- F1 mierzymy przez to samo API co u jury: przebieg 60 spraw kosztuje ok. 0,05 EUR, a nasz F1 jest wtedy równy ich F1.
- Dane z badania sprawdzamy skryptem: z kluczem zapytanie `GET /v1/models` pokaże, jakie modele są dostępne.
- LLM wywołujemy tylko dla pól, których nie wyciągną reguły (ADR-0002).

## Do sprawdzenia przed przyjęciem

- Czy model ma otwarte wagi i jest obsługiwany w UE.
- Osobny klucz z limitem wydatków (klucz trafia do jury).

## Rozwój lokalnie

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
