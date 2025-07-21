# Generated code for Machine model

from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from sqlmodel import Session, select, asc, desc, func
from sqlalchemy.orm import aliased
import typing
import json

from database import get_db
from models.user import User
from models.machine import Machine
from models.product import Product
from models.machine_product_link import MachineProductLink
from models.audit import Audit
from .auth import get_current_user
from .user import UserRole

router = APIRouter()


class ActionResponse(BaseModel):
    success: bool
    message: str


class MachineCreate(BaseModel):
    branch_id: int
    name: str
    created_at: datetime = None
    updated_at: datetime = None
    

class MachineResponse(BaseModel):
    id: int | None = None
    branch_id: int
    name: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    

class MachineUpdate(BaseModel):
    branch_id: int = None
    name: str = None
    created_at: datetime = None
    updated_at: datetime = None
    

class MachineProductCreate(BaseModel):
    product_id: int
    created_at: datetime = None
    updated_at: datetime = None


class MachineProductStatsResponse(BaseModel):
    remaining: float
    price: float
    sale: float


class MachineProductResponse(BaseModel):
    id: int | None = None
    name: str
    description: str = None
    image: str = None
    remaining: float | None = None
    last_price: float | None = None
    last_sale: float | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class MachineSaleCreate(BaseModel):
    dispensed: float
    price: float
    expenses: float
    created_at: datetime = None
    updated_at: datetime = None


class MachineRefillCreate(BaseModel):
    refill_amount: float
    created_at: datetime = None
    updated_at: datetime = None


class MachineAuditResponse(BaseModel):
    id: int | None = None
    user_id: int
    remaining: float | None = None
    dispensed: float | None = None
    expenses: float | None = None
    price: float | None = None
    sales: float | None = None
    refill_amount: float | None = None
    category: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


permissions = {
    'create': [UserRole.admin, UserRole.owner, UserRole.admin_inventory],
    'read': [UserRole.admin, UserRole.owner, UserRole.admin_inventory],
    'update': [UserRole.admin, UserRole.owner, UserRole.admin_inventory],
    'delete': [UserRole.admin, UserRole.owner, UserRole.admin_inventory],
    'sales': [UserRole.pump_attendant]
}

@router.post('/machines', response_model=MachineResponse, tags=['Machine'])
def create_machine(
    data: MachineCreate,
	current_user: typing.Annotated[User, Depends(get_current_user)],   
    db: Session = Depends(get_db)
):
    if current_user.role not in permissions['create']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='No access to resource',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    try:
        machine = Machine(**data.model_dump())
        db.add(machine)
        db.commit()
        return machine
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/machines', response_model=typing.List[MachineResponse], tags=['Machine'])
def get_machines(
	current_user: typing.Annotated[User, Depends(get_current_user)],  
    order_field: str = 'id', 
    order_by: str = 'desc', 
    limit: int = None, 
    offset: int = None, 
    filters: str = None, 
    db: Session = Depends(get_db)
):
    try:
        query = select(Machine)
        if filters:
            filters_dict = {}
            filter_exc = HTTPException(status_code=400, detail='Invalid filter parameter')
            try:
                filters_dict = json.loads(filters)
                if not isinstance(filters_dict, dict):
                    raise filter_exc
            except Exception:
                raise filter_exc
            for key, value in filters_dict.items():
                if key not in Machine.model_fields:
                    continue
                column = getattr(Machine, key)
                query = query.where(column == value)
        if order_field is not None:
            if order_field not in Machine.model_fields:
                raise HTTPException(
                    status_code=400,
                    detail=f'{order_field} is not a valid field'
                )
            if order_by == 'asc':
                query = query.order_by(asc(getattr(Machine, order_field)))
            else:
                query = query.order_by(desc(getattr(Machine, order_field)))
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)
        machines = db.exec(query).all()
        return machines
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/machines/{id}', response_model=MachineResponse, tags=['Machine'])
def get_machine(
	current_user: typing.Annotated[User, Depends(get_current_user)],  
    id: int, 
    db: Session = Depends(get_db)
):
    try:
        query = select(Machine).where(Machine.id == id)
        machine = db.exec(query).first()
        if not machine:
            raise HTTPException(status_code=404, detail='Machine not found')
        return machine
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch('/machines/{id}', response_model=MachineResponse, tags=['Machine'])
def update_machine(
    id: int, 
    data: MachineUpdate,
	current_user: typing.Annotated[User, Depends(get_current_user)],  
    db: Session = Depends(get_db)
):
    if current_user.role not in permissions['update']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='No access to resource',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    try:
        query = select(Machine).where(Machine.id == id)
        machine = db.exec(query).first()
        if not machine:
            raise HTTPException(
                status_code=404,
                detail='Machine not found'
            )
            
        data_dict = data.model_dump()
        for field in data_dict:
            if hasattr(machine, field) and data_dict[field]:
                setattr(machine, field, data_dict[field])
        
        db.add(machine)
        db.commit()
        db.refresh(machine)
        return machine
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete('/machines/{id}', response_model=ActionResponse, tags=['Machine'])
def delete_machine(
    id: int,
	current_user: typing.Annotated[User, Depends(get_current_user)],  
    db: Session = Depends(get_db)
):
    if current_user.role not in permissions['delete']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='No access to resource',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    try:
        query = select(Machine).where(Machine.id == id)
        machine = db.exec(query).first()
        if not machine:
            raise HTTPException(status_code=404, detail='Machine not found')
        db.delete(machine)
        db.commit()
        return ActionResponse(
            success=True,
            message=f'Machine deleted successfully'
        )
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/machines/{id}/products', response_model=MachineProductResponse, tags=['Machine'])
def create_machine_product(
	current_user: typing.Annotated[User, Depends(get_current_user)],  
    id: int, 
    data: MachineProductCreate,
    db: Session = Depends(get_db)
):
    if current_user.role not in permissions['create']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='No access to resource',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    try:
        machine = db.get(Machine, id)
        if not machine:
            raise HTTPException(status_code=404, detail='Machine not found')
        product = db.get(Product, data.product_id)
        if not product:
            raise HTTPException(status_code=404, detail='Product not found')
        machine.products.append(product)
        db.add(machine)
        db.commit()
        db.refresh(product)
        return product
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/machines/{id}/products', response_model=typing.List[MachineProductResponse], tags=['Machine'])
def get_machine_products(
    current_user: typing.Annotated[User, Depends(get_current_user)],
    id: int,
    order_field: str = 'id',
    order_by: str = 'desc',
    limit: int = None,
    offset: int = None,
    filters: str = None,
    db: Session = Depends(get_db)
):
    try:
        AuditAlias = aliased(Audit)

        latest_audit_subq = (
            select(
                AuditAlias.id.label('audit_id'),
                AuditAlias.machine_product_link_id,
                AuditAlias.remaining,
                AuditAlias.sales,
                AuditAlias.price,
                func.row_number().over(
                    partition_by=AuditAlias.machine_product_link_id,
                    order_by=desc(AuditAlias.created_at)
                ).label('rnk')
            )
        ).subquery()

        query = (
            select(
                Product,
                latest_audit_subq.c.remaining,
                latest_audit_subq.c.sales,
                latest_audit_subq.c.price
            )
            .join(MachineProductLink, MachineProductLink.product_id == Product.id)
            .outerjoin(latest_audit_subq, latest_audit_subq.c.machine_product_link_id == MachineProductLink.id)
            .where(MachineProductLink.machine_id == id)
            .where(
                (latest_audit_subq.c.rnk == 1) | (latest_audit_subq.c.rnk.is_(None))
            )
        )

        if filters:
            try:
                filters_dict = json.loads(filters)
                for key, value in filters_dict.items():
                    if hasattr(Product, key):
                        query = query.where(getattr(Product, key) == value)
            except Exception:
                raise HTTPException(status_code=400, detail='Invalid filter parameter')

        if hasattr(Product, order_field):
            order_column = getattr(Product, order_field)
            query = query.order_by(order_column.asc() if order_by == 'asc' else order_column.desc())
        else:
            raise HTTPException(status_code=400, detail=f'{order_field} is not a valid field')

        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)

        results = db.exec(query).all()
        return [
            MachineProductResponse(
                **product.dict(),
                remaining=remaining,
                last_sale=sales,
                last_price=price
            )
            for product, remaining, sales, price in results
        ]

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/machines/{id}/products/{product_id}', response_model=MachineProductResponse, tags=['Machine'])
def get_machine_product(
    current_user: typing.Annotated[User, Depends(get_current_user)],
    id: int,
    product_id: int,
    db: Session = Depends(get_db)
):
    try:
        AuditAlias = aliased(Audit)

        latest_audit_subq = (
            select(
                AuditAlias.id.label("audit_id"),
                AuditAlias.machine_product_link_id,
                AuditAlias.remaining,
                AuditAlias.sales,
                AuditAlias.price,
                func.row_number().over(
                    partition_by=AuditAlias.machine_product_link_id,
                    order_by=desc(AuditAlias.created_at)
                ).label("rnk")
            ).subquery()
        )

        query = (
            select(
                Product,
                latest_audit_subq.c.remaining,
                latest_audit_subq.c.sales,
                latest_audit_subq.c.price
            )
            .join(MachineProductLink, MachineProductLink.product_id == Product.id)
            .outerjoin(latest_audit_subq, latest_audit_subq.c.machine_product_link_id == MachineProductLink.id)
            .where(MachineProductLink.machine_id == id)
            .where(Product.id == product_id)
            .where(
                (latest_audit_subq.c.rnk == 1) | (latest_audit_subq.c.rnk.is_(None))
            )
        )

        result = db.exec(query).first()
        if not result:
            raise HTTPException(status_code=404, detail='Product not found for this machine')

        product, remaining, sales, price = result

        return MachineProductResponse(
            **product.dict(),
            remaining=remaining,
            last_sale=sales,
            last_price=price
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete('/machines/{id}/products/{product_id}', response_model=ActionResponse, tags=['Machine'])
def delete_machine_product(
    id: int,
    product_id: int,
	current_user: typing.Annotated[User, Depends(get_current_user)],  
    db: Session = Depends(get_db)
):
    if current_user.role not in permissions['delete']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='No access to resource',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    try:
        query = (
            select(MachineProductLink)
            .where(MachineProductLink.machine_id == id)
            .where(MachineProductLink.product_id == product_id)
        )
        mp_link = db.exec(query).first()
        if not mp_link:
            raise HTTPException(status_code=404, detail='MachineProductLink not found')
        db.delete(mp_link)
        db.commit()
        return ActionResponse(
            success=True,
            message=f'MachineProductLink deleted successfully'
        )
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/machines/{id}/products/{product_id}/refill', response_model=MachineAuditResponse, tags=['Machine'])
def refill_machine_product(
	current_user: typing.Annotated[User, Depends(get_current_user)],  
    id: int, 
    product_id: int,
    data: MachineRefillCreate,
    db: Session = Depends(get_db)
):
    if current_user.role not in permissions['create']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='No access to resource',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    try:
        machine = db.get(Machine, id)
        if not machine:
            raise HTTPException(status_code=404, detail='Machine not found')
        product = db.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail='Product not found')
        
        query = (
            select(MachineProductLink)
            .where(MachineProductLink.machine_id == id)
            .where(MachineProductLink.product_id == product_id)
        )
        mp_link = db.exec(query).first()
        if not mp_link:
            raise HTTPException(status_code=404, detail='MachineProductLink not found')

        remaining = 0
        query = (
            select(Audit)
            .where(Audit.machine_product_link_id == mp_link.id)
            .order_by(desc(Audit.created_at))
        )
        latest_audit = db.exec(query).first()
        if latest_audit:
            remaining = latest_audit.remaining

        audit = Audit(
            user_id=current_user.id,
            machine_product_link_id=mp_link.id,
            remaining=remaining + data.refill_amount,
            refill_amount=data.refill_amount,
            category='refill'
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)
        return audit
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/machines/{id}/products/{product_id}/sales', response_model=MachineAuditResponse, tags=['Machine'])
def add_machine_product_sale(
	current_user: typing.Annotated[User, Depends(get_current_user)],  
    id: int, 
    product_id: int,
    data: MachineSaleCreate,
    db: Session = Depends(get_db)
):
    if current_user.role not in permissions['sales']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='No access to resource',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    try:
        machine = db.get(Machine, id)
        if not machine:
            raise HTTPException(status_code=404, detail='Machine not found')
        product = db.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail='Product not found')
        
        query = (
            select(MachineProductLink)
            .where(MachineProductLink.machine_id == id)
            .where(MachineProductLink.product_id == product_id)
        )
        mp_link = db.exec(query).first()
        if not mp_link:
            raise HTTPException(status_code=404, detail='MachineProductLink not found')

        remaining = 0
        query = (
            select(Audit)
            .where(Audit.machine_product_link_id == mp_link.id)
            .order_by(desc(Audit.created_at))
        )
        latest_audit = db.exec(query).first()
        if latest_audit:
            remaining = latest_audit.remaining

        audit = Audit(
            user_id=current_user.id,
            machine_product_link_id=mp_link.id,
            remaining=remaining - data.dispensed,
            dispensed=data.dispensed,
            price=data.price,
            sales=data.dispensed * data.price,
            expenses=data.expenses,
            category='sales'
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)
        return audit
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/machines/{id}/products/{product_id}/audits', response_model=typing.List[MachineAuditResponse], tags=['Machine'])
def get_machine_product_audit(
	current_user: typing.Annotated[User, Depends(get_current_user)],
    id: int,
    product_id: int,
    order_field: str = 'id', 
    order_by: str = 'desc', 
    limit: int = None, 
    offset: int = None, 
    filters: str = None, 
    db: Session = Depends(get_db)
):
    try:
        query = (
            select(MachineProductLink)
            .where(MachineProductLink.machine_id == id)
            .where(MachineProductLink.product_id == product_id)
        )
        mp_link = db.exec(query).first()
        if not mp_link:
            raise HTTPException(status_code=404, detail='MachineProductLink not found')

        query = (
            select(Audit)
            .where(Audit.machine_product_link_id == mp_link.id)
        )

        if filters:
            try:
                filters_dict = json.loads(filters)
                if not isinstance(filters_dict, dict):
                    raise HTTPException(status_code=400, detail='Invalid filter format')
            except Exception:
                raise HTTPException(status_code=400, detail='Invalid filter parameter')
            
            for key, value in filters_dict.items():
                if key not in Audit.model_fields:
                    continue
                column = getattr(Audit, key)
                query = query.where(column == value)

        if order_field not in Audit.model_fields:
            raise HTTPException(status_code=400, detail=f'{order_field} is not a valid field')
        order_column = getattr(Audit, order_field)
        query = query.order_by(order_column.asc() if order_by == 'asc' else order_column.desc())

        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)

        audits = db.exec(query).all()
        return audits
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

