from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint
from typing import List, Optional

class MachineProductLink(SQLModel, table=True):
    __tablename__ = 'machine_product_link'
    __table_args__ = (UniqueConstraint('machine_id', 'product_id'),)

    id: int = Field(default=None, primary_key=True)
    machine_id: int = Field(foreign_key='machines.id')
    product_id: int = Field(foreign_key='products.id')

    audits: List['Audit'] = Relationship( # type: ignore
        back_populates='machine_product_link', 
        sa_relationship_kwargs={'cascade':'all, delete-orphan'}
    )
