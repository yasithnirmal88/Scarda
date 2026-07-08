from sqlalchemy.orm import Session

from app.models.section import Section
from app.repositories.base import BaseRepository


class SectionRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)

    def get_all(self) -> list[Section]:
        return self.db.query(Section).all()

    def get_by_id(self, section_id: int) -> Section | None:
        return self.db.query(Section).filter(Section.id == section_id).first()
