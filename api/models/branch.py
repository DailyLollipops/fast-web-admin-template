from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import List

class Branch(SQLModel, table=True):
    __tablename__ = 'branches'
    id: int = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    province: str = Field(default=None, nullable=True)
    municipality: str = Field(default=None, nullable=True)
    barangay: str = Field(default=None, nullable=True)

    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(), 
        sa_column_kwargs={'onupdate': lambda: datetime.now()}
    )

    users: List['User'] = Relationship(back_populates='branch') # type: ignore
    machines: List['Machine'] = Relationship( # type: ignore
        back_populates='branch', 
        sa_relationship_kwargs={'cascade':'all, delete-orphan'}
    )
