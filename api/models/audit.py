from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class Audit(SQLModel, table=True):
    __tablename__ = 'audits'
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key='users.id')
    machine_product_link_id: int = Field(foreign_key='machine_product_link.id')
    remaining: float = Field(nullable=True)
    dispensed: float = Field(nullable=True)
    expenses: float = Field(nullable=True)
    price: float = Field(nullable=True)
    sales: float = Field(nullable=True)
    refill_amount: float = Field(nullable=True)
    category: str = Field(...)

    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(), 
        sa_column_kwargs={'onupdate': lambda: datetime.now()}
    )

    user: Optional['User'] = Relationship( # type:ignore
        back_populates='audits',
        sa_relationship_kwargs={'primaryjoin': 'User.id == Audit.user_id'}
    )

    machine_product_link: Optional['MachineProductLink'] = Relationship( # type:ignore
        back_populates='audits',
        sa_relationship_kwargs={'primaryjoin': 'MachineProductLink.id == Audit.machine_product_link_id'}
    )
