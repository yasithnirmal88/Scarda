"""Shared API dependencies."""

import logging
from collections.abc import Generator
from typing import Any

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.providers.interfaces import IDataProvider
from app.services.alert_engine import AlertEngine

logger = logging.getLogger(__name__)


def get_db_session(db: Session = Depends(get_db)) -> Generator[Session, None, None]:
    yield db


def get_provider(request: Request) -> IDataProvider:
    return request.app.state.provider


def get_alert_engine(request: Request) -> AlertEngine:
    return request.app.state.alert_engine
