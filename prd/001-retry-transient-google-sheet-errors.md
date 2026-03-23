# PRD: Retry dla tymczasowych błędów podczas przetwarzania konfiguracji

## Krótki opis zmiany
W pojedynczym przebiegu aplikacji występują sytuacje, w których podczas przetwarzania wpisu konfiguracyjnego pojawia się błąd tymczasowy (np. `421 4.3.0 Temporary System Problem`).

Celem zmiany jest dodanie mechanizmu retry, aby pojedynczy przejściowy błąd nie kończył od razu obsługi danego wpisu konfiguracyjnego.

## Kontekst
Zaobserwowany błąd:

```text
Nie udalo sie przetworzyc konfiguracji 1SyDFBbDsK1Yad_f2Ft8lwEGjvdDRdJUF6ICfc7JdNzM/Arkusz1 (growdelan@gmail.com): (421, b'4.3.0 Temporary System Problem. Try again later. For more information, go to\n4.3.0  https://support.google.com/a/answer/3221692 a640c23a62f3a-b9832f43ae8sm504602766b.6 - gsmtp')
```

Błąd ma charakter przejściowy i może ustąpić po krótkim czasie. Obecne zachowanie kończy obsługę bieżącej konfiguracji po pierwszym nieudanym podejściu.

## Problem
Przejściowe błędy integracji z usługami zewnętrznymi powodują utratę szansy na wykonanie operacji dla danego wpisu konfiguracyjnego w tym przebiegu, mimo że ponowna próba po krótkim czasie często kończy się sukcesem.

## Cel
- Zwiększyć odporność przebiegu na błędy tymczasowe.
- Ograniczyć liczbę fałszywych niepowodzeń wynikających z chwilowych problemów po stronie zewnętrznej.
- Zachować dotychczasową zasadę, że błąd jednego wpisu konfiguracyjnego nie blokuje kolejnych.

## Zakres
### W zakresie
- dodanie retry dla operacji wykonywanych w ramach obsługi pojedynczego wpisu konfiguracyjnego,
- liczba prób: maksymalnie 5,
- przerwa między próbami: 3 sekundy,
- retry uruchamiane wyłącznie dla błędów tymczasowych zgodnych z klasą błędów typu `Temporary System Problem` / kodów `421 4.3.0`,
- logowanie numeru próby i finalnego rezultatu (sukces po retry albo trwała porażka po 5 próbach).

### Poza zakresem
- zmiana logiki biznesowej porównywania cen,
- zmiana struktury danych w Google Sheets,
- zmiana szablonu e-mail,
- dodawanie własnego schedulera.

## Wymagania funkcjonalne
- System musi ponowić operację do 5 razy przy wykryciu błędu tymczasowego.
- System musi zachować 3 sekundy przerwy pomiędzy kolejnymi próbami.
- System musi przerwać retry natychmiast po pierwszej udanej próbie.
- System musi po 5 nieudanych próbach zalogować błąd i przejść do kolejnego wpisu konfiguracyjnego.
- System nie może wykonywać retry dla błędów trwałych (np. błędna konfiguracja, brak uprawnień, nieprawidłowe dane wejściowe).

## Wymagania niefunkcjonalne
- Mechanizm retry ma być deterministyczny (stała liczba prób i stały odstęp 3 sekundy).
- Logi muszą umożliwić identyfikację: typu błędu, numeru próby i końcowego statusu.
- Zmiana nie może obniżyć odporności całego przebiegu na poziomie wielu wpisów konfiguracyjnych.

## Kryteria akceptacji
- Dla błędu tymczasowego w pierwszej próbie i sukcesu w kolejnej: wpis konfiguracyjny kończy się sukcesem bez ręcznej interwencji.
- Dla 5 kolejnych błędów tymczasowych: wpis konfiguracyjny kończy się logowanym błędem, a aplikacja przetwarza następne wpisy.
- Dla błędu trwałego: brak retry i natychmiastowe przejście do standardowej obsługi błędu.
- W logach widoczna jest liczba wykonanych prób oraz informacja o końcowym wyniku.

## Ryzyka
- Zbyt szeroka klasyfikacja błędów jako tymczasowe może maskować realne problemy konfiguracji.
- Dodatkowe retry wydłużą czas przebiegu dla wpisów dotkniętych problemem tymczasowym.

## Uwagi implementacyjne (referencyjne)
- Preferowane jest wydzielenie wspólnego mechanizmu retry do warstwy aplikacyjnej, aby nie duplikować logiki.
- Klasyfikacja błędu tymczasowego powinna bazować na kodzie/statusie i treści komunikatu, nie na pojedynczym pełnym stringu.

## Status dokumentu
- Data utworzenia: 2026-03-23
- Powiązanie: przyrostowy PRD do bazowego `prd/000-initial-prd.md`
