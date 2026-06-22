from sqlalchemy import *
from sqlalchemy.orm import *

from src.core.config import DB_PATH

engine = create_engine(DB_PATH)
Base = declarative_base()


class Manga(Base):
    __tablename__ = "manga"

    id = Column(String, primary_key=True)
    title = Column(String)
    status = Column(String)
    last_updated = Column(String)


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)