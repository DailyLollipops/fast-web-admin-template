# pyright: reportAssignmentType=false
# pyright: reportUndefinedVariable=false
from datetime import datetime

from sqlmodel import JSON, Column, Field, Relationship, SQLModel


class User(SQLModel, table=True):
    __tablename__ = 'users' # type: ignore

    id: int = Field(default=None, primary_key=True)
    name: str = Field(...)
    email: str = Field(unique=True)
    role: str = Field(default='user')
    provider: str = Field(default='native')
    provider_id: str | None = Field(nullable=True, default=None)
    password: str | None = Field(nullable=True, default=None)
    profile: str | None = Field(nullable=True, default=None)
    verified: bool = Field(default=False)
    api: str | None = Field(nullable=True, default=None)
    tfa_secret: str | None = Field(nullable=True, default=None)
    tfa_methods: list[str] = Field(sa_column=Column(JSON), default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(),
        sa_column_kwargs={'onupdate': lambda: datetime.now()}
    )

    notifications: list['Notification'] = Relationship( # noqa: F821
        back_populates='user',
        sa_relationship_kwargs={'cascade':'all, delete-orphan'}
    )
