from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Entity(Base):
    __abstract__ = True

    def as_dict(self):
        """Dictionary representation of entity"""
