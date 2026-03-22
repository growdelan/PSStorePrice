import unittest

import main
from scrapers import playstation_store


class FakeWorksheet:
    def __init__(self, values):
        self._values = values
        self.updated_cells = []

    def get_all_values(self):
        return self._values

    def update_cell(self, row, column, value):
        self.updated_cells.append((row, column, value))


class MilestoneOneOneTestCase(unittest.TestCase):
    def test_extract_current_price_prefers_variant_matching_base_price(self):
        html = """
        <html>
          <body>
            <h1>Sample Game</h1>
            <div>Editions:</div>
            <div>Sample Game Deluxe</div>
            <div>PS5</div>
            <div>299,00 zl</div>
            <div>Sample Game Standard</div>
            <div>PS5</div>
            <div>199,00 zl</div>
          </body>
        </html>
        """

        price = playstation_store.extract_current_price(
            page_html=html,
            expected_name="Sample Game Standard",
            reference_price="199,00 zl",
        )

        self.assertEqual(199.0, price)

    def test_extract_current_price_supports_gbp_and_eur_prefix_prices(self):
        html = """
        <html>
          <body>
            <div>Euro Game</div>
            <div>PS5</div>
            <div>€39.99</div>
            <div>Pound Game</div>
            <div>PS5</div>
            <div>£35.99</div>
          </body>
        </html>
        """

        eur_price = playstation_store.extract_current_price(
            page_html=html,
            expected_name="Euro Game",
            reference_price="€39.99",
        )
        gbp_price = playstation_store.extract_current_price(
            page_html=html,
            expected_name="Pound Game",
            reference_price="£35.99",
        )

        self.assertEqual(39.99, eur_price)
        self.assertEqual(35.99, gbp_price)

    def test_extract_current_price_skips_trial_and_uses_first_paid_option(self):
        html = """
        <html>
          <body>
            <div>Mafia: The Old Country</div>
            <div>Game Trial</div>
            <div>Subscribe to PlayStation Plus Premium to play a 1-hour full game trial</div>
            <div>£35.99</div>
            <div>£44.99</div>
          </body>
        </html>
        """

        price = playstation_store.extract_current_price(
            page_html=html,
            expected_name="Mafia: The Old Country",
            reference_price="£44.99",
        )

        self.assertEqual(35.99, price)

    def test_extract_current_price_skips_polish_trial_label(self):
        html = """
        <html>
          <body>
            <div>Test Game</div>
            <div>Wersja próbna gry</div>
            <div>Wypróbuj grę przez ograniczony czas</div>
            <div>259,00 zl</div>
            <div>299,00 zl</div>
          </body>
        </html>
        """

        price = playstation_store.extract_current_price(
            page_html=html,
            expected_name="Test Game",
            reference_price="299,00 zl",
        )

        self.assertEqual(259.0, price)

    def test_process_price_rows_updates_only_discounted_entries(self):
        worksheet = FakeWorksheet(
            [
                ["Nazwa", "Link", "cena", "przecena"],
                ["Game One", "https://example.com/game-one", "299,00 zl", "299,00 zl"],
                ["Game Two", "https://example.com/game-two", "149,00 zl", ""],
            ]
        )
        price_rows = [
            {
                "nazwa": "Game One",
                "link": "https://example.com/game-one",
                "cena": "299,00 zl",
                "przecena": "299,00 zl",
                "row_number": 2,
            },
            {
                "nazwa": "Game Two",
                "link": "https://example.com/game-two",
                "cena": "149,00 zl",
                "przecena": "",
                "row_number": 3,
            },
        ]

        html_by_url = {
            "https://example.com/game-one": """
                <html><body><div>Game One</div><div>PS5</div><div>249,00 zl</div></body></html>
            """,
            "https://example.com/game-two": """
                <html><body><div>Game Two</div><div>PS5</div><div>149,00 zl</div></body></html>
            """,
        }

        result = main.process_price_rows(
            worksheet,
            price_rows,
            fetch_html=lambda url: html_by_url[url],
        )

        self.assertEqual(2, result["checked_items"])
        self.assertEqual(1, result["updated_items"])
        self.assertEqual([(2, 4, 249.0)], worksheet.updated_cells)

    def test_process_price_rows_resets_discount_to_base_price_when_sale_ends(self):
        worksheet = FakeWorksheet(
            [
                ["Nazwa", "Link", "cena", "przecena"],
                ["Game One", "https://example.com/game-one", "299,00 zl", "249,00 zl"],
            ]
        )
        price_rows = [
            {
                "nazwa": "Game One",
                "link": "https://example.com/game-one",
                "cena": "299,00 zl",
                "przecena": "249,00 zl",
                "row_number": 2,
            }
        ]

        result = main.process_price_rows(
            worksheet,
            price_rows,
            fetch_html=lambda url: (
                "<html><body><div>Game One</div><div>PS5</div><div>299,00 zl</div></body></html>"
            ),
        )

        self.assertEqual(1, result["checked_items"])
        self.assertEqual(1, result["updated_items"])
        self.assertEqual([], result["changes"])
        self.assertEqual([(2, 4, 299.0)], worksheet.updated_cells)

    def test_process_price_rows_does_not_repeat_same_discount(self):
        worksheet = FakeWorksheet(
            [
                ["Nazwa", "Link", "cena", "przecena"],
                ["Game One", "https://example.com/game-one", "299,00 zl", "249,00 zl"],
            ]
        )
        price_rows = [
            {
                "nazwa": "Game One",
                "link": "https://example.com/game-one",
                "cena": "299,00 zl",
                "przecena": "249,00 zl",
                "row_number": 2,
            }
        ]

        result = main.process_price_rows(
            worksheet,
            price_rows,
            fetch_html=lambda url: (
                "<html><body><div>Game One</div><div>PS5</div><div>249,00 zl</div></body></html>"
            ),
        )

        self.assertEqual(1, result["checked_items"])
        self.assertEqual(0, result["updated_items"])
        self.assertEqual([], result["changes"])
        self.assertEqual([], worksheet.updated_cells)


if __name__ == "__main__":
    unittest.main()
