# ADR-0006: GUI „PDF i JSON obok siebie” oraz prezentacja

Status: przyjęte, 2026-11-21 (wybór biblioteki GUI po sprawdzeniu)

## Kontekst

- FAQ UZP: GUI nie jest obowiązkowe, ale daje punkty. Ideał: wgranie PDF, uruchomienie analizy, podgląd JSON; najlepiej dokument i dane obok siebie.
- Końcowe zgłoszenie w HackTribe wymaga prezentacji (PDF do 10 MB). Finał (top 3) to pokaz przed jury.
- UZP premiuje przejrzystość ekstrakcji (widać, skąd pochodzi wartość).

## Decyzja

Oba punkty są w planie z wykonawcą i terminem (`docs/STAN.md`), a nie „jeśli zdążymy”.

1. GUI osobno od CLI: `gui.bat` i `requirements-gui.txt`, żeby CLI na komputerze jury pozostało lekkie.
   - Kandydat: Streamlit (Apache 2.0): wgrywanie pliku, dwie kolumny, podgląd JSON. Strony PDF pokazujemy jako obrazy.
   - GUI wywołuje tę samą funkcję `przetworz()` z `odwolania2json/pipeline.py` co CLI; logika jest jedna.
   - Przykład ekranu: po lewej strona `pelnomocnictwo.pdf`, po prawej `{"pelnomocnicy": [{"imie_nazwisko": "Krystyna Mazowiecka", …}]}`.
   - Później: przy każdym polu fragment tekstu, z którego pochodzi wartość.
2. Prezentacja (PDF do 10 MB): problem, jak działa (na przykładzie), F1 na danych treningowych, jak dodać nowy typ przez YAML, technologie.

## Konsekwencje

- Streamlit jest ciężki (ponad 100 MB zależności), dlatego osobny `requirements-gui.txt`.
