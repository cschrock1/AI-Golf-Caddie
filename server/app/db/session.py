from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL

_engine = None
_SessionLocal = None

def init_engine(database_url: str = None):
    global _engine, _SessionLocal
    database_url = database_url or DATABASE_URL
    if not database_url:
        return None
    _engine = create_engine(database_url, future=True)
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    return _engine

def get_session():
    if _SessionLocal is None:
        init_engine()
    return _SessionLocal()
