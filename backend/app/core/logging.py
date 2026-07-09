import logging
import sys

from app.config import settings


def setup_logging() -> None:
    cfg = settings.logging
    formatter = logging.Formatter(fmt=cfg.FORMAT, datefmt=cfg.DATE_FORMAT)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, cfg.LEVEL.upper(), logging.INFO))
    root_logger.addHandler(handler)

    logging.getLogger("uvicorn.access").setLevel(
        getattr(logging, cfg.UVICORN_ACCESS_LEVEL.upper(), logging.WARNING)
    )