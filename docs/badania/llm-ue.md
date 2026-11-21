# Badanie dostawcow LLM w UE (do ADR-0004)

Data: 2026-11-21

## Wymagania UZP
1. **Model:** wylacznie open source / open-weight z mozliwoscia instalacji lokalnej oraz **licencja bez ograniczen komercyjnych** (`Apache 2.0` lub `MIT`).
   > Modele z niestandardowymi licencjami (*Llama 3.3 Community License*, *Mistral Ecosystem Open Weight License* dla `Mistral Large 4`, *NVIDIA Open Model License* czy *Premier* dla `Codestral`) odrzucamy.
2. **Infrastruktura i jurysdykcja:** zarowno firma, jak i serwery API musza znajdowac sie **na terenie Unii Europejskiej** (zgodnosc z RODO/GDPR, brak podlegania pod US CLOUD Act).
3. **Poufnosc danych:** zapytania i dokumenty nie moga byc uzywane do trenowania modeli.
4. **Integracja:** API zgodne ze standardem OpenAI (`/v1/chat/completions`), aby zmiana dostawcy wymagala wylacznie zmiany `.env` (`LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`).

---

## 1. Odpowiedz na pytanie o modele lokalne: `Qwen3.5-4B` oraz `Gemma 4 E4B`

Zweryfikowano bezposrednio przez API Hugging Face (`https://huggingface.co/api/models`) oraz katalogi wszystkich 4 dostawcow:

| Model lokalny | Oficjalne repozytorium wag | Licencja | Czy hostowany przez API u dostawcow w UE? | Najblizszy odpowiednik w API dostawcow (ta sama rodzina i licencja Apache 2.0) |
|---|---|---|---|---|
| **`Qwen3.5-4B`** | `Qwen/Qwen3.5-4B`<br>(`unsloth/Qwen3.5-4B-GGUF`) | **Apache 2.0** (`license:apache-2.0`) | **Nie** (wariant 4B nie jest oferowany w serverless API zadnego z 4 dostawcow) | **`Qwen3.5-9B`** (Apache 2.0, kontekst 262k):<br>- **OVHcloud:** $0.12 / $0.18 za 1M tokenow<br>- **IONOS:** $0.11 / $0.17 za 1M tokenow |
| **`Gemma 4 E4B`** | `google/gemma-4-E4B-it` | **Apache 2.0** (`license:apache-2.0` — w odroznieniu od starszej serii Gemma 3, cala seria Gemma 4 jest na Apache 2.0) | **Nie** w wariancie `E4B` | **`gemma-4-26b-a4b`** (MoE 26B, 4B aktywnych parametrow, Apache 2.0, kontekst 256k):<br>- **OVHcloud:** $0.10 / $0.41 za 1M tokenow |

---

## 2. Porownanie 4 dostawcow w UE (dane z oficjalnych stron i katalogow z dnia 2026-11-21)

| Kryterium | Mistral AI (La Plateforme / Studio) | Scaleway Generative APIs | OVHcloud AI Endpoints | IONOS AI Model Hub |
|---|---|---|---|---|
| **Firma i serwery w UE** | **Tak** (Mistral AI SAS, Paryz, Francja; serwery w UE) | **Tak** (Scaleway SAS / Iliad Group, Paryz, Francja; DC Paryz `fr-par`) | **Tak** (OVH Groupe SA, Roubaix, Francja; DC w UE, certyfikaty ISO 27001 / SecNumCloud) | **Tak** (IONOS Cloud GmbH, Montabaur, Niemcy; DC w Niemczech `de-txl` / `de-fra`) |
| **Aktywne modele tekstowe na licencji Apache 2.0 / MIT** | - `mistral-small-2603` (**Mistral Small 4**, MoE 119B/6.5B akt., Apache 2.0)<br>- `ministral-8b-2512` (**Ministral 3 8B**, Apache 2.0)<br>- `ministral-14b-2512` (**Ministral 3 14B**, Apache 2.0)<br>- `ministral-3b-2512` (**Ministral 3 3B**, Apache 2.0)<br>- `deepseek-v4.1-flash-1017` (MIT)<br>- `zai-glm-5.3` / `5.3-flash` (MIT) | - `mistral-small-3.2-24b-instruct-2506` (Apache 2.0)<br>- `qwen3.6-35b-a3b` (Apache 2.0)<br>- `qwen3.8-27b` (Apache 2.0)<br>- `qwen3.5-397b-a17b` (Apache 2.0)<br>- `qwen3-235b-a22b-instruct-2507` (Apache 2.0) | - `Mistral-Small-3.2-24B-Instruct-2506` (Apache 2.0)<br>- `Qwen3.5-9B` (Apache 2.0)<br>- `gemma-4-26b-a4b` (Apache 2.0)<br>- `qwen3-vl-30b-a3b` (Apache 2.0)<br>- `qwen3.6-35b-a3b` (Apache 2.0)<br>- `Qwen3.8-27B` (Apache 2.0)<br>- `Qwen3.5-397B-A17B` (Apache 2.0)<br>- `gpt-oss-20b` / `gpt-oss-120b` (Apache 2.0)<br>- `DeepSeek-V4.1-Flash-1017` (MIT)<br>- `Olala-v1.0-mini-7A1B` (Apache 2.0) | - `Qwen3.5-9B` (Apache 2.0)<br>- `Mistral Small 24B Instruct` (Apache 2.0)<br>- `Qwen3.8-27B` (Apache 2.0)<br>- `Qwen3.5-397B-A17B` (Apache 2.0)<br>- `Qwen3-Coder-Next (80B)` (Apache 2.0)<br>- `gpt-oss-120b` (Apache 2.0) |
| **Cena za 1M tokenow (wejscie / wyjscie)** | - `Mistral Small 4`: **$0.15 / $0.60**<br>- `Ministral 3 8B`: **$0.15 / $0.15** | - `mistral-small-3.2-24b`: **0,15 EUR / 0,35 EUR**<br>- `qwen3.6-35b-a3b`: **0,25 EUR / 1,50 EUR**<br>- `qwen3.8-27b`: **0,60 EUR / 3,30 EUR** | - `gpt-oss-20b`: **$0.05 / $0.18**<br>- `gpt-oss-120b`: **$0.09 / $0.47**<br>- `Mistral-Small-3.2-24B`: **$0.10 / $0.31**<br>- `gemma-4-26b-a4b`: **$0.10 / $0.41**<br>- `Qwen3.5-9B`: **$0.12 / $0.18**<br>- `qwen3.6-35b-a3b`: **$0.20 / $1.33**<br>- `Qwen3.8-27B`: **$0.47 / $3.19**<br>- `Olala-v1.0-mini-7A1B`: **Free ($0.00)** | - `Qwen3.5-9B`: **$0.11 / $0.17** (~0,10/0,15 EUR)<br>- `Mistral Small 24B`: **$0.11 / $0.33** (~0,10/0,30 EUR)<br>- `gpt-oss-120b`: **$0.17 / $0.71**<br>- `Qwen3-Coder-Next 80B`: **$0.17 / $0.89**<br>- `Qwen3.8-27B`: **$0.45 / $2.70**<br>- `Qwen3.5-397B-A17B`: **$0.67 / $4.00** |
| **Darmowy limit (Free Tier / Trial)** | Plan **Free** bez karty (niskie limity RPS/TPM) | Pierwszy **1 000 000 tokenow** za darmo (wymagana weryfikacja konta i karta; uwaga: 21.11 rejestracja zwracala HTTP 500) | 1. **Tryb bez klucza / Playground** (z limitem zapytan na IP) oraz darmowy model `Olala-v1.0-mini-7A1B`<br>2. **US$ 200** kredytu startowego na pierwszy projekt Public Cloud (wazny 1 miesiac, wymagana zapisana metoda platnosci) | Brak stalego darmowego planu dla samego API (kredyty startowe tylko przy pelnej rejestracji konta IONOS Cloud) |
| **Czy darmowy plan trenuje na danych?** | **TAK (domyslnie w planie Free** — wymagany reczny Opt-out w ustawieniach prywatnosci lub przejscie na plan platny PAYG) | **NIE** (Zero Data Retention zarowno dla darmowego miliona tokenow, jak i ruchu platnego) | **NIE** (*"Zero data retention: Your data is never used to train our models, and we only keep what is strictly necessary for billing"*) | **NIE** (dane nie sa uzywane do trenowania modeli; zgodnosc z RODO i EU AI Act) |
| **Adres API zgodnego z OpenAI** | `https://api.mistral.ai/v1` | `https://api.scaleway.ai/v1` | `https://oai.endpoints.kepler.ai.cloud.ovh.net/v1` | `https://openai.inference.de-txl.ionos.com/v1` |

---

## 3. Szczegoly wedlug dostawcow

### 3.1. OVHcloud AI Endpoints (Francja)
- **Kluczowe fakty z oficjalnego katalogu (`https://www.ovhcloud.com/en/public-cloud/ai-endpoints/catalog/`):**
  - Katalog obejmuje 33 modele, z czego najwazniejsze modele tekstowe z licencja **Apache 2.0** i obsluga **Structured Output** (wymuszanie poprawnego schematu JSON) to:
    1. `Mistral-Small-3.2-24B-Instruct-2506` (24B, bf16, kontekst 128K) — **$0.10 / 1M wejscie**, **$0.31 / 1M wyjscie**.
    2. `Qwen3.5-9B` (9.7B, int4, kontekst 262K, Reasoning + Vision + Structured Output) — **$0.12 / 1M wejscie**, **$0.18 / 1M wyjscie**.
    3. `gemma-4-26b-a4b` (26B MoE / 4B akt., fp4, kontekst 256K, Reasoning + Structured Output) — **$0.10 / 1M wejscie**, **$0.41 / 1M wyjscie**.
    4. `gpt-oss-20b` (21B, fp4, kontekst 131K, Apache 2.0) — **$0.05 / 1M wejscie**, **$0.18 / 1M wyjscie** oraz `gpt-oss-120b` (117B, fp4, Apache 2.0) — **$0.09 / 1M wejscie**, **$0.47 / 1M wyjscie**.
    5. `Olala-v1.0-mini-7A1B` (6.8B, bf16, kontekst 32K, Apache 2.0, Structured Output) — **$0.00 (Free)**.
  - Limit przepustowosci w trybie Base (z kluczem API): **400 zapytan na minute (RPM)** na projekt, SLA 99,5%.
  - Tryb Batch (beta): 50% taniej.
  - Nowy projekt Public Cloud otrzymuje **US$ 200 darmowego kredytu** na 1 miesiac po podpieciu metody platnosci.
- **Zrodla:**
  - Strona glowna i specyfikacja: https://www.ovhcloud.com/en/public-cloud/ai-endpoints/
  - Katalog modeli i cennik: https://www.ovhcloud.com/en/public-cloud/ai-endpoints/catalog/
  - Dokumentacja: https://help.ovhcloud.com/csm/en-public-cloud-ai-endpoints-getting-started

### 3.2. Mistral AI — La Plateforme / Mistral Studio (Francja)
- **Kluczowe fakty z oficjalnej dokumentacji (`https://docs.mistral.ai/getting-started/models/models_overview/`):**
  - **Wazna zmiana cyklu zycia modeli w 2026 r.:** Bezposrednio w API Mistral AI starsze modele `Mistral Small 3.1` (`mistral-small-2503`), `Mistral Small 3.2` (`mistral-small-2506`) oraz `Mistral Nemo 12B` (`open-mistral-nemo-2407`) zostaly juz wycofane (*Retired* odpowiednio 30.11.2025 oraz 31.07.2026).
  - Aktualnie aktywne modele z otwartymi wagami na licencji **Apache 2.0** w API Mistral AI to:
    1. **`Mistral Small 4`** (ID API: `mistral-small-2603`, wydany 16.03.2026, architektura hybrydowa MoE: 119B parametrow lacznie / 6,5B aktywnych, kontekst **256k**, pelne wsparcie `Structured Outputs`): **$0.15 / 1M wejscie**, **$0.60 / 1M wyjscie**.
    2. **`Ministral 3 8B`** (ID API: `ministral-8b-2512`, wydany 02.12.2025, kontekst **256k**, `Structured Outputs`): **$0.15 / 1M wejscie**, **$0.15 / 1M wyjscie**.
    3. **`Ministral 3 14B`** (`ministral-14b-2512`, Apache 2.0) oraz **`Ministral 3 3B`** (`ministral-3b-2512`, Apache 2.0).
  - *Uwaga licencyjna:* `Mistral Large 4` (`26.10`) korzysta z *Mistral Ecosystem Open Weight License* (z ograniczeniami komercyjnymi), a `Codestral` (`25.08`) ma licencje *Premier* — obu nie uzywamy.
  - *Prywatnosc:* Na stronie cennika (`https://mistral.ai/pricing`) opcja `Model training: Opt-out` jest dostepna, ale w darmowym planie trzeba ja jawnie wylaczyc w panelu lub uzywac konta z podpietymi kredytami PAYG.
- **Zrodla:**
  - Wykaz aktywnych i wycofanych modeli: https://docs.mistral.ai/getting-started/models/models_overview/
  - Karta i cena `Mistral Small 4`: https://docs.mistral.ai/models/mistral-small-4-0-26-03
  - Karta i cena `Ministral 3 8B`: https://docs.mistral.ai/models/ministral-3-8b-25-12
  - Cennik i plany: https://mistral.ai/pricing

### 3.3. IONOS AI Model Hub (Niemcy)
- **Kluczowe fakty z oficjalnej dokumentacji (`https://docs.ionos.com/cloud/ai/ai-model-hub/models` oraz `https://cloud.ionos.com/managed/ai-model-hub`):**
  - W pazdzierniku 2026 r. wycofano starsze modele `Mistral Nemo (12B)` (22.10.2026) oraz `Llama 3.1 8B` (15.10.2026), zastepujac je modelem **`Qwen3.5-9B`**.
  - Aktualnie aktywne modele jezykowe na licencji **Apache 2.0**:
    1. **`Qwen3.5-9B`** (kontekst 262k, tekst + obraz, Tool Calling) — **$0.11 / 1M wejscie**, **$0.17 / 1M wyjscie** (~0,10 / 0,15 EUR).
    2. **`Mistral Small 24B Instruct`** (kontekst 128k, tekst + obraz, Tool Calling) — **$0.11 / 1M wejscie**, **$0.33 / 1M wyjscie** (~0,10 / 0,30 EUR).
    3. **`gpt-oss-120b`** (kontekst 128k, Apache 2.0) — **$0.17 / 1M wejscie**, **$0.71 / 1M wyjscie**.
    4. **`Qwen3-Coder-Next (80B)`** (kontekst 128k, Apache 2.0) — **$0.17 / 1M wejscie**, **$0.89 / 1M wyjscie**.
    5. **`Qwen3.8-27B`** (kontekst 262k, Apache 2.0) — **$0.45 / 1M wejscie**, **$2.70 / 1M wyjscie**.
    6. **`Qwen3.5-397B-A17B`** (MoE 397B / 17B akt., kontekst 262k, Apache 2.0) — **$0.67 / 1M wejscie**, **$4.00 / 1M wyjscie**.
  - Wszystkie modele maja domyslnie wlaczone *Prefix caching* (przyspiesza kolejne zapytania ze stalym promptem systemowym).
- **Zrodla:**
  - Strona produktu i tabela cen: https://cloud.ionos.com/managed/ai-model-hub
  - Lista aktywnych i wycofanych modeli: https://docs.ionos.com/cloud/ai/ai-model-hub/models
  - Porownanie parametrow modeli: https://docs.ionos.com/cloud/ai/ai-model-hub/models/models-comparison.md
  - Opisy modeli LLM: https://docs.ionos.com/cloud/ai/ai-model-hub/models/llms.md
  - Polityka danych i EU AI Act: https://docs.ionos.com/cloud/ai/ai-model-hub/governance-and-compliance.md

### 3.4. Scaleway Generative APIs (Francja)
- **Kluczowe fakty:**
  - Serwery w Paryzu (`fr-par`), polityka Zero Data Retention, kompatybilnosc z OpenAI (`https://api.scaleway.ai/v1`), darmowy 1 mln tokenow po weryfikacji konta.
  - Dostepne modele Apache 2.0: `mistral-small-3.2-24b-instruct-2506` (0,15 EUR / 0,35 EUR za 1M tokenow), `qwen3.6-35b-a3b` (0,25 EUR / 1,50 EUR), `qwen3.8-27b` (0,60 EUR / 3,30 EUR), `qwen3.5-397b-a17b` (0,60 EUR / 3,60 EUR).
  - *Ryzyko operacyjne:* w dniu 21.11.2026 rejestracja nowego konta w Scaleway zwracala blad HTTP 500 (odnotowane w ADR-0004).
- **Zrodla:**
  - Strona uslugi: https://www.scaleway.com/en/generative-apis/
  - Cennik MaaS: https://www.scaleway.com/en/pricing/model-as-a-service/
  - Dokumentacja wspieranych modeli: https://www.scaleway.com/en/docs/ai-data/generative-apis/reference-content/supported-models/

---

## 4. Wnioski i rekomendacja do ADR-0004

1. **Jesli rejestracja w Scaleway nadal zwraca HTTP 500**, najlepszym dostawca pierwszego wyboru jest **OVHcloud AI Endpoints** (`https://oai.endpoints.kepler.ai.cloud.ovh.net/v1`) lub **Mistral AI Studio w planie PAYG** (`https://api.mistral.ai/v1`):
   - W **OVHcloud** mamy zarowno `Mistral-Small-3.2-24B-Instruct-2506` ($0.10 / $0.31), jak i `Qwen3.5-9B` ($0.12 / $0.18 — bezposredni starszy brat naszego lokalnego `Qwen3.5-4B`) oraz `gemma-4-26b-a4b` ($0.10 / $0.41 — rodzina Gemma 4 na Apache 2.0), z gwarancja *Zero Data Retention* i limitem 400 RPM.
   - W **Mistral AI** aktualnym odpowiednikiem na licencji Apache 2.0 jest **`mistral-small-2603` (Mistral Small 4)** ($0.15 / $0.60) lub **`ministral-8b-2512` (Ministral 3 8B)** ($0.15 / $0.15).
2. **Koszt uruchomienia:** pelny przebieg na 60 sprawach treningowych (ok. 240 tys. tokenow wejsciowych i 30 tys. wyjsciowych) kosztuje **ok. 0,03 - 0,05 EUR** w kazdym z czterech serwisow.
