# Roadmapa (milestones)

## Statusy milestone’ów
Dozwolone statusy:
- planned
- in_progress
- done
- blocked

---

## Milestone 0.5: Minimal end-to-end slice (done)

Cel:
- aplikacja uruchamia się jednym poleceniem
- potrafi wykonać pojedynczy przebieg dla uproszczonego zestawu danych
- zwraca wynik potwierdzający podstawowy przepływ od wejścia do decyzji biznesowej

Definition of Done:
- aplikację da się uruchomić jednym poleceniem (opisanym w README.md)
- istnieje co najmniej jeden smoke test
- testy przechodzą lokalnie
- brak placeholderów w kodzie
- minimalny przebieg potrafi odczytać stubowaną konfigurację, przetworzyć jedną pozycję i podjąć decyzję, czy wykryto obniżkę

Zakres:
- minimalny entrypoint aplikacji
- minimalna logika domenowa porównania `cena` i `przecena`
- minimalna obsługa wejścia i wyjścia na stubach
- smoke test end-to-end

---

## Milestone 1.0: Integracja z konfiguracją i arkuszami roboczymi (done)

Cel:
- aplikacja odczytuje centralny arkusz konfiguracyjny i przetwarza wiele arkuszy roboczych w jednym przebiegu

Definition of Done:
- aplikacja potrafi uwierzytelnić się do Google Sheets kontem serwisowym
- odczyt centralnego arkusza konfiguracyjnego zwraca listę wpisów do przetworzenia
- dla każdego wpisu aplikacja potrafi odczytać wskazany arkusz roboczy
- dokumentacja konfiguracji zawiera wymagane zmienne środowiskowe i sposób podłączenia konta serwisowego
- testy pokrywają odczyt konfiguracji i odczyt arkusza roboczego bez realnego IO sieciowego

Zakres:
- integracja z Google Sheets wzorowana na `../GameFlash`
- model danych dla arkusza konfiguracyjnego
- model danych dla arkusza roboczego z kolumnami `Nazwa`, `Link`, `cena`, `przecena`
- obsługa iteracji po wielu wpisach konfiguracyjnych

Uwagi:
- milestone domyka podstawę danych wejściowych dla dalszej logiki biznesowej

---

## Milestone 1.1: Pobieranie cen i kwalifikacja obniżek (done)

Cel:
- aplikacja pobiera stronę produktu z PlayStation Store, ustala cenę właściwego wariantu i aktualizuje `przecena` tylko dla realnych obniżek

Definition of Done:
- aplikacja potrafi pobrać stronę produktu z `store.playstation.com`
- logika ekstrakcji ceny działa dla monitorowanego wariantu wskazanego przez użytkownika
- porównanie ceny aktualnej z `cena` poprawnie rozróżnia brak zmiany i realną obniżkę
- aktualizacja `przecena` odbywa się przez dopasowanie po `Link`
- błędy odczytu ceny są raportowane wyłącznie w logach i nie przerywają całego przebiegu
- testy pokrywają parsowanie ceny, wariant produktu i regułę aktualizacji tylko przy niższej cenie

Zakres:
- pobieranie HTML strony produktu
- ekstrakcja ceny i interpretacja właściwego wariantu produktu
- logika domenowa porównania cen
- zapis zmian do arkusza roboczego
- logowanie błędów dotyczących pojedynczych produktów

Uwagi:
- ten milestone obejmuje główne ryzyko domenowe projektu związane ze strukturą strony PS Store

---

## Milestone 1.2: Zbiorcze powiadomienia e-mail i odporność przebiegu (planned)

Cel:
- aplikacja wysyła jeden zbiorczy e-mail na wpis konfiguracyjny i zachowuje odporność na błędy częściowe

Definition of Done:
- dla jednego wpisu konfiguracyjnego powstaje jeden e-mail zbiorczy zawierający wszystkie wykryte obniżki
- format wiadomości odwzorowuje obecny szablon z workflow `n8n`
- brak realnych obniżek nie skutkuje wysyłką błędnego powiadomienia
- błąd jednego wpisu konfiguracyjnego nie blokuje przetwarzania kolejnych wpisów
- testy pokrywają agregację zmian, generowanie wiadomości i obsługę błędów bez realnego SMTP
- README opisuje finalny sposób uruchomienia, konfiguracji i testowania

Zakres:
- agregacja zmian na poziomie wpisu konfiguracyjnego
- generowanie wiadomości e-mail zgodnej z obecnym szablonem `n8n`
- wysyłka e-mail przez SMTP
- odporność przebiegu na błędy częściowe
- finalizacja dokumentacji operacyjnej

Uwagi:
- milestone domyka pełne odwzorowanie workflow `n8n` w aplikacji Python
