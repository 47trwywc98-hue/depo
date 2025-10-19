import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SiteIntegrityTests(unittest.TestCase):
    def test_data_file_structure(self):
        data_path = ROOT / "data" / "doganismakinalari-data.json"
        self.assertTrue(data_path.exists(), "Data file is missing")

        data = json.loads(data_path.read_text(encoding="utf-8"))
        self.assertIsInstance(data, dict, "Data file must contain a JSON object")
        self.assertIn("machines", data)
        self.assertIn("contact", data)
        self.assertIsInstance(data["machines"], list, "`machines` should be a list")
        self.assertIsInstance(data["contact"], dict, "`contact` should be an object")

        expected_contact_keys = {"phone", "email", "address", "servicePhone"}
        self.assertTrue(
            expected_contact_keys.issubset(data["contact"].keys()),
            "Contact object must include phone, email, address and servicePhone keys",
        )

    def test_index_contains_required_hooks(self):
        html_path = ROOT / "index.html"
        html = html_path.read_text(encoding="utf-8")

        required_snippets = [
            'id="stock-list"',
            'id="stock-empty-message"',
            'id="header-phone"',
            'id="service-phone"',
            'id="contact-phone"',
            'id="contact-email"',
            'id="contact-address"',
        ]

        for snippet in required_snippets:
            with self.subTest(snippet=snippet):
                self.assertIn(snippet, html)

        self.assertIn(
            '<script type="module" src="site-data.js"></script>',
            html,
            "index.html should include site-data.js script tag",
        )

    def test_site_data_fetch_path(self):
        script_path = ROOT / "site-data.js"
        script = script_path.read_text(encoding="utf-8")

        self.assertIn(
            "data/doganismakinalari-data.json",
            script,
            "site-data.js should fetch the data JSON from the data directory",
        )


if __name__ == "__main__":
    unittest.main()
