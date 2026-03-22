# PSStorePrice

Minimalny bootstrap aplikacji do monitorowania cen w PS Store.

## Uruchomienie

Synchronizacja srodowiska:

```bash
uv sync
```

Uruchomienie aplikacji:

```bash
uv run main.py
```

Aktualny Milestone 0.5 uruchamia minimalny przebieg end-to-end na stubowanych danych i wypisuje wynik do standardowego wyjscia.

## Testy

Projekt uzywa `unittest`. Standardowa komenda:

```bash
uv run python -m unittest discover -s tests -p "test_*.py"
```
