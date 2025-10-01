from . import models
import os
from sqlmodel import SQLModel, create_engine, Session

# Byt enkelt till Postgres genom att sätta env:
# DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/dbname
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# SQLite behöver check_same_thread=False
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def get_session():
    with Session(engine) as session:
        yield session


def init_db():
    # Viktigt: importera modellerna innan create_all
    from . import models  # noqa: F401
    SQLModel.metadata.create_all(bind=engine)
