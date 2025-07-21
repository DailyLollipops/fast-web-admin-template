# Generated code for Audit model

from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlmodel import Session, select
from sqlalchemy.orm import aliased
import typing
import json

from database import get_db
from models.user import User
from models.audit import Audit
from models.machine import Machine
from models.machine_product_link import MachineProductLink
from .auth import get_current_user
from .user import UserRole

router = APIRouter()


class ActionResponse(BaseModel):
    success: bool
    message: str
    

class AuditResponse(BaseModel):
    id: int | None = None
    user_id: int
    branch_id: int
    machine_id: int
    product_id: int
    remaining: float | None = None
    dispensed: float | None = None
    expenses: float | None = None
    price: float | None = None
    sales: float | None = None
    refill_amount: float | None = None
    category: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


@router.get('/audits', response_model=typing.List[AuditResponse], tags=['Audit'])
def get_audits(
    current_user: typing.Annotated[User, Depends(get_current_user)],
    order_field: str = 'id',
    order_by: str = 'desc',
    limit: int = None,
    offset: int = None,
    filters: str = None,
    db: Session = Depends(get_db)
):
    try:
        # Aliases for clarity
        mp_link_alias = aliased(MachineProductLink)
        machine_alias = aliased(Machine)

        # Start base query with joins
        query = (
            select(
                Audit,
                machine_alias.branch_id,
                mp_link_alias.machine_id,
                mp_link_alias.product_id
            )
            .join(mp_link_alias, Audit.machine_product_link_id == mp_link_alias.id)
            .join(machine_alias, mp_link_alias.machine_id == machine_alias.id)
        )

        if filters:
            try:
                filters_dict = json.loads(filters)
                if not isinstance(filters_dict, dict):
                    raise HTTPException(status_code=400, detail='Invalid filter parameter')
            except Exception:
                raise HTTPException(status_code=400, detail='Invalid filter parameter')

            for key, value in filters_dict.items():
                if key in Audit.model_fields:
                    query = query.where(getattr(Audit, key) == value)
                elif key == "machine_id":
                    query = query.where(mp_link_alias.machine_id == value)
                elif key == "product_id":
                    query = query.where(mp_link_alias.product_id == value)
                elif key == "branch_id":
                    query = query.where(machine_alias.branch_id == value)

        if current_user.role == UserRole.pump_attendant:
            query = query.where(Audit.user_id == current_user.id)

        if order_field:
            sort_col = None
            if order_field in Audit.model_fields:
                sort_col = getattr(Audit, order_field)
            elif order_field == "machine_id":
                sort_col = mp_link_alias.machine_id
            elif order_field == "product_id":
                sort_col = mp_link_alias.product_id
            elif order_field == "branch_id":
                sort_col = machine_alias.branch_id
            else:
                raise HTTPException(status_code=400, detail=f'{order_field} is not a valid field')

            query = query.order_by(sort_col.asc() if order_by == 'asc' else sort_col.desc())

        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)

        results = db.exec(query).all()

        return [
            AuditResponse(
                **audit.model_dump(),
                branch_id=branch_id,
                machine_id=machine_id,
                product_id=product_id,
            )
            for audit, branch_id, machine_id, product_id in results
        ]

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/audits/{id}', response_model=AuditResponse, tags=['Audit'])
def get_audit(
	current_user: typing.Annotated[User, Depends(get_current_user)],  
    id: int, 
    db: Session = Depends(get_db)
):
    try:
        query = select(Audit).where(Audit.id == id)

        if current_user == UserRole.pump_attendant:
            query = query.where(Audit.user_id == current_user.id)

        audit = db.exec(query).first()
        if not audit:
            raise HTTPException(status_code=404, detail='Audit not found')
        machine = db.get(Machine, audit.machine_product_link.machine_id)
        if not machine:
            raise HTTPException(status_code=404, detail='Machine not found')
        response = AuditResponse(
            **audit.model_dump(),
            branch_id=machine.branch_id,
            machine_id=audit.machine_product_link.machine_id,
            product_id=audit.machine_product_link.product_id,
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
