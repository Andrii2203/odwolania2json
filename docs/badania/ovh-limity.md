# Limity wydatków, monitoring zużycia i zarządzanie kluczami w OVHcloud (Public Cloud i AI Endpoints)

Data: 2026-11-21

Badanie wykonano na podstawie oficjalnej dokumentacji OVHcloud (`help.ovhcloud.com`, `docs.ovhcloud.com` oraz oficjalnego repozytorium dokumentacji `github.com/ovh/docs`).

---

## 1. Czy da się ustawić twardy limit wydatków albo alert dla projektu Public Cloud i AI Endpoints?

### A. Brak twardego limitu blokującego usługę (Hard Spending Cap)
W OVHcloud Public Cloud oraz w usłudze **AI Endpoints nie istnieje funkcja twardego limitu kwotowego (hard spending cap)**, która automatycznie wyłączałaby projekt lub blokowała zapytania API po przekroczeniu określonej kwoty w EUR/USD lub po wyczerpaniu darmowego kredytu startowego.

Zgodnie z oficjalną dokumentacją (*Adding cloud credit* oraz *Information regarding Public Cloud billing options*):
1. **Kolejność rozliczania (*Pay-as-you-go*):**
   - W pierwszej kolejności zużycie jest pokrywane z **vouchera / kredytu startowego** (*Voucher balance*, np. 200 USD na start).
   - W drugiej kolejności z **kredytu chmurowego projektu** (*Cloud Credit* w sekcji `Credit & Vouchers`).
   - Po wyczerpaniu kredytu **lub po upływie jego terminu ważności** (kredyt startowy 200 USD jest ważny przez **1 miesiąc** od aktywacji projektu), każda nadwyżka jest rozliczana fakturą wystawianą **1. dnia kolejnego miesiąca** i pobierana automatycznie z domyślnej metody płatności (podpiętej karty płatniczej).
2. **Wymóg przypiętej metody płatności:**
   - Zgodnie z przewodnikiem *AI Endpoints - Getting started* (sekcja *Requirements*), klucze API wygenerowane w projekcie w trybie *Discovery mode* (bez zapisanej metody płatności) nie mogą korzystać z AI Endpoints.

### B. Co da się ustawić w panelu, aby zabezpieczyć kartę przed opłatami

W panelu OVHcloud dostępne są **trzy mechanizmy ochronne**:

#### 1. Alert przekroczenia progu wydatków (Billing Forecast Alert)
W projekcie Public Cloud można włączyć **alert e-mail** informujący o przekroczeniu ustalonego progu prognozowanych wydatków miesięcznych.
> **Ważne:** Jest to wyłącznie powiadomienie e-mail — wyzwolenie alertu **nie blokuje** klucza API ani nie zatrzymuje naliczania opłat.

**Kroki w panelu OVHcloud Control Panel:**
1. Zaloguj się do panelu **OVHcloud Control Panel** (`https://www.ovh.com/manager/`).
2. Na górnym pasku nawigacji wybierz **`Public Cloud`**, a następnie wybierz swój projekt z listy.
3. W lewym menu bocznym przewiń do sekcji **`Settings`** (*Project Management*) i kliknij **`Billing`** (*Billing control*).
4. Otwórz zakładkę **`Current usage`** (Bieżące zużycie).
5. W dolnej części ekranu, w sekcji **`Estimation of my next invoice`** (Szacowana kwota następnej faktury na 1. dzień kolejnego miesiąca), kliknij konfigurację progu alertu (ikona dzwonka / edycji progu), wpisz niski próg kwotowy (np. `1 EUR` / `1 USD` lub kwotę znacznie niższą niż posiadany kredyt) i zatwierdź.
6. Gdy bieżące lub prognozowane zużycie na koniec miesiąca przekroczy wpisany próg, OVHcloud wyśle ostrzeżenie e-mail na adres głównego kontaktu rozliczeniowego konta.

#### 2. Data automatycznego wygaśnięcia klucza API (`Expiration`) w AI Endpoints
Podczas tworzenia klucza API dla jury w usłudze AI Endpoints można ustawić twardą datę jego wygaśnięcia:
1. W lewym menu projektu Public Cloud wybierz **`AI`** (*AI & Machine Learning*) -> **`AI Endpoints`**.
2. Przejdź do zakładki **`API keys`** i kliknij **`Create an API key`** (lub **`Generate my first access key`**).
3. W formularzu oprócz pola `Name` i `Description` ustaw pole **`Expiration`** (data wygaśnięcia klucza) — np. na datę zakończenia oceny konkursowej (przed upływem 1-miesięcznej ważności darmowego kredytu 200 USD).
4. Po upływie daty `Expiration` klucz przestaje działać automatycznie i żadne zapytania nie mogą już wygenerować kosztów.

#### 3. Wbudowany limit przepustowości (Rate Limit)
Zgodnie z sekcją *Model rate limit* w przewodniku *AI Endpoints - Getting started*:
- Ruch uwierzytelniony kluczem API ma sztywny limit **400 zapytań na minutę (RPM) na projekt Public Cloud i na model** (powyżej tego limitu API zwraca błąd `HTTP 429`).
- Dla porównania: jeden pełny przebieg naszego programu na 60 sprawach treningowych (180 plików PDF) zużywa ok. **0,04–0,05 USD**. Darmowy kredyt startowy **200 USD** pokrywa ponad **4 000 pełnych przebiegów** (ok. 500–1 000 mln tokenów dla modeli `Qwen3.5-9B` i `Mistral-Small-3.2-24B-Instruct-2506`). Nawet przy ciągłym wysyłaniu 400 RPM wyczerpanie 200 USD krótkimi dokumentami KIO w trakcie oceny jury jest praktycznie niemożliwe.

---

## 2. Gdzie widać zużycie i pozostały kredyt startowy?

W panelu OVHcloud informacje te znajdują się w **trzech miejscach**:

### A. Pozostały kredyt startowy (200 USD Free Trial / Voucher) i data jego wygaśnięcia
- **Ścieżka w panelu:**
  `OVHcloud Control Panel` -> **`Public Cloud`** -> `[Twój projekt]` -> lewe menu: sekcja **`Settings`** -> **`Credit & Vouchers`** (*Credits & Vouchers*).
- **Co tam widać:**
  - Lista wszystkich aktywnych voucherów i kredytów przypisanych do projektu.
  - Kolumna z **pozostałym saldem** (*Available credit* / *Balance*) oraz **okresem ważności** (*Validity* — data początkowa i końcowa; należy pilnować tej daty, bo po jej upływie niewykorzystany kredyt przepada, a nowe zużycie obciąża kartę).

### B. Szczegółowe zużycie tokenów i koszt w AI Endpoints (na bieżąco)
- **Ścieżka w panelu:**
  `OVHcloud Control Panel` -> **`Public Cloud`** -> `[Twój projekt]` -> lewe menu: sekcja **`AI`** -> **`AI Endpoints`** -> zakładka **`Metrics`**.
- **Co tam widać:**
  - Zgodnie z sekcją *Billing and usage* w dokumentacji AI Endpoints, zakładka **`Metrics`** pokazuje w czasie zbliżonym do rzeczywistego liczbę zapytań, zużycie tokenów w podziale na modele oraz **szacowany koszt (*estimated consumption*)** samego AI Endpoints.

### C. Zbiorcze rozliczenie projektu Public Cloud w bieżącym miesiącu
- **Ścieżka w panelu:**
  `OVHcloud Control Panel` -> **`Public Cloud`** -> `[Twój projekt]` -> lewe menu: sekcja **`Settings`** -> **`Billing`**.
- **Co tam widać:**
  - Zakładka **`Current usage`**:
    - sekcja **`Already billed`** (zasoby opłacane z góry w abonamencie miesięcznym),
    - sekcja **`Future bills`** (zasoby *Pay-as-you-go* naliczone od 1. dnia bieżącego miesiąca do dziś),
    - sekcja **`Estimation of my next invoice`** (prognoza faktury na 1. dzień kolejnego miesiąca wraz z ustawieniem alertu e-mail).
  - Zakładka **`History`**: zamknięte rozliczenia projektu z poprzednich miesięcy.

---

## 3. Jak unieważnić klucz API po hackathonie (oraz jak całkowicie zamknąć projekt i odpiąć kartę)?

### Krok 1: Natychmiastowe unieważnienie (usunięcie) klucza API w AI Endpoints
Zgodnie z sekcją *Revoke your API access key* w oficjalnym przewodniku *AI Endpoints - Getting started*:
1. Zaloguj się do **OVHcloud Control Panel** i otwórz **`Public Cloud`** -> `[Twój projekt]`.
2. W lewym menu w sekcji **`AI`** kliknij **`AI Endpoints`**.
3. Otwórz zakładkę **`API keys`**. Zobaczysz tabelę ze wszystkimi wygenerowanymi kluczami (`Name`, `Description`, `Creation`, `Expiration`).
4. W wierszu klucza, który chcesz unieważnić, wybierz akcję **`Delete`** (ikona kosza / przycisk akcji po prawej stronie wiersza).
5. W oknie dialogowym **`Delete API key`** potwierdź usunięcie przyciskiem **`Delete`**.
6. **Weryfikacja:** Klucz jest unieważniany natychmiast. Każda próba wywołania API z usuniętym kluczem zwraca błąd `403 Forbidden: Authentication Failed`.

> **Uwaga z dokumentacji dotycząca projektów współdzielonych:** Jeśli projekt Public Cloud został udostępniony innemu kontu OVHcloud NIC z uprawnieniami *Read & Write*, administrator projektu nie widzi na liście kluczy wygenerowanych przez innych użytkowników. Dlatego klucz przekazywany w rozwiązaniu konkursowym zawsze generujemy z głównego konta właściciela projektu.

### Krok 2 (opcjonalnie po zakończeniu oceny jury): Usunięcie projektu Public Cloud i odpięcie karty
Dopóki projekt Public Cloud jest aktywny, OVHcloud wymaga zachowania co najmniej jednej domyślnej metody płatności. Aby po zakończeniu konkursu mieć 100% gwarancji braku jakichkolwiek przyszłych obciążeń i usunąć kartę z konta:
1. **Usuń projekt Public Cloud** (*GDPR - How to immediately delete your OVHcloud services* -> sekcja *Public Cloud Project*):
   - Przejdź do **`Public Cloud`** -> `[Twój projekt]` -> w lewym menu na dole w sekcji **`Settings`** kliknij **`Project settings`** (*Project Management*).
   - Kliknij **`Delete project`** i zatwierdź przyciskiem **`Yes, cancel`**.
   - Otwórz skrzynkę e-mail głównego konta OVHcloud i **kliknij link potwierdzający w wiadomości od OVHcloud**, aby sfinalizować natychmiastowe usunięcie projektu.
2. **Usuń kartę płatniczą z konta OVHcloud** (*Managing payment methods* -> sekcja *Delete a payment method*):
   - Po usunięciu projektu (gdy na koncie nie ma aktywnych usług w `My offers and services` ani nierozliczonych płatności) kliknij swoją nazwę użytkownika w prawym górnym rogu panelu i wybierz **`My payment methods`**.
   - Kliknij przycisk **`...`** (lub ikonę kosza) po prawej stronie zapisanej karty płatniczej i wybierz **`Delete this payment method`**.

---

## 4. Źródła (oficjalna dokumentacja OVHcloud)

1. **AI Endpoints – Getting started** (wymóg metody płatności, tworzenie klucza z datą `Expiration`, unieważnianie klucza w zakładce `API keys` -> `Delete`, limit 400 RPM, monitoring w zakładce `Metrics`):
   - Strona dokumentacji: https://help.ovhcloud.com/csm/en-public-cloud-ai-endpoints-getting-started
   - Wersja Markdown (`docs.ovhcloud.com`): https://docs.ovhcloud.com/en/guides/public-cloud/ai-machine-learning/ai-endpoints-getting-started.md
2. **AI Endpoints – Billing and lifecycle** (zasady rozliczania modeli AI Endpoints i powiadomienia):
   - Źródło w oficjalnym repozytorium `ovh/docs`: https://github.com/ovh/docs/blob/develop/pages/public_cloud/ai_machine_learning/endpoints_guide_04_billing_concept/guide.en-gb.md
3. **Information regarding Public Cloud billing options** (model *Pay-as-you-go*, rozliczanie 1. dnia miesiąca, podgląd `Billing` -> `Current usage` / `Future bills` / `Estimation of my next invoice` oraz konfiguracja alertu progowego e-mail):
   - Źródło w oficjalnym repozytorium `ovh/docs`: https://github.com/ovh/docs/blob/develop/pages/public_cloud/public_cloud_cross_functional/analyze_billing/guide.en-gb.md
4. **Adding cloud credit** (sekcja `Settings` -> `Credit & Vouchers`, kolejność pobierania środków: najpierw voucher startowy ważny 1 miesiąc, potem kredyt projektu, a następnie domyślna metoda płatności):
   - Strona dokumentacji: https://help.ovhcloud.com/csm/en-account-vouchers-cloud-credit
   - Źródło w oficjalnym repozytorium `ovh/docs`: https://github.com/ovh/docs/blob/develop/pages/account_and_service_management/managing_billing_payments_and_services/add_cloud_credit_to_project/guide.en-gb.md
5. **GDPR – How to immediately delete your OVHcloud services** (procedura natychmiastowego usunięcia projektu Public Cloud: `Project settings` -> `Delete project` + potwierdzenie e-mail):
   - Źródło w oficjalnym repozytorium `ovh/docs`: https://github.com/ovh/docs/blob/develop/pages/account_and_service_management/managing_billing_payments_and_services/how_to_permanently_delete_services/guide.en-gb.md
6. **Managing payment methods** (zarządzanie kartami płatniczymi i ich usuwanie w `My payment methods` -> `Delete this payment method`):
   - Źródło w oficjalnym repozytorium `ovh/docs`: https://github.com/ovh/docs/blob/develop/pages/account_and_service_management/managing_billing_payments_and_services/manage-payment-methods/guide.en-gb.md
