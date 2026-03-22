import io
import unittest
from contextlib import redirect_stdout

import main


class SmokeTestCase(unittest.TestCase):
    def test_run_price_check_detects_discount_for_stub_item(self):
        run_result = main.run_price_check()

        self.assertEqual("demo-user", run_result["user"])
        self.assertEqual(1, len(run_result["results"]))
        self.assertTrue(run_result["results"][0]["has_discount"])

    def test_main_prints_summary_for_discounted_item(self):
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            main.main()

        output = stdout.getvalue().strip()
        self.assertIn("Wykryto obnizke dla demo-user", output)
        self.assertIn("Demo Game", output)


if __name__ == "__main__":
    unittest.main()
