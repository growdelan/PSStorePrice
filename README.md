# PSStorePrice

Minimalna aplikacja do monitorowania cen w PS Store rozwijana milestone'ami.

## Wymagania

- `uv`
- konto Google z arkuszem konfiguracyjnym oraz arkuszami roboczymi
- konto serwisowe Google z dostepem do wymaganych arkuszy

## Konfiguracja

1. Skopiuj `.env.example` do `.env`.
2. Ustaw wymagane zmienne:
   - `GOOGLE_CONFIG_SHEET_ID`
   - `GOOGLE_CONFIG_WORKSHEET`
   - `GSPREAD_SERVICE_ACCOUNT_FILE`
   - `SMTP_SERVER`
   - `SENDER_MAIL`
   - `SENDER_PASS`

## Uruchomienie

Synchronizacja srodowiska:

```bash
uv sync
```

Uruchomienie aplikacji:

```bash
uv run main.py
```

Aktualny stan po Milestone 1.2 odczytuje centralny arkusz konfiguracyjny i wskazane arkusze robocze, pobiera strony produktow z PlayStation Store, wybiera monitorowany wariant na podstawie `cena` i `Nazwa`, aktualizuje `przecena` tylko dla realnych obnizek i wysyla zbiorczy e-mail dla zmian z danego wpisu konfiguracyjnego.

## Testy

Projekt uzywa `unittest`. Standardowa komenda:

```bash
uv run python -m unittest discover -s tests -p "test_*.py"
```
