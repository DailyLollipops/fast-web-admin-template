# Generated code for Machine model

from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlmodel import Session, select, asc, desc
import typing
import json

from database import get_db
from models.user import User
from models.machine import Machine
from .auth import get_current_user

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
    

@router.post('/machines', response_model=MachineResponse, tags=['Machine'])
def create_machine(
    data: MachineCreate,
	current_user: typing.Annotated[User, Depends(get_current_user)],   
    db: Session = Depends(get_db)
):
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
