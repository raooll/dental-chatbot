import datetime

from nanoid import generate
from sqlalchemy import Column, DateTime, String
from .database import Base


class BaseModel(Base):
    __abstract__ = True

    id = Column(String(length=12), primary_key=True, default=lambda: generate(size=12))
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc),
    )

    def as_dict(self):
        dict_ = {}
        for key in self.__mapper__.c.keys():
            dict_[key] = getattr(self, key)
        return dict_