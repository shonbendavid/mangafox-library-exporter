<<<<<<< HEAD
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

=======
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

>>>>>>> c4667f23e9f76579d0d87263e04724529d314eac
Session = sessionmaker(bind=engine)