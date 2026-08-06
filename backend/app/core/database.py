from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session

DB_PATH = Path(__file__).resolve().parents[3] / "data" / "aether.db"
DB_PATH.parent.mkdir(exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}")

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session