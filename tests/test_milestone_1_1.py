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

    def test_process_price_rows_updates_only_discounted_entries(self):
        worksheet = FakeWorksheet(
            [
                ["Nazwa", "Link", "cena", "przecena"],
                ["Game One", "https://example.com/game-one", "299,00 zl", ""],
                ["Game Two", "https://example.com/game-two", "149,00 zl", ""],
            ]
        )
        price_rows = [
            {
                "nazwa": "Game One",
                "link": "https://example.com/game-one",
                "cena": "299,00 zl",
                "przecena": "",
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
        self.assertEqual([(2, 4, "249.00")], worksheet.updated_cells)


if __name__ == "__main__":
    unittest.main()
