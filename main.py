"""Entrypoint aplikacji dla odczytu konfiguracji i arkuszy roboczych."""

import logging
import os

from dotenv import load_dotenv

from scrapers import playstation_store
from storage import google_sheets

LOGGER = logging.getLogger(__name__)


def load_config():
    """Laduje konfiguracje srodowiskowa wymagana do polaczenia z Google Sheets."""
    load_dotenv()
    required_variables = [
        "GOOGLE_CONFIG_SHEET_ID",
        "GOOGLE_CONFIG_WORKSHEET",
        "GSPREAD_SERVICE_ACCOUNT_FILE",
    ]

    config = {}
    missing_variables = []
    for variable in required_variables:
        value = os.getenv(variable)
        if not value:
            missing_variables.append(variable)
            continue
        config[variable] = value

    if missing_variables:
        raise RuntimeError(
            "Brak wymaganych zmiennych srodowiskowych: "
            + ", ".join(missing_variables)
        )

    return config


def fetch_configuration_entries(gc, config):
    """Czyta centralny arkusz konfiguracji i zwraca wpisy do przetworzenia."""
    _, worksheet = google_sheets.open_sheet(
        gc=gc,
        spreadsheet_id=config["GOOGLE_CONFIG_SHEET_ID"],
        worksheet_title=config["GOOGLE_CONFIG_WORKSHEET"],
    )
    return google_sheets.read_config_rows(worksheet)


def fetch_price_rows(gc, configuration_entry):
    """Czyta pozycje z jednego arkusza roboczego."""
    _, worksheet = google_sheets.open_sheet(
        gc=gc,
        spreadsheet_id=configuration_entry["dokument"],
        worksheet_title=configuration_entry["arkusz"],
    )
    return google_sheets.read_price_rows(worksheet)


def process_price_rows(worksheet, price_rows, fetch_html=None):
    """Pobiera ceny dla pozycji i aktualizuje przeceny dla realnych obnizek."""
    if fetch_html is None:
        fetch_html = playstation_store.fetch_product_html
    checked_items = 0
    updated_items = 0
    for price_row in price_rows:
        checked_items += 1
        try:
            page_html = fetch_html(price_row["link"])
            current_price = playstation_store.extract_current_price(
                page_html=page_html,
                expected_name=price_row["nazwa"],
                reference_price=price_row["cena"],
            )
            base_price = playstation_store.parse_price_value(price_row["cena"])
            if current_price < base_price:
                google_sheets.update_discount_price(
                    worksheet=worksheet,
                    row_number=price_row["row_number"],
                    price=current_price,
                )
                updated_items += 1
        except Exception as exc:
            LOGGER.warning(
                "Nie udalo sie przetworzyc pozycji %s (%s): %s",
                price_row["nazwa"],
                price_row["link"],
                exc,
            )

    return {
        "checked_items": checked_items,
        "updated_items": updated_items,
    }


def run_price_check():
    """Wykonuje przebieg odczytu konfiguracji, sprawdzania cen i aktualizacji przecen."""
    config = load_config()
    gc = google_sheets.authenticate_gspread(config["GSPREAD_SERVICE_ACCOUNT_FILE"])
    configuration_entries = fetch_configuration_entries(gc, config)

    run_result = {
        "configuration_count": len(configuration_entries),
        "processed_sheets": [],
    }
    for entry in configuration_entries:
        _, worksheet = google_sheets.open_sheet(
            gc=gc,
            spreadsheet_id=entry["dokument"],
            worksheet_title=entry["arkusz"],
        )
        price_rows = google_sheets.read_price_rows(worksheet)
        sheet_result = process_price_rows(worksheet, price_rows)
        run_result["processed_sheets"].append(
            {
                "email": entry["email"],
                "spreadsheet_id": entry["dokument"],
                "worksheet": entry["arkusz"],
                "item_count": sheet_result["checked_items"],
                "updated_items": sheet_result["updated_items"],
            }
        )
    return run_result


def build_summary(run_result):
    """Buduje komunikat tekstowy z wyniku przebiegu."""
    total_items = sum(sheet["item_count"] for sheet in run_result["processed_sheets"])
    updated_items = sum(sheet["updated_items"] for sheet in run_result["processed_sheets"])
    return (
        "Wczytano "
        f"{run_result['configuration_count']} konfiguracje i "
        f"{total_items} pozycje, zaktualizowano {updated_items} przeceny."
    )


def main():
    """Uruchamia przebieg aplikacji."""
    run_result = run_price_check()
    print(build_summary(run_result))


if __name__ == "__main__":
    main()
