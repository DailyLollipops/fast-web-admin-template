# pyright: reportAssignmentType=false
# pyright: reportUndefinedVariable=false
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel


class Notification(SQLModel, table=True):
    __tablename__ = 'notifications'

    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key='users.id')
    triggered_by: int = Field(...)
    
    title: str
    body: str
    seen: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(),
        sa_column_kwargs={'onupdate': lambda: datetime.now()}
    )

    user: 'User' = Relationship( # noqa: F821
        sa_relationship_kwargs={"primaryjoin": "User.id == Notification.user_id"},
        back_populates='notifications'
    )
