"""Integracja z Google Sheets dla konfiguracji i arkuszy roboczych."""

import gspread
from gspread.exceptions import APIError, SpreadsheetNotFound, WorksheetNotFound


def authenticate_gspread(service_account_file: str) -> gspread.Client:
    """Autoryzuje klienta Google Sheets przez konto serwisowe."""
    return gspread.service_account(filename=service_account_file)


def open_sheet(gc: gspread.Client, spreadsheet_id: str, worksheet_title: str):
    """Otwiera arkusz i wskazana zakladke po ID dokumentu."""
    try:
        spreadsheet = gc.open_by_key(spreadsheet_id)
    except SpreadsheetNotFound as exc:
        raise RuntimeError("Nie znaleziono arkusza Google Sheets.") from exc
    except APIError as exc:
        raise RuntimeError("Brak dostepu do arkusza Google Sheets.") from exc

    try:
        worksheet = spreadsheet.worksheet(worksheet_title)
    except WorksheetNotFound as exc:
        raise RuntimeError(f"Nie znaleziono zakladki: {worksheet_title}") from exc

    return spreadsheet, worksheet


def _normalize_header(values):
    return [str(value or "").strip().lower() for value in values]


def _row_to_dict(header, row):
    row_dict = {}
    for index, key in enumerate(header):
        row_dict[key] = str(row[index]).strip() if index < len(row) else ""
    return row_dict


def read_config_rows(worksheet) -> list[dict]:
    """Czyta wpisy konfiguracji z centralnego arkusza."""
    values = worksheet.get_all_values()
    if not values:
        raise RuntimeError("Arkusz konfiguracyjny jest pusty.")

    header = _normalize_header(values[0])
    required_columns = ["dokument", "arkusz", "email"]
    for column in required_columns:
        if column not in header:
            raise RuntimeError(
                f"Brak wymaganej kolumny w arkuszu konfiguracyjnym: {column}"
            )

    config_rows = []
    for row in values[1:]:
        if not any(str(value).strip() for value in row):
            continue
        row_dict = _row_to_dict(header, row)
        if not row_dict["dokument"] or not row_dict["arkusz"] or not row_dict["email"]:
            continue
        config_rows.append(row_dict)
    return config_rows


def read_price_rows(worksheet) -> list[dict]:
    """Czyta pozycje do monitorowania z arkusza roboczego."""
    values = worksheet.get_all_values()
    if not values:
        raise RuntimeError("Arkusz roboczy jest pusty.")

    header = _normalize_header(values[0])
    required_columns = ["nazwa", "link", "cena", "przecena"]
    for column in required_columns:
        if column not in header:
            raise RuntimeError(f"Brak wymaganej kolumny w arkuszu roboczym: {column}")

    price_rows = []
    for row_index, row in enumerate(values[1:], start=2):
        if not any(str(value).strip() for value in row):
            continue
        row_dict = _row_to_dict(header, row)
        if not row_dict["link"]:
            continue
        row_dict["row_number"] = row_index
        price_rows.append(row_dict)
    return price_rows


def update_discount_price(worksheet, row_number: int, price: float) -> None:
    """Aktualizuje kolumne `przecena` dla wskazanego wiersza."""
    values = worksheet.get_all_values()
    if not values:
        raise RuntimeError("Arkusz roboczy jest pusty.")

    header = _normalize_header(values[0])
    try:
        discount_column = header.index("przecena") + 1
    except ValueError as exc:
        raise RuntimeError("Brak wymaganej kolumny w arkuszu roboczym: przecena") from exc

    worksheet.update_cell(row_number, discount_column, f"{price:.2f}")
