# Aktualny stan projektu

## Co działa
- aplikacja uruchamia się poleceniem `uv run main.py`
- aplikacja czyta centralny arkusz konfiguracyjny Google Sheets
- aplikacja pobiera strony produktow z `store.playstation.com`
- aplikacja wybiera monitorowany wariant po `cena` i wspiera dopasowanie po `Nazwa`
- aplikacja aktualizuje pole `przecena` tylko dla realnych obnizek
- testy dla odczytu konfiguracji, parsowania cen i aktualizacji przecen przechodzą lokalnie

## Co jest skończone
- przygotowano bazowy PRD w `prd/000-initial-prd.md`
- uzupełniono `spec.md` oraz `ROADMAP.md` zgodnie z bazowym PRD
- zrealizowano Milestone 0.5
- zrealizowano Milestone 1.0
- zrealizowano Milestone 1.1
- opisano konfigurację Google Sheets, uruchomienie i testy w `README.md`

## Co jest w trakcie
- brak aktywnej implementacji kolejnego milestone'u

## Co jest następne
- Milestone 1.2: zbiorcze powiadomienia e-mail
- agregacja zmian na poziomie pojedynczego wpisu konfiguracyjnego
- odporność przebiegu na błędy częściowe i finalizacja operacyjna

## Blokery i ryzyka
- główne ryzyko domenowe pozostaje w ekstrakcji ceny i dopasowaniu właściwego wariantu produktu ze strony PS Store
- powodzenie kolejnych etapów zależy od poprawnej konfiguracji dostępu do Google Sheets i później SMTP poza repozytorium
- aplikacja nie wysyła jeszcze e-maili, więc operator nie otrzymuje zbiorczych powiadomien po przebiegu

## Ostatnie aktualizacje
- dodano scraper `scrapers/playstation_store.py`
- rozszerzono `main.py` o pobieranie cen i aktualizację `przecena`
- dodano testy `tests/test_milestone_1_1.py`
- oznaczono Milestone 1.1 jako `done` w `ROADMAP.md`
