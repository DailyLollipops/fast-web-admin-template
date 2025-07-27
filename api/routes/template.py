# Generated code for Template model

from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlmodel import Session, select, asc, desc, func
from typing import Annotated, List, Optional
import json

from database import get_db
from models.user import User
from models.template import Template
from .auth import get_current_user

router = APIRouter()


class ActionResponse(BaseModel):
    success: bool
    message: str


class TemplateCreate(BaseModel):
    name: str
    template_type: str
    path: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    modified_by_id: int
    

class TemplateResponse(BaseModel):
    id: int
    name: str
    template_type: str
    path: str
    created_at: datetime
    updated_at: datetime
    modified_by_id: int
    

class TemplateListResponse(BaseModel):
    total: int
    data: List[TemplateResponse]


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    template_type: Optional[str] = None
    path: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    modified_by_id: Optional[int] = None


@router.post('/templates', response_model=TemplateResponse, tags=['Template'])
def create_template(
    data: TemplateCreate,
	current_user: Annotated[User, Depends(get_current_user)],   
    db: Session = Depends(get_db)
):
    try:
        if db.exec(select(Template).where(Template.name == data.name)).first():
            raise HTTPException(
                status_code=400,
                detail=f'Template with name of {data.name} already exists'
            )
            
        template = Template(**data.model_dump())
        db.add(template)
        db.commit()
        return template
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/templates', response_model=TemplateListResponse, tags=['Template'])
def get_templates(
	current_user: Annotated[User, Depends(get_current_user)],  
    order_field: str = 'id', 
    order_by: str = 'desc', 
    limit: Optional[int] = None, 
    offset: Optional[int] = None,
    filters: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        query = select(Template)

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
                if key not in Template.model_fields:
                    continue
                column = getattr(Template, key)
                query = query.where(column == value)

        if order_field is not None:
            if order_field not in Template.model_fields:
                raise HTTPException(
                    status_code=400,
                    detail=f'{order_field} is not a valid field'
                )
            if order_by == 'asc':
                query = query.order_by(asc(getattr(Template, order_field)))
            else:
                query = query.order_by(desc(getattr(Template, order_field)))

        count_query = select(func.count()).select_from(query.subquery())
        total = db.exec(count_query).first() or 0

        if offset is not None:
            query = query.offset(offset)

        if limit is not None:
            query = query.limit(limit)

        templates = db.exec(query).all()
        templates = [TemplateResponse(**d.model_dump()) for d in templates]
        return TemplateListResponse(total=total, data=templates)
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/templates/{id}', response_model=TemplateResponse, tags=['Template'])
def get_template(
	current_user: Annotated[User, Depends(get_current_user)],  
    id: int, 
    db: Session = Depends(get_db)
):
    try:
        query = select(Template).where(Template.id == id)
        template = db.exec(query).first()
        if not template:
            raise HTTPException(status_code=404, detail='Template not found')
        return template
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch('/templates/{id}', response_model=TemplateResponse, tags=['Template'])
def update_template(
    id: int, 
    data: TemplateUpdate,
	current_user: Annotated[User, Depends(get_current_user)],  
    db: Session = Depends(get_db)
):
    try:
        query = select(Template).where(Template.id == id)
        template = db.exec(query).first()
        if not template:
            raise HTTPException(
                status_code=404,
                detail='Template not found'
            )
            
        if db.exec(select(Template).where(Template.name == data.name).where(Template.id != template.id)).first():
            raise HTTPException(
                status_code=400,
                detail=f'Template with name of {data.name} already exists'
            )
            
        data_dict = data.model_dump()
        for field in data_dict:
            if hasattr(template, field) and data_dict[field]:
                setattr(template, field, data_dict[field])
        
        db.add(template)
        db.commit()
        db.refresh(template)
        return template
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete('/templates/{id}', response_model=ActionResponse, tags=['Template'])
def delete_template(
    id: int,
	current_user: Annotated[User, Depends(get_current_user)],  
    db: Session = Depends(get_db)
):
    try:
        query = select(Template).where(Template.id == id)
        template = db.exec(query).first()
        if not template:
            raise HTTPException(status_code=404, detail='Template not found')
        db.delete(template)
        db.commit()
        return ActionResponse(
            success=True,
            message='Template deleted successfully'
        )
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
