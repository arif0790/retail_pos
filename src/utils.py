# ------------------------------------------------------------------
#  src/utils.py
# ------------------------------------------------------------------
"""
Utility functions for the POS Application.

Contains core helper functions used throughout the application:
- db_connect: Establishes database connection
- get_logger: Configures and returns logger instance

These utilities are designed to be simple, reusable, and testable.
"""

import logging
from typing import Optional
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Global variables for database connection
_DATABASE_URL = "sqlite:///data/db.sqlite3"
_engine: Optional[create_engine] = None
_session: Optional[Session] = None

def db_connect() -> Session:
    """
    Establishes and returns a database session.

    Uses SQLite by default (from environment.yml), but can be adapted
    for PostgreSQL/MySQL by changing the connection string.

    Returns:
        SQLAlchemy Session object ready for queries.

    Example usage:
        >>> session = db_connect()
        >>> user = session.query(User).first()
    """
    global _engine, _session

    if _engine is None:
        # Create engine if it doesn't exist
        _engine = create_engine(_DATABASE_URL)

        # Ensure database directory exists
        Path("data").mkdir(exist_ok=True)

    if _session is None or not _session.is_active:
        # Create new session if none exists or previous one is closed
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=_engine)
        _session = Session()

    return _session

def get_logger(name: str = "posapp") -> logging.Logger:
    """
    Configures and returns a logger instance.

    Sets up basic logging configuration with:
    - Console output (stream handler)
    - Formatted messages including timestamp
    - Error level filtering

    Args:
        name: Name of the logger (defaults to "posapp")

    Returns:
        Configured Logger instance.

    Example usage:
        >>> logger = get_logger()
        >>> logger.info("Application started")
    """
    logger = logging.getLogger(name)

    if not logger.handlers:  # Avoid duplicate handlers
        logger.setLevel(logging.INFO)

        # Create console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Create formatter and add it to handler
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        ch.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(ch)

    return logger

# Initialize global logger for this module
logger = get_logger(__name__)
