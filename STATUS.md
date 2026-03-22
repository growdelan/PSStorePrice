# Aktualny stan projektu

## Co działa
- aplikacja uruchamia się poleceniem `uv run main.py`
- minimalny przebieg end-to-end działa na stubowanej konfiguracji i stubowanych danych w pamięci
- logika domenowa potrafi wykryć obniżkę przez porównanie ceny bazowej i bieżącej
- smoke testy dla minimalnego przebiegu przechodzą lokalnie

## Co jest skończone
- przygotowano bazowy PRD w `prd/000-initial-prd.md`
- uzupełniono `spec.md` oraz `ROADMAP.md` zgodnie z bazowym PRD
- zrealizowano Milestone 0.5
- opisano uruchomienie i testy w `README.md`

## Co jest w trakcie
- brak aktywnej implementacji kolejnego milestone'u

## Co jest następne
- Milestone 1.0: integracja z centralnym arkuszem konfiguracyjnym Google Sheets
- odczyt arkuszy roboczych użytkowników
- przygotowanie konfiguracji środowiskowej dla konta serwisowego Google

## Blokery i ryzyka
- obecny przebieg korzysta wyłącznie ze stubów i nie weryfikuje jeszcze integracji z Google Sheets
- główne ryzyko domenowe pozostaje w ekstrakcji ceny i dopasowaniu właściwego wariantu produktu ze strony PS Store
- powodzenie kolejnych etapów zależy od poprawnej konfiguracji dostępu do Google Sheets i SMTP poza repozytorium

## Ostatnie aktualizacje
- dodano minimalny bootstrap aplikacji w `main.py`
- dodano smoke test w `tests/test_smoke.py`
- oznaczono Milestone 0.5 jako `done` w `ROADMAP.md`
- utrwalono decyzję techniczną o użyciu stubów w Milestone 0.5
