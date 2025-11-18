"""
Database connection and session management.

This module provides database initialization, connection pooling,
and session management for both SQLite and PostgreSQL databases.
"""

import os
from typing import Generator, Optional
from contextlib import contextmanager
from sqlalchemy import create_engine, event, pool
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import QueuePool, NullPool
import logging

from .models import Base

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration class."""

    def __init__(
        self,
        database_url: Optional[str] = None,
        echo: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        pool_pre_ping: bool = True,
    ):
        """
        Initialize database configuration.

        Args:
            database_url: Database connection URL. If None, uses environment variable.
            echo: Enable SQL query logging.
            pool_size: Number of permanent connections.
            max_overflow: Maximum overflow connections.
            pool_timeout: Connection timeout in seconds.
            pool_recycle: Time in seconds to recycle connections.
            pool_pre_ping: Enable connection health checks.
        """
        self.database_url = database_url or self._get_database_url()
        self.echo = echo
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
        self.pool_pre_ping = pool_pre_ping
        self.is_sqlite = self.database_url.startswith("sqlite")
        self.is_async = "async" in self.database_url

    @staticmethod
    def _get_database_url() -> str:
        """
        Get database URL from environment variables.

        Priority:
        1. DATABASE_URL
        2. Build from components (DB_HOST, DB_NAME, etc.)
        3. Default to SQLite
        """
        # Check for full DATABASE_URL
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            return database_url

        # Check for PostgreSQL components
        db_type = os.getenv("DB_TYPE", "sqlite")

        if db_type == "postgresql":
            host = os.getenv("DB_HOST", "localhost")
            port = os.getenv("DB_PORT", "5432")
            user = os.getenv("DB_USER", "postgres")
            password = os.getenv("DB_PASSWORD", "postgres")
            database = os.getenv("DB_NAME", "ppe_detection")
            return f"postgresql://{user}:{password}@{host}:{port}/{database}"

        # Default to SQLite
        db_path = os.getenv("DB_PATH", "./data/ppe_detection.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        return f"sqlite:///{db_path}"


class Database:
    """Database manager for synchronous operations."""

    def __init__(self, config: Optional[DatabaseConfig] = None):
        """
        Initialize database manager.

        Args:
            config: Database configuration. If None, uses default config.
        """
        self.config = config or DatabaseConfig()
        self.engine = None
        self.SessionLocal = None
        self._initialized = False

    def initialize(self):
        """Initialize database engine and session factory."""
        if self._initialized:
            logger.warning("Database already initialized")
            return

        logger.info(f"Initializing database: {self.config.database_url}")

        # Create engine with appropriate settings
        engine_kwargs = {
            "echo": self.config.echo,
        }

        if self.config.is_sqlite:
            # SQLite-specific configuration
            engine_kwargs.update({
                "connect_args": {"check_same_thread": False},
                "poolclass": NullPool,  # Disable pooling for SQLite
            })
        else:
            # PostgreSQL-specific configuration
            engine_kwargs.update({
                "pool_size": self.config.pool_size,
                "max_overflow": self.config.max_overflow,
                "pool_timeout": self.config.pool_timeout,
                "pool_recycle": self.config.pool_recycle,
                "pool_pre_ping": self.config.pool_pre_ping,
                "poolclass": QueuePool,
            })

        self.engine = create_engine(self.config.database_url, **engine_kwargs)

        # Enable SQLite foreign keys
        if self.config.is_sqlite:
            @event.listens_for(self.engine, "connect")
            def set_sqlite_pragma(dbapi_conn, connection_record):
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

        # Create session factory
        self.SessionLocal = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine,
            )
        )

        self._initialized = True
        logger.info("Database initialized successfully")

    def create_tables(self):
        """Create all database tables."""
        if not self._initialized:
            self.initialize()

        logger.info("Creating database tables")
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created successfully")

    def drop_tables(self):
        """Drop all database tables. Use with caution!"""
        if not self._initialized:
            self.initialize()

        logger.warning("Dropping all database tables")
        Base.metadata.drop_all(bind=self.engine)
        logger.info("Database tables dropped")

    def get_session(self) -> Session:
        """
        Get a new database session.

        Returns:
            SQLAlchemy session instance.
        """
        if not self._initialized:
            self.initialize()

        return self.SessionLocal()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Provide a transactional scope for database operations.

        Yields:
            SQLAlchemy session instance.

        Example:
            with db.session_scope() as session:
                user = session.query(User).first()
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def close(self):
        """Close database connections."""
        if self.SessionLocal:
            self.SessionLocal.remove()
        if self.engine:
            self.engine.dispose()
        self._initialized = False
        logger.info("Database connections closed")


class AsyncDatabase:
    """Database manager for asynchronous operations."""

    def __init__(self, config: Optional[DatabaseConfig] = None):
        """
        Initialize async database manager.

        Args:
            config: Database configuration. If None, uses default config.
        """
        self.config = config or DatabaseConfig()
        # Convert sync URL to async URL
        if not self.config.is_async:
            if self.config.is_sqlite:
                self.config.database_url = self.config.database_url.replace(
                    "sqlite://", "sqlite+aiosqlite://"
                )
            else:
                self.config.database_url = self.config.database_url.replace(
                    "postgresql://", "postgresql+asyncpg://"
                )

        self.engine = None
        self.SessionLocal = None
        self._initialized = False

    async def initialize(self):
        """Initialize async database engine and session factory."""
        if self._initialized:
            logger.warning("Async database already initialized")
            return

        logger.info(f"Initializing async database: {self.config.database_url}")

        # Create async engine
        engine_kwargs = {
            "echo": self.config.echo,
        }

        if "sqlite" not in self.config.database_url:
            # PostgreSQL-specific configuration
            engine_kwargs.update({
                "pool_size": self.config.pool_size,
                "max_overflow": self.config.max_overflow,
                "pool_timeout": self.config.pool_timeout,
                "pool_recycle": self.config.pool_recycle,
                "pool_pre_ping": self.config.pool_pre_ping,
            })

        self.engine = create_async_engine(self.config.database_url, **engine_kwargs)

        # Create async session factory
        self.SessionLocal = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        self._initialized = True
        logger.info("Async database initialized successfully")

    async def create_tables(self):
        """Create all database tables asynchronously."""
        if not self._initialized:
            await self.initialize()

        logger.info("Creating database tables (async)")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully (async)")

    async def drop_tables(self):
        """Drop all database tables asynchronously. Use with caution!"""
        if not self._initialized:
            await self.initialize()

        logger.warning("Dropping all database tables (async)")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("Database tables dropped (async)")

    async def get_session(self) -> AsyncSession:
        """
        Get a new async database session.

        Returns:
            Async SQLAlchemy session instance.
        """
        if not self._initialized:
            await self.initialize()

        return self.SessionLocal()

    async def close(self):
        """Close async database connections."""
        if self.engine:
            await self.engine.dispose()
        self._initialized = False
        logger.info("Async database connections closed")


# Global database instances
db = Database()
async_db = AsyncDatabase()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database sessions in FastAPI or similar frameworks.

    Yields:
        Database session.

    Example:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()


async def get_async_db() -> AsyncSession:
    """
    Dependency for getting async database sessions.

    Yields:
        Async database session.

    Example:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_async_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
    """
    async with async_db.SessionLocal() as session:
        yield session


def init_db(database_url: Optional[str] = None, create_tables: bool = True):
    """
    Initialize database with optional table creation.

    Args:
        database_url: Optional database URL override.
        create_tables: Whether to create tables automatically.

    Example:
        init_db("postgresql://user:pass@localhost/dbname")
    """
    config = DatabaseConfig(database_url=database_url) if database_url else None
    global db
    db = Database(config)
    db.initialize()

    if create_tables:
        db.create_tables()

    return db


async def init_async_db(database_url: Optional[str] = None, create_tables: bool = True):
    """
    Initialize async database with optional table creation.

    Args:
        database_url: Optional database URL override.
        create_tables: Whether to create tables automatically.

    Example:
        await init_async_db("postgresql+asyncpg://user:pass@localhost/dbname")
    """
    config = DatabaseConfig(database_url=database_url) if database_url else None
    global async_db
    async_db = AsyncDatabase(config)
    await async_db.initialize()

    if create_tables:
        await async_db.create_tables()

    return async_db
