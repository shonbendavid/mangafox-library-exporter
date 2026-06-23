import unittest
from src.scraper import Scraper

class TestScraper(unittest.TestCase):

    def setUp(self):
        self.scraper = Scraper()

    def test_scrape_library(self):
        # Test that the scrape_library method returns expected results
        result = self.scraper.scrape_library()
        self.assertIsInstance(result, list)  # Assuming it returns a list of manga
        self.assertGreater(len(result), 0)   # Ensure that the list is not empty

    def test_parse_content(self):
        # Test that the parse_content method correctly extracts data
        html_content = "<html><body><div class='manga'>Test Manga</div></body></html>"
        result = self.scraper.parse_content(html_content)
        self.assertIn("Test Manga", result)  # Assuming it extracts manga titles

if __name__ == '__main__':
    unittest.main()