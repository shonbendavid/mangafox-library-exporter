<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

This repository contains the `mangadex-scrapper` Python package. Please prefer small, testable functions, asynchronous HTTP I/O with `httpx.AsyncClient`, and clear CLI interfaces using `click`.

Guidelines:
- Keep functions pure where possible and document side effects.
- Favor typing and docstrings.
- Write pytest-style unit and async tests under `tests/` using `pytest-asyncio`.
- Avoid web scraping that violates site terms of service; include rate limiting and caching.
