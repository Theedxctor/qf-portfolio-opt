# tables/__init__.py
from typing import Any
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Base Class for SQLAlchemy"""
    def __repr__(self) -> str:
        return get_attributes(self)

def get_attributes(obj: Any) -> str:
    """Helper to make printing/debugging your data much cleaner"""
    class_ = obj.__class__.__name__
    # This grabs the column names and values automatically
    attrs = sorted((k, getattr(obj, k)) for k in obj.__mapper__.column.keys())
    sattrs = ", ".join("{}={!r}".format(*x) for x in attrs)
    return f"{class_}({sattrs})"