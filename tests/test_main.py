import pytest
from mangadex_scrapper.scraper import fetch_titles

@pytest.mark.asyncio
async def test_fetch_titles():
    results = fetch_titles("naruto", limit=3)
    assert isinstance(results, list)
    assert len(results) == 3
    assert results[0].startswith("naruto")
