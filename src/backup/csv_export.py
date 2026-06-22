import pandas as pd
from src.database.db import Manga, Session


def export_csv(path: str):
    session = Session()

    data = session.query(Manga).all()

    df = pd.DataFrame([
        {
            "id": m.id,
            "title": m.title,
            "status": m.status
        }
        for m in data
    ])

    df.to_csv(path, index=False)