import email
import io
import os
import unittest
from contextlib import redirect_stdout

import main
from emails import notifications


class FakeWorksheet:
    def __init__(self, values):
        self._values = values
        self.updated_cells = []

    def get_all_values(self):
        return self._values

    def update_cell(self, row, column, value):
        self.updated_cells.append((row, column, value))


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


class FakeSMTP:
    last_instance = None

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.started_tls = False
        self.logged_in_as = None
        self.sent_messages = []
        FakeSMTP.last_instance = self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def ehlo(self):
        return None

    def starttls(self, context):
        self.started_tls = True

    def login(self, user, password):
        self.logged_in_as = (user, password)

    def sendmail(self, sender, recipients, raw_message):
        self.sent_messages.append((sender, recipients, raw_message))


class MilestoneOneTwoTestCase(unittest.TestCase):
    def setUp(self):
        self.original_env = {
            "GOOGLE_CONFIG_SHEET_ID": os.environ.get("GOOGLE_CONFIG_SHEET_ID"),
            "GOOGLE_CONFIG_WORKSHEET": os.environ.get("GOOGLE_CONFIG_WORKSHEET"),
            "GSPREAD_SERVICE_ACCOUNT_FILE": os.environ.get(
                "GSPREAD_SERVICE_ACCOUNT_FILE"
            ),
            "SMTP_SERVER": os.environ.get("SMTP_SERVER"),
            "SENDER_MAIL": os.environ.get("SENDER_MAIL"),
            "SENDER_PASS": os.environ.get("SENDER_PASS"),
        }
        self.original_authenticate = main.google_sheets.authenticate_gspread
        self.original_fetch_html = main.playstation_store.fetch_product_html
        self.original_smtp = notifications.smtplib.SMTP

    def tearDown(self):
        for key, value in self.original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        main.google_sheets.authenticate_gspread = self.original_authenticate
        main.playstation_store.fetch_product_html = self.original_fetch_html
        notifications.smtplib.SMTP = self.original_smtp

    def _configure_env(self):
        os.environ["GOOGLE_CONFIG_SHEET_ID"] = "config-sheet"
        os.environ["GOOGLE_CONFIG_WORKSHEET"] = "Users"
        os.environ["GSPREAD_SERVICE_ACCOUNT_FILE"] = "service_account.json"
        os.environ["SMTP_SERVER"] = "smtp.example.com"
        os.environ["SENDER_MAIL"] = "sender@example.com"
        os.environ["SENDER_PASS"] = "secret"

    def _configure_fake_client(self):
        config_values = [
            ["dokument", "arkusz", "email"],
            ["bad-sheet", "ListaBad", "bad@example.com"],
            ["good-sheet", "ListaGood", "good@example.com"],
        ]
        good_sheet_values = [
            ["Nazwa", "Link", "cena", "przecena"],
            ["Game One", "https://example.com/game-one", "299,00 zl", ""],
        ]

        fake_client = FakeClient(
            {
                "config-sheet": FakeSpreadsheet(
                    {"Users": FakeWorksheet(config_values)}
                ),
                "good-sheet": FakeSpreadsheet(
                    {"ListaGood": FakeWorksheet(good_sheet_values)}
                ),
            }
        )
        main.google_sheets.authenticate_gspread = lambda _: fake_client
        main.playstation_store.fetch_product_html = (
            lambda url: "<html><body><div>Game One</div><div>PS5</div><div>249,00 zl</div></body></html>"
        )
        notifications.smtplib.SMTP = FakeSMTP

    def test_build_email_html_renders_change_rows(self):
        html_body = notifications.build_email_html(
            [
                {
                    "Nazwa": "Game One",
                    "Link": "https://example.com/game-one",
                    "cena": 299.0,
                    "przecena": 249.0,
                }
            ]
        )

        self.assertIn("Zmiany cen (1)", html_body)
        self.assertIn("Game One", html_body)
        self.assertIn("249.00 zl", html_body)

    def test_run_price_check_sends_email_and_skips_failed_config(self):
        self._configure_env()
        self._configure_fake_client()

        run_result = main.run_price_check()

        self.assertEqual(2, run_result["configuration_count"])
        self.assertEqual(1, run_result["sent_emails"])
        smtp_instance = FakeSMTP.last_instance
        self.assertIsNotNone(smtp_instance)
        self.assertEqual(("sender@example.com", "secret"), smtp_instance.logged_in_as)
        self.assertEqual(1, len(smtp_instance.sent_messages))
        parsed_message = email.message_from_string(smtp_instance.sent_messages[0][2])
        self.assertEqual("Promocje w PS Store!", parsed_message["Subject"])
        self.assertEqual("good@example.com", parsed_message["To"])


if __name__ == "__main__":
    unittest.main()
