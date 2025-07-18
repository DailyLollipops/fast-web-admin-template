from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import List
from .machine_product_link import MachineProductLink

class Product(SQLModel, table=True):
    __tablename__ = 'products'
    id: int = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    description: str = Field(...)
    image: str = Field(...)

    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(), 
        sa_column_kwargs={'onupdate': lambda: datetime.now()}
    )

    machines: List['Machine'] = Relationship( # type: ignore
        back_populates='products',
        link_model=MachineProductLink
    )
