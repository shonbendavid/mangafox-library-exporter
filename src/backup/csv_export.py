<<<<<<< HEAD
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

=======
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

>>>>>>> c4667f23e9f76579d0d87263e04724529d314eac
    df.to_csv(path, index=False)