from unittest import TestCase
from scraper import GoesScraper


class TestGoesScraper(TestCase):
    def test_earlier_than(self):
        g = GoesScraper()
        self.assertFalse(g.earlier_than('20170201','20170131'))
        self.assertTrue(g.earlier_than('20170201','20170201'))
        self.assertTrue(g.earlier_than('20170201','20170202'))