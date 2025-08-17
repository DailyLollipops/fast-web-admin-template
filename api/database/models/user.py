# pyright: reportAssignmentType=false
# pyright: reportUndefinedVariable=false
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    __tablename__ = 'users' # type: ignore

    id: int = Field(default=None, primary_key=True)
    name: str = Field(...)
    email: str = Field(unique=True)
    role: str = Field(default='user')
    password: str = Field(...)
    verified: bool = Field(default=False)
    api: str = Field(nullable=True, default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(),
        sa_column_kwargs={'onupdate': lambda: datetime.now()}
    )

    notifications: list['Notification'] = Relationship( # noqa: F821
        back_populates='user',
        sa_relationship_kwargs={'cascade':'all, delete-orphan'}
    )
