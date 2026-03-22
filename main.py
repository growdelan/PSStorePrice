"""Entrypoint aplikacji dla odczytu konfiguracji i arkuszy roboczych."""

import os

from dotenv import load_dotenv

from storage import google_sheets


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


def run_price_check():
    """Wykonuje przebieg odczytu konfiguracji i arkuszy roboczych."""
    config = load_config()
    gc = google_sheets.authenticate_gspread(config["GSPREAD_SERVICE_ACCOUNT_FILE"])
    configuration_entries = fetch_configuration_entries(gc, config)

    run_result = {
        "configuration_count": len(configuration_entries),
        "processed_sheets": [],
    }
    for entry in configuration_entries:
        price_rows = fetch_price_rows(gc, entry)
        run_result["processed_sheets"].append(
            {
                "email": entry["email"],
                "spreadsheet_id": entry["dokument"],
                "worksheet": entry["arkusz"],
                "item_count": len(price_rows),
            }
        )
    return run_result


def build_summary(run_result):
    """Buduje komunikat tekstowy z wyniku przebiegu."""
    total_items = sum(sheet["item_count"] for sheet in run_result["processed_sheets"])
    return (
        "Wczytano "
        f"{run_result['configuration_count']} konfiguracje i "
        f"{total_items} pozycje do dalszego przetwarzania."
    )


def main():
    """Uruchamia przebieg aplikacji."""
    run_result = run_price_check()
    print(build_summary(run_result))


if __name__ == "__main__":
    main()
