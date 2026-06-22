from src.database.db import Session, Manga
from src.api.client import MangaDexClient


def sync_library(client: MangaDexClient):
    session = Session()

    library = client.get_library()
    manga_list = library.get("data", [])

    for item in manga_list:
        manga_id = item["id"]

        try:
            details = client.get_manga(manga_id)
            title = details["data"]["attributes"]["title"].get("en", "Unknown")
        except Exception:
            title = "Unknown"

        existing = session.get(Manga, manga_id)

        if existing:
            existing.title = title
        else:
            session.add(Manga(
                id=manga_id,
                title=title,
                status="followed",
                last_updated=""
            ))

    session.commit()