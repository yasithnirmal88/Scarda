from typing import Any

from sqlalchemy.orm import Session


class BaseRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, instance: Any) -> Any:
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def delete(self, instance: Any) -> None:
        self.db.delete(instance)
        self.db.commit()
