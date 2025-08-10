from datetime import datetime
from enum import Enum
from typing import Annotated

from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models.template import Template
from models.user import User
from pydantic import BaseModel
from sqlmodel import Session

from .auth import get_current_user
from .utils import queryutil
from .utils.queryutil import GetListParams, get_list_params


router = APIRouter()
TAGS: list[str | Enum] = ['Template']

class ActionResponse(BaseModel):
    success: bool
    message: str


class TemplateCreate(BaseModel):
    name: str
    template_type: str
    path: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
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
    data: list[TemplateResponse]


class TemplateUpdate(BaseModel):
    name: str | None = None
    template_type: str | None = None
    path: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    modified_by_id: int | None = None


@router.post('/templates', response_model=TemplateResponse, tags=TAGS)
def create_template(
	current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    data: TemplateCreate,
):
    try:
        obj = Template(**data.model_dump())
        result = queryutil.create_one(db, obj)
        return result
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex

@router.get('/templates', response_model=TemplateListResponse, tags=TAGS)
def get_templates(
	current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    params: Annotated[GetListParams, Depends(get_list_params)],
):
    try:
        total, results = queryutil.get_list(db, Template, params)
        data = [TemplateResponse(**r.model_dump()) for r in results]
        return TemplateListResponse(total=total, data=data)
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex

@router.get('/templates/{id}', response_model=TemplateResponse, tags=TAGS)
def get_template(
	current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    id: int,
):
    try:
        result = queryutil.get_one(db, Template, id)
        return result
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex

@router.patch('/templates/{id}', response_model=TemplateResponse, tags=TAGS)
def update_template(
	current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    id: int,
    data: TemplateUpdate,
):
    try:
        obj = Template(id=id, **data.model_dump())
        result = queryutil.update_one(db, obj)
        return result
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex

@router.delete('/templates/{id}', response_model=ActionResponse, tags=TAGS)
def delete_template(
	current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    id: int,
):
    try:
        queryutil.delete_one(db, Template, id)
        return ActionResponse(
            success=True,
            message='Template deleted successfully'
        )
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex
