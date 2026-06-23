"""Simple PySide6 GUI for mangadex-scrapper.

This is a lightweight front-end to the existing utilities:
- Search (uses the synchronous `fetch_titles` stub)
- Start an OIDC authorization flow with PKCE (opens a browser and awaits redirect)

Run with:
  python -m mangadex_scrapper.gui

Note: This requires PySide6 to be installed in your environment.
"""
from __future__ import annotations

import sys
import asyncio
import json
from typing import Optional

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QListWidget,
    QLabel,
    QSpinBox,
    QTextEdit,
)
from PySide6.QtCore import Qt

from mangadex_scrapper.scraper import fetch_titles, oidc_authorize_with_pkce


class MainWindow(QWidget):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("mangadex-scrapper GUI")
        self.resize(800, 600)

        layout = QVBoxLayout()

        # Search row
        row = QHBoxLayout()
        row.addWidget(QLabel("Query:"))
        self.query_edit = QLineEdit()
        row.addWidget(self.query_edit)
        row.addWidget(QLabel("Limit:"))
        self.limit_spin = QSpinBox()
        self.limit_spin.setRange(1, 100)
        self.limit_spin.setValue(5)
        row.addWidget(self.limit_spin)
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.on_search)
        row.addWidget(self.search_btn)
        layout.addLayout(row)

        # Results list
        self.results_list = QListWidget()
        layout.addWidget(self.results_list)

        # OIDC block
        oidc_label = QLabel("OIDC / MangaDex Auth (PKCE)")
        oidc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(oidc_label)

        oidc_row = QHBoxLayout()
        oidc_row.addWidget(QLabel("Client ID:"))
        self.client_id_edit = QLineEdit()
        self.client_id_edit.setPlaceholderText("mangadex-frontend-stable")
        oidc_row.addWidget(self.client_id_edit)
        self.auth_btn = QPushButton("Start Auth (opens browser)")
        self.auth_btn.clicked.connect(self.on_auth)
        oidc_row.addWidget(self.auth_btn)
        layout.addLayout(oidc_row)

        # Token/output display
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.setLayout(layout)

    def on_search(self) -> None:
        """Handle search button click."""
        query = self.query_edit.text().strip()
        if not query:
            self.output.setPlainText("Please enter a query")
            return
        limit = int(self.limit_spin.value())
        try:
            results = fetch_titles(query, limit)
            self.results_list.clear()
            for r in results:
                self.results_list.addItem(r)
            self.output.setPlainText(f"Shown {len(results)} result(s)")
        except Exception as exc:
            self.output.setPlainText(f"Search failed: {exc}")

    def on_auth(self) -> None:
        """Start OIDC authorization flow using asyncio.run so the UI remains simple.

        This will open the browser and block the UI until the flow completes; for a
        production GUI, run the flow in a background thread or async task instead.
        """
        client_id = self.client_id_edit.text().strip() or "mangadex-frontend-stable"
        self.output.setPlainText("Starting authorization... (browser will open)")
        try:
            # Call the async OIDC helper synchronously
            token_response = asyncio.run(oidc_authorize_with_pkce(client_id))
            pretty = json.dumps(token_response, indent=2)
            self.output.setPlainText(pretty)
        except Exception as exc:
            self.output.setPlainText(f"Authorization failed: {exc}")


def main(argv: Optional[list[str]] = None) -> int:
    app = QApplication(argv or sys.argv)
    w = MainWindow()
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
