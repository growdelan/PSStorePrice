# Specyfikacja techniczna

## Cel
PSStorePrice to aplikacja Python przeznaczona do automatycznego monitorowania cen produktów w PlayStation Store na podstawie danych utrzymywanych w Google Sheets.

Aplikacja rozwiązuje problem ręcznego sprawdzania promocji dla wielu pozycji zapisanych w różnych arkuszach roboczych. Jej odbiorcą jest właściciel prywatnego workflow, który zarządza konfiguracją i listami produktów przez Google Sheets.

Zakres obejmuje odczyt centralnego arkusza konfiguracyjnego, przetwarzanie wielu arkuszy roboczych, sprawdzanie cen na `store.playstation.com`, aktualizację pola `przecena` wyłącznie przy realnej obniżce względem ceny bazowej oraz wysyłkę zbiorczego e-maila z wykrytymi zmianami. Poza zakresem pozostają panel UI, własny scheduler, obsługa innych sklepów oraz przechowywanie sekretów w repozytorium.

---

## Zakres funkcjonalny (high-level)
Kluczowe use-case'i:
- operator utrzymuje centralny arkusz konfiguracyjny z listą przebiegów do wykonania,
- operator utrzymuje arkusze robocze z produktami i ceną bazową dla wskazanego wariantu produktu,
- aplikacja wykonuje jednorazowy przebieg i przetwarza wszystkie aktywne wpisy konfiguracyjne,
- aplikacja aktualizuje `przecena` dla pozycji, dla których cena w PS Store spadła poniżej `cena`,
- aplikacja wysyła zbiorczy e-mail do odbiorcy przypisanego do danego wpisu konfiguracyjnego.

Główne przepływy:
- odczyt konfiguracji przebiegów z Google Sheets,
- odczyt list produktów z arkusza roboczego,
- pobranie strony produktu i ustalenie aktualnej ceny dla właściwego wariantu,
- porównanie ceny aktualnej z ceną bazową,
- zapis zmian do arkusza roboczego,
- agregacja zmian i wysyłka powiadomienia e-mail.

Aplikacja **nie**:
- zarządza harmonogramem uruchomień,
- nie udostępnia interfejsu użytkownika,
- nie monitoruje sklepów innych niż PlayStation Store,
- nie raportuje braku ceny przez e-mail, jeśli cena nie została wykryta.

---

## Architektura i przepływ danych
1. Główne komponenty systemu
   - warstwa konfiguracji i uruchomienia pojedynczego przebiegu,
   - integracja z Google Sheets dla arkusza konfiguracyjnego i arkuszy roboczych,
   - warstwa pobierania stron produktów z PlayStation Store,
   - warstwa ekstrakcji i interpretacji ceny dla monitorowanego wariantu produktu,
   - warstwa porównania cen i kwalifikacji obniżek,
   - warstwa powiadomień e-mail.

2. Przepływ danych między komponentami
   - aplikacja uruchamia pojedynczy przebieg i pobiera listę konfiguracji z centralnego arkusza,
   - dla każdej konfiguracji pobierany jest wskazany arkusz roboczy z listą produktów,
   - dla każdego produktu aplikacja pobiera stronę z `store.playstation.com` i ustala aktualną cenę,
   - wynik porównania z wartością `cena` decyduje o aktualizacji pola `przecena`,
   - zmienione rekordy są agregowane w ramach jednego wpisu konfiguracyjnego,
   - po zakończeniu przetwarzania danej konfiguracji generowany i wysyłany jest jeden e-mail zbiorczy.

3. Granice odpowiedzialności
   - Google Sheets pozostaje źródłem prawdy dla konfiguracji i bieżącego stanu monitorowanych pozycji,
   - aplikacja odpowiada za wykonanie logiki biznesowej monitoringu cen i przygotowanie powiadomień,
   - zewnętrzny harmonogram odpowiada za uruchamianie aplikacji o określonych porach,
   - SMTP odpowiada wyłącznie za dostarczenie wiadomości, a nie za logikę wyboru zmian.

---

## Komponenty techniczne
- entrypoint aplikacji uruchamiający pojedynczy przebieg i obsługujący kolejność kroków,
- komponent konfiguracji odpowiedzialny za odczyt ustawień środowiskowych i dostępu do usług zewnętrznych,
- komponent Google Sheets odpowiedzialny za odczyt arkusza konfiguracyjnego, odczyt danych roboczych i zapis zmian,
- komponent pobierania stron PlayStation Store odpowiedzialny za wykonywanie żądań HTTP do stron produktów,
- komponent ekstrakcji ceny odpowiedzialny za odczyt ceny z HTML oraz interpretację właściwego wariantu produktu,
- komponent logiki domenowej odpowiedzialny za porównanie ceny aktualnej z ceną bazową i decyzję o aktualizacji `przecena`,
- komponent e-mail odpowiedzialny za wygenerowanie wiadomości zgodnej z obecnym szablonem z workflow `n8n`,
- warstwa logowania odpowiedzialna za diagnostykę przebiegu i raportowanie błędów do logów.

---

## Decyzje techniczne
- Decyzja: źródłem konfiguracji przebiegów i danych roboczych są Google Sheets.
- Uzasadnienie: wynika to bezpośrednio z PRD odtwarzającego dotychczasowy workflow `n8n` oraz z potrzeby zachowania modelu pracy operatora bez zmiany sposobu zarządzania danymi.
- Konsekwencje: poprawność działania zależy od dostępności arkuszy, poprawnego modelu kolumn i poprawnej autoryzacji konta serwisowego.

- Decyzja: aplikacja działa w trybie pojedynczego przebiegu, a harmonogram uruchamiania jest realizowany poza aplikacją.
- Uzasadnienie: PRD wyraźnie wyklucza własny scheduler i traktuje harmonogram jako odpowiedzialność warstwy zewnętrznej.
- Konsekwencje: rozwiązanie pozostaje prostsze operacyjnie, ale wymaga osobnej konfiguracji crona lub innego mechanizmu uruchamiania.

- Decyzja: aktualizacja `przecena` i wysyłka powiadomienia następują wyłącznie przy cenie niższej od wartości bazowej `cena`.
- Uzasadnienie: to podstawowa reguła biznesowa opisana w PRD.
- Konsekwencje: aplikacja nie raportuje wszystkich zmian ceny, lecz wyłącznie realne obniżki względem wartości referencyjnej.

- Decyzja: aplikacja ma uwzględniać wariant produktu wskazany przez użytkownika w arkuszu roboczym.
- Uzasadnienie: PRD określa, że użytkownik wskazuje monitorowany wariant, a cena bazowa odnosi się do tego konkretnego wariantu.
- Konsekwencje: poprawność detekcji promocji będzie zależna od zgodności danych arkusza z wariantem dostępnym na stronie produktu.

- Decyzja: wiadomość e-mail ma odwzorowywać obecny szablon używany w workflow `n8n`.
- Uzasadnienie: PRD wskazuje zachowanie obecnego formatu komunikacji jako wymaganie produktu.
- Konsekwencje: warstwa powiadomień musi obsłużyć format wiadomości zgodny z dotychczasowym oczekiwaniem, a nie jedynie minimalny komunikat tekstowy.

- Decyzja: w Milestone 0.5 wszystkie wejścia i wyjścia zewnętrzne są zastąpione stubami w pamięci.
- Uzasadnienie: roadmapa dla etapu 0.5 wymaga minimalnego działającego przebiegu end-to-end bez wdrażania jeszcze integracji z Google Sheets, HTTP i SMTP.
- Konsekwencje: pierwszy slice potwierdza przepływ logiki biznesowej i uruchamialność aplikacji, ale nie realizuje jeszcze docelowych integracji zewnętrznych.

- Decyzja: centralny arkusz konfiguracyjny w Milestone 1.0 uzywa kolumn `dokument`, `arkusz` i `email`.
- Uzasadnienie: to najprostsze odwzorowanie danych wejściowych wynikające z przekazanego workflow `n8n`.
- Konsekwencje: aplikacja oczekuje dokladnie takiego modelu wejscia dla konfiguracji przebiegow, a ewentualna zmiana nazewnictwa kolumn bedzie wymagac aktualizacji integracji.

- Decyzja: konfiguracja dostepu do Google Sheets jest dostarczana wylacznie przez zmienne srodowiskowe `GOOGLE_CONFIG_SHEET_ID`, `GOOGLE_CONFIG_WORKSHEET` oraz `GSPREAD_SERVICE_ACCOUNT_FILE`.
- Uzasadnienie: wynika to z wymagan operacyjnych repo oraz potrzeby unikniecia fallbackow i danych dostepowych zaszytych w kodzie.
- Konsekwencje: uruchomienie aplikacji poza testami wymaga jawnej konfiguracji srodowiska przed startem.

- Decyzja: w Milestone 1.1 wybor monitorowanego wariantu produktu odbywa sie na podstawie ceny bazowej z kolumny `cena`, z dodatkowym wsparciem dopasowania do `Nazwa`.
- Uzasadnienie: PRD wskazuje, ze uzytkownik identyfikuje monitorowany wariant przez pozycje wpisana w arkuszu i jej cene referencyjna, bez wprowadzania dodatkowej kolumny wariantu.
- Konsekwencje: gdy strona zawiera wiele edycji o podobnych nazwach, poprawne dopasowanie zalezy od zgodnosci `Nazwa` i `cena` z rzeczywistym wariantem na stronie PS Store.

---

## Jakość i kryteria akceptacji
Wspólne wymagania jakościowe:
- aplikacja uruchamia się jednym poleceniem opisanym w `README.md`,
- przebieg jest idempotentny dla niezmienionych cen,
- błąd pojedynczego produktu nie przerywa przetwarzania pozostałych produktów,
- błąd pojedynczego wpisu konfiguracyjnego nie blokuje przetwarzania kolejnych wpisów,
- brak możliwości wykrycia ceny jest raportowany wyłącznie w logach,
- sekrety są dostarczane przez zmienne środowiskowe lub plik konta serwisowego poza repozytorium,
- testy obejmują logikę porównania cen, obsługę arkuszy oraz generowanie powiadomień bez realnego IO zewnętrznego.

Kryteria akceptacji:
- aplikacja potrafi odczytać centralny arkusz konfiguracyjny i przetworzyć więcej niż jeden arkusz roboczy w jednym przebiegu,
- dla pozycji z niższą ceną niż `cena` aktualizowane jest pole `przecena`,
- dla pozycji bez realnej obniżki nie są wysyłane powiadomienia,
- dla jednego wpisu konfiguracyjnego powstaje jeden zbiorczy e-mail z listą zmian,
- format wiadomości jest zgodny z dotychczasowym szablonem `n8n`,
- dokumentacja uruchomienia i konfiguracji odpowiada rzeczywistemu sposobowi działania aplikacji.

---

## Zasady zmian i ewolucji
- zmiany funkcjonalne → aktualizacja `ROADMAP.md`
- zmiany architektoniczne → aktualizacja tej specyfikacji
- nowe zależności → wpis do `## Decyzje techniczne`
- refactory tylko w ramach aktualnego milestone’u

---

## Powiązanie z roadmapą
- Szczegóły milestone’ów i ich statusy znajdują się w `ROADMAP.md`.
- Roadmapa prowadzi od minimalnego przebiegu end-to-end przez integrację z Google Sheets i logikę monitoringu cen do pełnego odwzorowania powiadomień e-mail zgodnych z workflow `n8n`.

---

## Status specyfikacji
- Data utworzenia: 2026-03-22
- Ostatnia aktualizacja: 2026-03-22
- Aktualny zakres obowiązywania: bazowy zakres produktu wynikający z `prd/000-initial-prd.md`
