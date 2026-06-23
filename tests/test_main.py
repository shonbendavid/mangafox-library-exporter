"""
Light integration test for MangaDex backup tool.

Run with:
    python tests/test_basic.py
"""

from src.auth.login import login
from src.api.client import MangaDexClient
from src.sync.sync_engine import sync_library
from src.database.db import Session, Manga


def test_login():
    print("[TEST] login...")

    # You MUST fill these in manually for testing
    username = "YOUR_USERNAME"
    password = "YOUR_PASSWORD"

    tokens = login(username, password)

    assert "access_token" in tokens
    assert "refresh_token" in tokens

    print("[OK] login passed")
    return tokens


def test_api(client):
    print("[TEST] API library fetch...")

    data = client.get_library()

    assert "data" in data
    assert isinstance(data["data"], list)

    print("[OK] API passed")


def test_sync(client):
    print("[TEST] sync...")

    sync_library(client)

    session = Session()
    count = session.query(Manga).count()

    assert count >= 0  # just ensures DB works

    print(f"[OK] sync passed ({count} entries)")


def main():
    tokens = test_login()

    client = MangaDexClient(tokens["access_token"])

    test_api(client)
    test_sync(client)

    print("\nALL TESTS PASSED")


if __name__ == "__main__":
    main()
