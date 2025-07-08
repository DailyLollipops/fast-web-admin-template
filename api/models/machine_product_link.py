from sqlmodel import SQLModel, Field

class MachineProductLink(SQLModel, table=True):
    __tablename__ = 'machine_product_link'
    machine_id: int = Field(foreign_key='machines.id', primary_key=True)
    product_id: int = Field(foreign_key='products.id', primary_key=True)
