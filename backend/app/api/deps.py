"""Shared API dependencies."""

from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db


def get_db_session(db: Session = Depends(get_db)) -> Generator[Session, None, None]:
    """Provide a database session to endpoint handlers."""
    yield db
