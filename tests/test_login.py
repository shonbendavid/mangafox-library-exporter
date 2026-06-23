import asyncio
import os
import sys
import types
from unittest.mock import patch

import pytest
from mangadex_scrapper.scraper import login_mangafox


def _install_fake_httpx(dummy_client_cls):
    """Install a fake httpx module into sys.modules with AsyncClient pointing to dummy_client_cls."""
    fake_httpx = types.ModuleType("httpx")
    fake_httpx.AsyncClient = dummy_client_cls
    sys.modules["httpx"] = fake_httpx


def _remove_fake_httpx():
    sys.modules.pop("httpx", None)


def test_login_success_mocked():
    class DummyClient:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            return False
        async def post(self, url, data):
            class DummyResp:
                status_code = 200
                def json(self):
                    return {"success": True}
            return DummyResp()

    _install_fake_httpx(DummyClient)
    try:
        ok = asyncio.run(login_mangafox("user", "pass", login_url="https://mangafox.example/login"))
        assert ok is True
    finally:
        _remove_fake_httpx()


def test_login_failure_mocked():
    class DummyClient:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            return False
        async def post(self, url, data):
            class DummyResp:
                status_code = 401
                def json(self):
                    return {"success": False}
            return DummyResp()

    _install_fake_httpx(DummyClient)
    try:
        ok = asyncio.run(login_mangafox("user", "badpass", login_url="https://mangafox.example/login"))
        assert ok is False
    finally:
        _remove_fake_httpx()


def test_login_integration_optional():
    """Optional integration test that runs only when MANGAFOX_RUN_INTEGRATION=1 is set.

    Manually insert credentials into environment variables before running tests:
      setx MANGAFOX_USER "username"
      setx MANGAFOX_PASS "password"
    Then run (PowerShell):
      $env:MANGAFOX_RUN_INTEGRATION=1; $env:PYTHONPATH='src'; python -m pytest tests/test_login.py::test_login_integration_optional -q
    """
    run_integration = os.environ.get("MANGAFOX_RUN_INTEGRATION") == "1"
    if not run_integration:
        pytest.skip("Integration test disabled; set MANGAFOX_RUN_INTEGRATION=1 to enable")

    user = os.environ.get("MANGAFOX_USER")
    pwd = os.environ.get("MANGAFOX_PASS")
    if not user or not pwd:
        pytest.skip("MANGAFOX_USER or MANGAFOX_PASS not set")

    # integration requires real httpx; ensure it's importable
    try:
        import httpx as _
    except Exception:
        pytest.skip("httpx not installed; skip integration test")

    ok = asyncio.run(login_mangafox(user, pwd, login_url=None))
    assert ok is True
