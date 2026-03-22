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

## Uruchomienie

Synchronizacja srodowiska:

```bash
uv sync
```

Uruchomienie aplikacji:

```bash
uv run main.py
```

Aktualny stan po Milestone 1.1 odczytuje centralny arkusz konfiguracyjny i wskazane arkusze robocze, pobiera strony produktow z PlayStation Store, wybiera monitorowany wariant na podstawie `cena` i `Nazwa`, a nastepnie aktualizuje `przecena` tylko dla realnych obnizek.

## Testy

Projekt uzywa `unittest`. Standardowa komenda:

```bash
uv run python -m unittest discover -s tests -p "test_*.py"
```
