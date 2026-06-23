import pytest
from mangadex_scrapper.scraper import fetch_titles

def test_fetch_titles():
    """Synchronous test for fetch_titles stub."""
    results = fetch_titles("naruto", limit=3)
    assert isinstance(results, list)
    assert len(results) == 3
    assert results[0].startswith("naruto")
