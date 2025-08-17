from enum import Enum
from typing import Annotated

from database import get_db
from database.models.template import Template
from database.models.user import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from .auth import get_current_user
from .utils import queryutil
from .utils.crudutils import ActionResponse, make_crud_schemas
from .utils.queryutil import GetListParams, get_list_params


router = APIRouter()
TAGS: list[str | Enum] = ['Template']


CreateSchema, UpdateSchema, ResponseSchema, ListResponseSchema = make_crud_schemas(Template)
TemplateCreate = CreateSchema
TemplateUpdate = UpdateSchema


@router.post('/templates', response_model=ResponseSchema, tags=TAGS)
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

@router.get('/templates', response_model=ListResponseSchema, tags=TAGS)
def get_templates(
	current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    params: Annotated[GetListParams, Depends(get_list_params)],
):
    try:
        total, results = queryutil.get_list(db, Template, params)
        data = [ResponseSchema(**r.model_dump()) for r in results]
        return ListResponseSchema(total=total, data=data)
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex

@router.get('/templates/{id}', response_model=ResponseSchema, tags=TAGS)
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

@router.patch('/templates/{id}', response_model=ResponseSchema, tags=TAGS)
def update_template(
	current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    id: int,
    data: TemplateUpdate,
):
    try:
        result = queryutil.update_one(db, Template, id, data)
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
