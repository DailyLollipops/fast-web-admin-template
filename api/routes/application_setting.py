from enum import Enum
from typing import Annotated

from database import get_db
from database.models.application_setting import ApplicationSetting
from database.models.user import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from .auth import get_current_user
from .utils import queryutil
from .utils.crudutils import ActionResponse, make_crud_schemas
from .utils.queryutil import GetListParams, get_list_params


router = APIRouter()
TAGS: list[str | Enum] = ['Application Setting']


CreateSchema, UpdateSchema, ResponseSchema, ListResponseSchema = make_crud_schemas(ApplicationSetting)
ApplicationSettingCreate = CreateSchema
ApplicationSettingUpdate = UpdateSchema


@router.post('/application_settings', response_model=ResponseSchema, tags=TAGS)
def create_application_setting(
	current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    data: ApplicationSettingCreate,
):
    try:
        fields = data.model_dump()
        fields.pop('modified_by_id')
        obj = ApplicationSetting(
            **fields,
            modified_by_id=current_user.id
        )
        result = queryutil.create_one(db, obj)
        return result
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex


@router.get('/application_settings', response_model=ListResponseSchema, tags=TAGS)
def get_application_settings(
	current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    params: Annotated[GetListParams, Depends(get_list_params)],
):
    try:
        total, results = queryutil.get_list(db, ApplicationSetting, params)
        data = [ResponseSchema(**r.model_dump()) for r in results]
        return ListResponseSchema(total=total, data=data)
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex


@router.get('/application_settings/{id}', response_model=ResponseSchema, tags=TAGS)
def get_application_setting(
	current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    id: int,
):
    try:
        result = queryutil.get_one(db, ApplicationSetting, id)
        return result
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex


@router.patch('/application_settings/{id}', response_model=ResponseSchema, tags=TAGS)
def update_application_setting(
	current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    id: int,
    data: ApplicationSettingUpdate,
):
    try:
        result = queryutil.update_one(db, ApplicationSetting, id, data)
        return result
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex


@router.delete('/application_settings/{id}', response_model=ActionResponse, tags=TAGS)
def delete_application_setting(
	current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    id: int,
):
    try:
        queryutil.delete_one(db, ApplicationSetting, id)
        return ActionResponse(
            success=True,
            message='Application Setting deleted successfully'
        )
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex
