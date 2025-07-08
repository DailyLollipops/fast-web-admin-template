from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import List, Optional
from .machine_product_link import MachineProductLink

class Machine(SQLModel, table=True):
    __tablename__ = 'machines'
    id: int = Field(default=None, primary_key=True)
    branch_id: int = Field(foreign_key='branches.id')
    name: str

    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(), 
        sa_column_kwargs={'onupdate': lambda: datetime.now()}
    )

    branch: Optional['Branch'] = Relationship(back_populates='machines') # type: ignore
    products: List['Product'] = Relationship( # type: ignore
        back_populates='machines', link_model=MachineProductLink
    )
