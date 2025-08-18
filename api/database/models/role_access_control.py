# pyright: reportAssignmentType=false
# pyright: reportUndefinedVariable=false
from datetime import datetime
from typing import Optional

from sqlmodel import JSON, Column, Field, Relationship, SQLModel


class RoleAccessControl(SQLModel, table=True):
    __tablename__ = 'role_access_control'

    id: int = Field(default=None, primary_key=True)
    modified_by_id: int | None = Field(foreign_key='users.id', nullable=True)

    role: str = Field(unique=True)
    permissions: list[str] = Field(sa_column=Column(JSON), default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(),
        sa_column_kwargs={'onupdate': lambda: datetime.now()}
    )

    modified_by: Optional['User'] = Relationship(sa_relationship_kwargs={"lazy": "joined"}) # noqa: F821
