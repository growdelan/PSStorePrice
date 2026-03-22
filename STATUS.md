# Aktualny stan projektu

## Co działa
- aplikacja uruchamia się poleceniem `uv run main.py`
- aplikacja czyta centralny arkusz konfiguracyjny Google Sheets
- aplikacja pobiera strony produktow z `store.playstation.com`
- aplikacja wybiera monitorowany wariant po `cena` i wspiera dopasowanie po `Nazwa`
- aplikacja pomija wariant trialowy (`Game Trial` / `Wersja próbna gry`) i bierze pierwsza platna opcje ponizej
- aplikacja obsluguje ceny zapisywane jako `zł`, `£` i `€`
- aplikacja aktualizuje `przecena` jako liczbe oraz przywraca ja do ceny bazowej po zakonczeniu promocji
- aplikacja agreguje zmiany per wpis konfiguracyjny i wysyla jeden zbiorczy e-mail
- błąd jednego wpisu konfiguracyjnego nie blokuje przetwarzania kolejnych
- testy dla odczytu konfiguracji, parsowania cen, aktualizacji przecen i wysylki e-mail przechodzą lokalnie

## Co jest skończone
- przygotowano bazowy PRD w `prd/000-initial-prd.md`
- uzupełniono `spec.md` oraz `ROADMAP.md` zgodnie z bazowym PRD
- zrealizowano Milestone 0.5
- zrealizowano Milestone 1.0
- zrealizowano Milestone 1.1
- zrealizowano Milestone 1.2
- opisano konfigurację Google Sheets, uruchomienie i testy w `README.md`

## Co jest w trakcie
- brak aktywnej implementacji

## Co jest następne
- brak kolejnych milestone'ow w aktualnej roadmapie
- ewentualne dalsze zmiany wymagaja nowego PRD lub aktualizacji roadmapy

## Blokery i ryzyka
- główne ryzyko domenowe pozostaje w ekstrakcji ceny i dopasowaniu właściwego wariantu produktu ze strony PS Store
- poprawne dzialanie produkcyjne zalezy od konfiguracji dostepu do Google Sheets i SMTP poza repozytorium
- zmiana struktury strony PS Store moze wymagac aktualizacji parsera cen

## Ostatnie aktualizacje
- dodano warstwe e-maili w `emails/notifications.py`
- rozszerzono `main.py` o agregacje zmian, wysylke powiadomien i obsluge bledow czesciowych
- dodano testy `tests/test_milestone_1_2.py`
- oznaczono Milestone 1.2 jako `done` w `ROADMAP.md`
- poprawiono parser cen dla walut `£` i `€`
- dodano obsluge wariantu trialowego w PlayStation Store
- poprawiono zapis `przecena`, aby byl liczba i wracal do ceny bazowej po zakonczeniu promocji
