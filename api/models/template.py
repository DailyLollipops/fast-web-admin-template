from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

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
    modified_by_id: int = Field(foreign_key='users.id')

    modified_by: 'User' = Relationship(sa_relationship_kwargs={"lazy": "joined"}) # type: ignore  # noqa: F821
