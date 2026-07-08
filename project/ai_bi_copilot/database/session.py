from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings


engine = create_engine(
    settings.database_url,

    echo=settings.DEBUG,

    pool_pre_ping=True,

    future=True
)


SessionLocal = sessionmaker(
    bind=engine,

    autoflush=False,

    autocommit=False,

    expire_on_commit=False
)


def get_db():
    """
    FastAPI Dependency
    """

    db = SessionLocal()

    try:

        yield db

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()