from typing import Any
from sqlalchemy.ext.declarative import declared_attr
from app.db.base import Base


class BaseModel(Base):
    """
    Base class for all models with common attributes.
    """
    __abstract__ = True

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def dict(self) -> dict[str, Any]:
        """Convert model instance to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
