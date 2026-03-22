# PRD: PSStorePrice

## Krótki opis produktu
PSStorePrice to aplikacja Python odtwarzająca prywatny workflow wcześniej realizowany w `n8n`. Jej zadaniem jest cykliczne sprawdzanie cen produktów zapisanych w Google Sheets, wykrywanie realnych obniżek na `store.playstation.com`, aktualizowanie informacji w odpowiednich arkuszach oraz wysyłanie zbiorczych powiadomień e-mail.

## Kontekst
Dotychczasowy proces działał jako workflow w `n8n` i opierał się na arkuszu konfiguracyjnym oraz arkuszach roboczych w Google Sheets. Rozwiązanie spełniało swoją funkcję, ale było związane z konkretnym narzędziem automatyzacyjnym i trudniejsze do dalszego utrzymania, rozwijania oraz testowania.

Celem nowego rozwiązania jest przeniesienie tego procesu do samodzielnej aplikacji Python, która zachowa dotychczasową logikę biznesową, ale będzie prostsza w utrzymaniu, uruchamianiu i dalszym rozwoju.

## Problem
Operator utrzymuje listy produktów PlayStation Store w różnych arkuszach Google Sheets. Ręczne sprawdzanie aktualnych cen dla każdej pozycji jest czasochłonne i podatne na błędy. Dodatkowo konfiguracja monitoringu jest rozproszona pomiędzy wieloma arkuszami, co utrudnia regularne wykonywanie procesu.

Potrzebne jest rozwiązanie, które:
- centralnie odczyta konfigurację przebiegów z jednego arkusza,
- automatycznie sprawdzi aktualne ceny na stronie PlayStation Store,
- zaktualizuje zapisane promocje tylko wtedy, gdy rzeczywiście pojawi się niższa cena,
- poinformuje odbiorcę e-mailowego o wykrytych zmianach.

## Użytkownik i odbiorca
Docelowym użytkownikiem jest właściciel prywatnego workflow do śledzenia promocji w PS Store. Zarządza on listami produktów, arkuszami roboczymi i odbiorcami powiadomień przez Google Sheets. System nie jest projektowany jako narzędzie wieloosobowe ani jako produkt z interfejsem dla użytkowników końcowych.

## Cele
- Odtworzyć istniejący workflow `n8n` w formie aplikacji Python.
- Zachować model pracy oparty na arkuszu konfiguracyjnym i wielu arkuszach roboczych.
- Automatycznie wykrywać realne obniżki cen produktów z `store.playstation.com`.
- Aktualizować dane w Google Sheets w sposób zgodny z obecnym procesem biznesowym.
- Wysyłać zbiorcze powiadomienia e-mail dla zmian wykrytych w danym przebiegu.

## Zakres
### W zakresie
- odczyt arkusza konfiguracyjnego Google Sheets jako listy zadań do wykonania,
- iteracja po wielu wpisach konfiguracyjnych w jednym przebiegu,
- odczyt wskazanego dokumentu i zakładki roboczej dla każdego wpisu konfiguracyjnego,
- przetwarzanie wierszy zawierających co najmniej `Nazwa`, `Link`, `cena`, `przecena`,
- pobieranie strony produktu z adresu zapisane w kolumnie `Link`,
- ekstrakcja aktualnej ceny ze strony `store.playstation.com`,
- porównanie wykrytej ceny z wartością bazową `cena`,
- aktualizacja pola `przecena` tylko wtedy, gdy wykryta cena jest niższa od `cena`,
- agregacja wszystkich zmian dla pojedynczego wpisu konfiguracyjnego,
- wysyłka jednego zbiorczego e-maila do odbiorcy wskazanego w konfiguracji.

### Poza zakresem
- panel administracyjny lub interfejs użytkownika,
- własny scheduler w aplikacji,
- przechowywanie sekretów w repozytorium,
- obsługa sklepów innych niż PlayStation Store,
- zaawansowane raportowanie historyczne zmian cen,
- zarządzanie użytkownikami, rolami lub uprawnieniami w samej aplikacji.

## Przebieg użytkowy
1. Zewnętrzny harmonogram uruchamia aplikację w trybie jednorazowego przebiegu.
2. Aplikacja odczytuje arkusz konfiguracyjny Google Sheets.
3. Dla każdego wpisu konfiguracyjnego pobierane są:
   - identyfikator dokumentu Google Sheets,
   - nazwa zakładki roboczej,
   - adres e-mail odbiorcy powiadomienia.
4. Aplikacja odczytuje wszystkie pozycje z danego arkusza roboczego.
5. Dla każdego wiersza pobierana jest strona produktu z kolumny `Link`.
6. Aplikacja wyznacza aktualną cenę produktu na podstawie zawartości strony PlayStation Store.
7. Aktualna cena jest porównywana z wartością w kolumnie `cena`.
8. Jeżeli wykryta cena jest niższa od `cena`, aplikacja aktualizuje pole `przecena`.
9. Zmodyfikowane pozycje są agregowane do jednej listy zmian dla danego wpisu konfiguracyjnego.
10. Po zakończeniu przetwarzania danego arkusza roboczego aplikacja wysyła zbiorczy e-mail z wykrytymi obniżkami.

## Źródła danych
### Arkusz konfiguracyjny
Arkusz konfiguracyjny jest źródłem listy przebiegów do wykonania. Każdy wpis definiuje co najmniej:
- identyfikator dokumentu Google Sheets,
- nazwę zakładki roboczej,
- adres e-mail odbiorcy powiadomienia.

Arkusz konfiguracyjny pełni rolę centralnego punktu sterowania przebiegami aplikacji.

### Arkusze robocze
Każdy arkusz roboczy zawiera listę monitorowanych produktów. Minimalny oczekiwany model danych obejmuje kolumny:
- `Nazwa`,
- `Link`,
- `cena`,
- `przecena`.

Kolumna `Link` jest kluczem dopasowania przy aktualizacji wiersza.
Użytkownik wskazuje w arkuszu konkretny wariant produktu, który chce monitorować. Wartość bazowa `cena` odnosi się do tego właśnie wariantu i to względem niej aplikacja ma identyfikować właściwy produkt oraz oceniać, czy wystąpiła obniżka.

## Integracje
### Google Sheets
Google Sheets jest podstawowym źródłem konfiguracji i danych roboczych. Aplikacja ma korzystać z integracji opartej na koncie serwisowym, zgodnie ze wzorcem wykorzystywanym w projekcie `../GameFlash`.

### Store.PlayStation.com
Aplikacja pobiera strony produktów ze wskazanych adresów URL i na ich podstawie ustala aktualną cenę widoczną dla monitorowanej pozycji.

### SMTP / e-mail
Aplikacja wysyła wiadomości e-mail do odbiorcy zdefiniowanego w arkuszu konfiguracyjnym. E-mail ma zawierać zbiorczą listę wykrytych zmian dla jednego przebiegu konfiguracji.
Format wiadomości powinien odzwierciedlać obecny szablon używany w workflow `n8n`, a nie być jedynie uproszczonym powiadomieniem tekstowym.

## Wymagania funkcjonalne
- System musi odczytywać arkusz konfiguracyjny jako listę niezależnych wpisów do przetworzenia.
- System musi obsługiwać wiele arkuszy roboczych w ramach jednego uruchomienia.
- System musi odczytywać z arkusza roboczego co najmniej nazwę produktu, link, cenę bazową i aktualną przecenę.
- System musi pobierać stronę produktu dla każdego wiersza zawierającego link.
- System musi wyznaczać aktualną cenę produktu na podstawie danych ze strony PlayStation Store.
- System musi uwzględniać wariant produktu wskazany przez użytkownika w arkuszu roboczym i interpretować cenę bazową `cena` jako cenę referencyjną dla tego konkretnego wariantu.
- System musi porównywać wykrytą cenę z wartością `cena`.
- System musi aktualizować `przecena` tylko wtedy, gdy wykryta cena jest niższa od ceny bazowej.
- System nie może wysyłać powiadomienia dla pozycji, dla których nie wykryto realnej obniżki.
- System musi grupować wszystkie zmiany z jednego arkusza roboczego do jednego e-maila.
- System musi wysyłać e-mail do odbiorcy przypisanego do danego wpisu konfiguracyjnego.
- System musi odwzorowywać układ i charakter wiadomości e-mail znany z obecnego workflow `n8n`.

## Wymagania niefunkcjonalne
- Aplikacja ma działać idempotentnie dla niezmienionych cen.
- Błąd pojedynczego produktu nie może przerywać całego przebiegu.
- Błąd pojedynczego wpisu konfiguracyjnego nie może blokować przetwarzania pozostałych wpisów.
- Logi przebiegu mają wystarczać do podstawowej diagnostyki błędów i zmian.
- Brak możliwości wykrycia ceny ma być raportowany wyłącznie w logach i nie powinien generować osobnego powiadomienia e-mail.
- Sekrety i dane dostępowe nie mogą być przechowywane w repozytorium.
- Aplikacja ma być uruchamiana jako pojedynczy przebieg przez zewnętrzny harmonogram.

## Ograniczenia
- Harmonogram uruchamiania, w tym obecny rytm `06:00` i `18:00`, nie jest częścią aplikacji. Za planowanie uruchomień odpowiada warstwa zewnętrzna, np. cron lub inny orchestrator.
- Aplikacja zakłada, że dane wejściowe w Google Sheets są przygotowane zgodnie z oczekiwanym modelem kolumn.
- Skuteczność działania zależy od dostępności Google Sheets, poprawności danych w arkuszach, dostępu do strony PlayStation Store oraz poprawnej konfiguracji SMTP.

## Ryzyka
- Zmiana struktury HTML strony `store.playstation.com` może uniemożliwić poprawne odczytywanie ceny.
- Niepełne lub błędne dane w Google Sheets mogą prowadzić do pomijania produktów albo niepoprawnych aktualizacji.
- Problemy z autoryzacją konta serwisowego Google mogą zablokować dostęp do konfiguracji lub zapis zmian.
- Problemy z SMTP mogą uniemożliwić dostarczenie powiadomień mimo poprawnego wykrycia obniżek.

## Kryteria sukcesu
- Dokument opisuje aplikację Python jako następcę workflow `n8n`.
- Dokument jednoznacznie rozróżnia arkusz konfiguracyjny i arkusze robocze.
- Dokument zawiera regułę biznesową, że tylko cena niższa od `cena` powoduje aktualizację `przecena` i powiadomienie.
- Dokument wskazuje, że harmonogram uruchomień należy do warstwy zewnętrznej, a nie do samej aplikacji.
- Dokument ogranicza się do opisu PRD i nie definiuje zmian w `spec.md`, `ROADMAP.md`, `STATUS.md` ani w kodzie.
