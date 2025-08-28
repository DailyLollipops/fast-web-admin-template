# pyright: reportAssignmentType=false
# pyright: reportUndefinedVariable=false
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel


class Template(SQLModel, table=True):
    __tablename__ = 'templates'

    id: int = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    template_type: str = Field()
    path: str = Field()
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(),
        sa_column_kwargs={'onupdate': lambda: datetime.now()}
    )
    modified_by_id: int | None = Field(foreign_key='users.id', nullable=True)

    modified_by: 'User' = Relationship(sa_relationship_kwargs={"lazy": "joined"})  # noqa: F821
