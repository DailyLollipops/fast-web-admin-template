from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import List, Optional

class User(SQLModel, table=True):
    __tablename__ = 'users'
    id: int = Field(default=None, primary_key=True)
    branch_id: Optional[int] = Field(default=None, foreign_key='branches.id', nullable=True)

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

    branch: Optional['Branch'] = Relationship( # type:ignore
        back_populates='users',
        sa_relationship_kwargs={"primaryjoin": "Branch.id == User.branch_id"}
    )

    notifications: List['Notification'] = Relationship( # type: ignore
        back_populates='user', 
        sa_relationship_kwargs={'cascade':'all, delete-orphan'}
    ) 
