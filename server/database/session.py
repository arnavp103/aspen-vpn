"""Database session management"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from contextlib import contextmanager


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models"""

    pass


class DatabaseSession:
    """Singleton database session factory"""

    _instance = None
    _engine = None
    _session_factory = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseSession, cls).__new__(cls)
            cls._instance._engine = create_engine(
                "sqlite:///./vpn.db",
                connect_args={"check_same_thread": False},
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
            )
            cls._instance._session_factory = sessionmaker(
                autocommit=False, autoflush=False, bind=cls._instance._engine
            )
        return cls._instance

    @contextmanager
    def get_session(self):
        """Get database session with context management"""
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @property
    def engine(self):
        """Get SQLAlchemy engine"""
        return self._engine


db = DatabaseSession()


def get_db():
    """Get database session for FastAPI dependency injection"""
    with db.get_session() as session:
        yield session
