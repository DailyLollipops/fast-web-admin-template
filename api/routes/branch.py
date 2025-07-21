# Generated code for Branch model

from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from sqlmodel import Session, select, asc, desc
from sqlalchemy.orm import aliased
import typing
import json

from database import get_db
from models.user import User
from models.branch import Branch
from models.product import Product
from models.machine import Machine
from models.machine_product_link import MachineProductLink
from models.audit import Audit
from .auth import get_current_user
from .user import UserRole
from .audit import AuditResponse

router = APIRouter()


class ActionResponse(BaseModel):
    success: bool
    message: str


class BranchCreate(BaseModel):
    name: str
    province: str = None
    municipality: str = None
    barangay: str = None
    created_at: datetime = None
    updated_at: datetime = None
    

class BranchResponse(BaseModel):
    id: int | None = None
    name: str
    province: str | None = None
    municipality: str | None = None
    barangay: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    

class BranchUpdate(BaseModel):
    name: str = None
    province: str = None
    municipality: str = None
    barangay: str = None
    created_at: datetime = None
    updated_at: datetime = None
    

class BranchProductResponse(BaseModel):
    id: int | None = None
    name: str
    description: str = None
    image: str = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class BranchSales(BaseModel):
    machine_id: int
    product_id: int
    dispensed: float
    price: float
    expenses: float
    created_at: datetime = None
    updated_at: datetime = None


class BranchSaleCreate(BaseModel):
    sales: typing.List[BranchSales]


permissions = {
    'create': [UserRole.admin, UserRole.owner],
    'read': [UserRole.admin, UserRole.owner],
    'update': [UserRole.admin, UserRole.owner],
    'delete': [UserRole.admin, UserRole.owner],
    'sales': [UserRole.pump_attendant]
}

@router.post('/branches', response_model=BranchResponse, tags=['Branch'])
def create_branch(
    data: BranchCreate,
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
        if db.exec(select(Branch).where(Branch.name == data.name)).first():
            raise HTTPException(
                status_code=400,
                detail=f'Branch with name of {data.name} already exists'
            )
            
        branch = Branch(**data.model_dump())
        db.add(branch)
        db.commit()
        return branch
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/branches', response_model=typing.List[BranchResponse], tags=['Branch'])
def get_branchs(
	current_user: typing.Annotated[User, Depends(get_current_user)],  
    order_field: str = 'id', 
    order_by: str = 'desc', 
    limit: int = None, 
    offset: int = None, 
    filters: str = None, 
    db: Session = Depends(get_db)
):
    try:
        query = select(Branch)
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
                if key not in Branch.model_fields:
                    continue
                column = getattr(Branch, key)
                query = query.where(column == value)
        if order_field is not None:
            if order_field not in Branch.model_fields:
                raise HTTPException(
                    status_code=400,
                    detail=f'{order_field} is not a valid field'
                )
            if order_by == 'asc':
                query = query.order_by(asc(getattr(Branch, order_field)))
            else:
                query = query.order_by(desc(getattr(Branch, order_field)))
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)
        branchs = db.exec(query).all()
        return branchs
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/branches/{id}', response_model=BranchResponse, tags=['Branch'])
def get_branch(
	current_user: typing.Annotated[User, Depends(get_current_user)],  
    id: int, 
    db: Session = Depends(get_db)
):
    try:
        query = select(Branch).where(Branch.id == id)
        branch = db.exec(query).first()
        if not branch:
            raise HTTPException(status_code=404, detail='Branch not found')
        return branch
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch('/branches/{id}', response_model=BranchResponse, tags=['Branch'])
def update_branch(
    id: int, 
    data: BranchUpdate,
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
        query = select(Branch).where(Branch.id == id)
        branch = db.exec(query).first()
        if not branch:
            raise HTTPException(
                status_code=404,
                detail='Branch not found'
            )
            
        if db.exec(select(Branch).where(Branch.name == data.name).where(Branch.id != branch.id)).first():
            raise HTTPException(
                status_code=400,
                detail=f'Branch with name of {data.name} already exists'
            )
            
        data_dict = data.model_dump()
        for field in data_dict:
            if hasattr(branch, field) and data_dict[field]:
                setattr(branch, field, data_dict[field])
        
        db.add(branch)
        db.commit()
        db.refresh(branch)
        return branch
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete('/branches/{id}', response_model=ActionResponse, tags=['Branch'])
def delete_branch(
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
        query = select(Branch).where(Branch.id == id)
        branch = db.exec(query).first()
        if not branch:
            raise HTTPException(status_code=404, detail='Branch not found')
        db.delete(branch)
        db.commit()
        return ActionResponse(
            success=True,
            message=f'Branch deleted successfully'
        )
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/branches/{id}/products', response_model=typing.List[BranchProductResponse], tags=['Branch'])
def get_branch_products(
    current_user: typing.Annotated[User, Depends(get_current_user)],
    id: int,
    db: Session = Depends(get_db)
):
    try:
        branch = db.get(Branch, id)
        if not branch:
            raise HTTPException(status_code=404, detail='Branch not found')

        machine_alias = aliased(Machine)
        mp_link_alias = aliased(MachineProductLink)
        product_alias = aliased(Product)

        query = (
            select(product_alias)
            .join(mp_link_alias, mp_link_alias.product_id == product_alias.id)
            .join(machine_alias, machine_alias.id == mp_link_alias.machine_id)
            .where(machine_alias.branch_id == id)
            .distinct()
        )

        products = db.exec(query).all()

        return [BranchProductResponse(**p.model_dump()) for p in products]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/branches/{id}/sales', response_model=typing.List[AuditResponse], tags=['Branch'])
def add_branch_sale(
	current_user: typing.Annotated[User, Depends(get_current_user)],  
    id: int, 
    data: BranchSaleCreate,
    db: Session = Depends(get_db)
):
    if current_user.role not in permissions['sales']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='No access to resource',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    branch = db.get(Branch, id)
    if not branch:
        raise HTTPException(status_code=404, detail='Branch not found')

    if current_user.branch_id != branch.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='No access to resource',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    try:
        responses = []
        for sale in data.sales:
            machine = db.get(Machine, sale.machine_id)
            product = db.get(Product, sale.product_id)

            if not machine or not product or machine.branch_id != id:
                raise HTTPException(status_code=404, detail='Invalid machine or product')

            mp_link = db.exec(
                select(MachineProductLink)
                .where(
                    MachineProductLink.machine_id == sale.machine_id,
                    MachineProductLink.product_id == sale.product_id
                )
            ).first()

            if not mp_link:
                raise HTTPException(status_code=404, detail='MachineProductLink not found')

            latest = db.exec(
                select(Audit)
                .where(Audit.machine_product_link_id == mp_link.id)
                .order_by(desc(Audit.created_at))
            ).first()

            remaining = (latest.remaining if latest else 0) - sale.dispensed

            audit = Audit(
                user_id=current_user.id,
                machine_product_link_id=mp_link.id,
                remaining=remaining,
                dispensed=sale.dispensed,
                price=sale.price,
                sales=sale.dispensed * sale.price,
                expenses=sale.expenses,
                category='sales'
            )
            db.add(audit)
            response = AuditResponse(
                user_id=audit.user_id,
                branch_id=branch.id,
                machine_id=machine.id,
                product_id=product.id,
                remaining=audit.remaining,
                dispensed=audit.dispensed,
                price=audit.price,
                sales=audit.sales,
                expenses=audit.expenses,
                category=audit.category
            )
            responses.append(response)
        db.commit()
        return responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
