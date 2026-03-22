# Aktualny stan projektu

## Co działa
- aplikacja uruchamia się poleceniem `uv run main.py`
- aplikacja czyta centralny arkusz konfiguracyjny Google Sheets
- aplikacja potrafi odczytać wskazane arkusze robocze i policzyć pozycje do dalszego przetwarzania
- testy dla odczytu konfiguracji i arkuszy roboczych przechodzą lokalnie

## Co jest skończone
- przygotowano bazowy PRD w `prd/000-initial-prd.md`
- uzupełniono `spec.md` oraz `ROADMAP.md` zgodnie z bazowym PRD
- zrealizowano Milestone 0.5
- zrealizowano Milestone 1.0
- opisano konfigurację Google Sheets, uruchomienie i testy w `README.md`

## Co jest w trakcie
- brak aktywnej implementacji kolejnego milestone'u

## Co jest następne
- Milestone 1.1: pobieranie stron produktów i ekstrakcja cen
- porównanie ceny wykrytej z `cena` dla właściwego wariantu produktu
- aktualizacja pola `przecena` w arkuszu roboczym

## Blokery i ryzyka
- obecny przebieg nie pobiera jeszcze stron `store.playstation.com`
- główne ryzyko domenowe pozostaje w ekstrakcji ceny i dopasowaniu właściwego wariantu produktu ze strony PS Store
- powodzenie kolejnych etapów zależy od poprawnej konfiguracji dostępu do Google Sheets i później SMTP poza repozytorium

## Ostatnie aktualizacje
- dodano integrację z Google Sheets w `storage/google_sheets.py`
- przebudowano `main.py` do odczytu konfiguracji i arkuszy roboczych
- dodano testy `tests/test_milestone_1_0.py`
- oznaczono Milestone 1.0 jako `done` w `ROADMAP.md`
