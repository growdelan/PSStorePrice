import io
import os
import unittest
from contextlib import redirect_stdout

import main


class FakeWorksheet:
    def __init__(self, values):
        self._values = values

    def get_all_values(self):
        return self._values


class FakeSpreadsheet:
    def __init__(self, worksheets):
        self._worksheets = worksheets

    def worksheet(self, title):
        if title not in self._worksheets:
            raise main.google_sheets.WorksheetNotFound(title)
        return self._worksheets[title]


class FakeClient:
    def __init__(self, spreadsheets):
        self._spreadsheets = spreadsheets

    def open_by_key(self, key):
        if key not in self._spreadsheets:
            raise main.google_sheets.SpreadsheetNotFound(key)
        return self._spreadsheets[key]


class MilestoneOneZeroTestCase(unittest.TestCase):
    def setUp(self):
        self.original_env = {
            "GOOGLE_CONFIG_SHEET_ID": os.environ.get("GOOGLE_CONFIG_SHEET_ID"),
            "GOOGLE_CONFIG_WORKSHEET": os.environ.get("GOOGLE_CONFIG_WORKSHEET"),
            "GSPREAD_SERVICE_ACCOUNT_FILE": os.environ.get(
                "GSPREAD_SERVICE_ACCOUNT_FILE"
            ),
        }
        self.original_authenticate = main.google_sheets.authenticate_gspread
        self.original_fetch_html = main.playstation_store.fetch_product_html

    def tearDown(self):
        for key, value in self.original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        main.google_sheets.authenticate_gspread = self.original_authenticate
        main.playstation_store.fetch_product_html = self.original_fetch_html

    def _configure_fake_client(self):
        config_values = [
            ["dokument", "arkusz", "email"],
            ["sheet-1", "ListaA", "user1@example.com"],
            ["sheet-2", "ListaB", "user2@example.com"],
        ]
        sheet_one_values = [
            ["Nazwa", "Link", "cena", "przecena"],
            ["Gra 1", "https://store.playstation.com/gra-1", "299", ""],
            ["Gra 2", "https://store.playstation.com/gra-2", "199", ""],
        ]
        sheet_two_values = [
            ["Nazwa", "Link", "cena", "przecena"],
            ["Gra 3", "https://store.playstation.com/gra-3", "99", ""],
        ]

        fake_client = FakeClient(
            {
                "config-sheet": FakeSpreadsheet(
                    {"Users": FakeWorksheet(config_values)}
                ),
                "sheet-1": FakeSpreadsheet({"ListaA": FakeWorksheet(sheet_one_values)}),
                "sheet-2": FakeSpreadsheet({"ListaB": FakeWorksheet(sheet_two_values)}),
            }
        )
        main.google_sheets.authenticate_gspread = lambda _: fake_client
        main.playstation_store.fetch_product_html = lambda url: (
            "<html><body><div>Stub Game</div><div>PS5</div><div>999,00 zl</div></body></html>"
        )

    def test_run_price_check_reads_config_and_price_rows(self):
        os.environ["GOOGLE_CONFIG_SHEET_ID"] = "config-sheet"
        os.environ["GOOGLE_CONFIG_WORKSHEET"] = "Users"
        os.environ["GSPREAD_SERVICE_ACCOUNT_FILE"] = "service_account.json"
        self._configure_fake_client()

        run_result = main.run_price_check()

        self.assertEqual(2, run_result["configuration_count"])
        self.assertEqual(2, len(run_result["processed_sheets"]))
        self.assertEqual(2, run_result["processed_sheets"][0]["item_count"])
        self.assertEqual(1, run_result["processed_sheets"][1]["item_count"])

    def test_main_prints_summary_after_loading_sheets(self):
        os.environ["GOOGLE_CONFIG_SHEET_ID"] = "config-sheet"
        os.environ["GOOGLE_CONFIG_WORKSHEET"] = "Users"
        os.environ["GSPREAD_SERVICE_ACCOUNT_FILE"] = "service_account.json"
        self._configure_fake_client()

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            main.main()

        output = stdout.getvalue().strip()
        self.assertIn("Wczytano 2 konfiguracje", output)
        self.assertIn("3 pozycje", output)


if __name__ == "__main__":
    unittest.main()
