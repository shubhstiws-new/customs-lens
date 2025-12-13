"""
Database Connection Module
Handles Azure SQL Database connectivity
"""

import os
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from .models import Base

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / "config" / ".env")

# Database configuration
SQL_SERVER = os.getenv("AZURE_SQL_SERVER", "")
SQL_DATABASE = os.getenv("AZURE_SQL_DATABASE", "boe")
SQL_USERNAME = os.getenv("AZURE_SQL_USERNAME", "")
SQL_PASSWORD = os.getenv("AZURE_SQL_PASSWORD", "")

# Connection string for Azure SQL with ODBC
def get_connection_string() -> str:
    """Build connection string for Azure SQL Database"""

    # For Azure SQL with pyodbc
    # Using ODBC Driver 18 for SQL Server (latest)
    driver = "ODBC Driver 18 for SQL Server"

    conn_str = (
        f"mssql+pyodbc://{quote_plus(SQL_USERNAME)}:{quote_plus(SQL_PASSWORD)}"
        f"@{SQL_SERVER}/{SQL_DATABASE}"
        f"?driver={quote_plus(driver)}"
        f"&Encrypt=yes"
        f"&TrustServerCertificate=no"
        f"&Connection Timeout=30"
    )

    return conn_str


def get_engine(echo: bool = False):
    """Create SQLAlchemy engine for Azure SQL"""

    conn_str = get_connection_string()

    engine = create_engine(
        conn_str,
        echo=echo,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,  # Recycle connections every 30 minutes
    )

    return engine


def get_session() -> Session:
    """Create a new database session"""
    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


def init_db(engine=None, drop_existing: bool = False):
    """Initialize database schema"""

    if engine is None:
        engine = get_engine()

    # Create schemas first (Azure SQL requires explicit schema creation)
    schemas = ["header", "part1", "part2", "part3", "part4", "part5", "reference", "audit"]

    with engine.connect() as conn:
        for schema in schemas:
            try:
                conn.execute(text(f"""
                    IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = '{schema}')
                    BEGIN
                        EXEC('CREATE SCHEMA {schema}')
                    END
                """))
                conn.commit()
            except Exception as e:
                print(f"Schema {schema}: {e}")

    if drop_existing:
        Base.metadata.drop_all(engine)

    # Create all tables
    Base.metadata.create_all(engine)

    return engine


def test_connection() -> bool:
    """Test database connectivity"""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False


# Alternative: SQLite for local testing
def get_sqlite_engine(db_path: str = "boe_local.db", echo: bool = False):
    """Create SQLite engine for local testing"""

    engine = create_engine(
        f"sqlite:///{db_path}",
        echo=echo,
    )

    return engine


def init_sqlite_db(db_path: str = "boe_local.db"):
    """Initialize SQLite database for local testing"""

    engine = get_sqlite_engine(db_path)

    # SQLite doesn't support schemas, so we modify table names
    # For now, just create tables in default schema
    Base.metadata.create_all(engine)

    return engine
