<<<<<<< HEAD
from PySide6.QtWidgets import *

from src.sync.sync_engine import sync_library


class MainWindow(QMainWindow):
    def __init__(self, client):
        super().__init__()

        self.client = client

        self.setWindowTitle("MangaDex Backup")

        btn = QPushButton("Sync Library")
        btn.clicked.connect(self.sync)

        layout = QVBoxLayout()
        layout.addWidget(btn)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def sync(self):
        sync_library(self.client)

        QMessageBox.information(
            self,
            "Done",
            "Sync completed"
=======
from PySide6.QtWidgets import *

from src.sync.sync_engine import sync_library


class MainWindow(QMainWindow):
    def __init__(self, client):
        super().__init__()

        self.client = client

        self.setWindowTitle("MangaDex Backup")

        btn = QPushButton("Sync Library")
        btn.clicked.connect(self.sync)

        layout = QVBoxLayout()
        layout.addWidget(btn)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def sync(self):
        sync_library(self.client)

        QMessageBox.information(
            self,
            "Done",
            "Sync completed"
>>>>>>> c4667f23e9f76579d0d87263e04724529d314eac
        )