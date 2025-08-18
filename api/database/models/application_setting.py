# pyright: reportAssignmentType=false
# pyright: reportUndefinedVariable=false
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class ApplicationSetting(SQLModel, table=True):
    __tablename__ = 'application_settings'

    id: int = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    value: str = Field(default='')
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(),
        sa_column_kwargs={'onupdate': lambda: datetime.now()}
    )
    modified_by_id: int | None = Field(foreign_key='users.id', nullable=True)

    modified_by: Optional['User'] = Relationship(sa_relationship_kwargs={"lazy": "joined"}) # noqa: F821
