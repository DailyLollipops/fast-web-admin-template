# Generated code for Branch model

from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlmodel import Session, select, asc, desc
import typing
import json

from database import get_db
from models.user import User
from models.branch import Branch
from .auth import get_current_user

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
    

@router.post('/branches', response_model=BranchResponse, tags=['Branch'])
def create_branch(
    data: BranchCreate,
	current_user: typing.Annotated[User, Depends(get_current_user)],   
    db: Session = Depends(get_db)
):
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
