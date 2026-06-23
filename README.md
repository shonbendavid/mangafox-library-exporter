# mangadex-scrapper

Async scraping utilities and a CLI for extracting data from MangaDex-like sites.

Prerequisites (Windows):
1. python -m venv .venv
2. .\.venv\Scripts\Activate.ps1
3. pip install -r requirements.txt

Run the CLI:
- python -m mangadex_scrapper.cli --help

Run tests:
- python -m pytest -q

Windows build (bundle GUI into single EXE)

1) Create and activate venv, install requirements:
   python -m venv .venv; .\.venv\Scripts\Activate.ps1; python -m pip install -U pip; pip install -r requirements.txt

2) Build the EXE (windowed):
   powershell -ExecutionPolicy Bypass -File ./build_windows.ps1 -entry "-m mangadex_scrapper.gui" -name "mangadex-scrapper" -windowed

3) Result: `dist\mangadex-scrapper.exe`

Note: PyInstaller may require additional hooks for PySide6. If the resulting executable fails, run PyInstaller manually and inspect the build log.

Note: Replace placeholders (author, email) in pyproject.toml.

Option A — Single EXE (PyInstaller onefile)

This builds a single executable with PyInstaller (recommended for non-developer users).

1) Create & activate venv and install dependencies:
   python -m venv .venv; .\.venv\Scripts\Activate.ps1; python -m pip install -U pip; pip install -r requirements.txt

2) Build onefile windowed EXE:
   powershell -ExecutionPolicy Bypass -File ./build_windows.ps1 -entry "src\\mangadex_scrapper\\gui.py" -name "mangadex-scrapper" -windowed

3) Find the result in dist\mangadex-scrapper.exe

Troubleshooting:
- If PyInstaller misses PySide6 plugins, try building with --onedir first and copying the folder, or add the official PySide6 hook for PyInstaller.
- If you see import errors during the build, ensure all dependencies installed in the venv.
- For an icon, pass -icon "path\\to\\app.ico" to the build script.
