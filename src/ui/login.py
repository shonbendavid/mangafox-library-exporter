from PySide6.QtWidgets import *

from src.auth.login import login
from src.auth.token_store import save_refresh_token


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MangaDex Backup Login")

        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)

        btn = QPushButton("Login")
        btn.clicked.connect(self.handle_login)

        layout = QVBoxLayout()
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(btn)

        self.setLayout(layout)

    def handle_login(self):
        data = login(
            self.username.text(),
            self.password.text()
        )

        save_refresh_token(data["refresh_token"])

        QMessageBox.information(
            self,
            "Success",
            "Login successful"
        )