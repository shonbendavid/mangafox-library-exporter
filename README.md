# MangaDex Backup Tool

A lightweight Windows desktop application built with Python that logs into MangaDex, syncs your library, and stores it locally for backup and export.

---

## ✨ Features

- 🔐 Login with MangaDex username & password
- 📚 Sync followed manga library
- 🗄 Store data locally in SQLite
- 📤 Export library to JSON
- 📊 Export library to CSV
- 🔄 Update existing manga entries automatically
- ⚡ Simple desktop UI (PySide6)
- 🔁 Retry-safe API requests

---

## 🧱 Project Structure

```text
mangadex_backup/
│
├── app.py
├── requirements.txt
│
├── src/
│   ├── auth/
│   ├── api/
│   ├── database/
│   ├── sync/
│   ├── backup/
│   ├── ui/
│   └── core/
│
├── data/
├── backups/
└── tests/
