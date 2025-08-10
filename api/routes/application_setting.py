from datetime import datetime
from enum import Enum
from typing import Annotated

from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models.application_setting import ApplicationSetting
from models.user import User
from pydantic import BaseModel
from sqlmodel import Session

from .auth import get_current_user
from .utils import queryutil
from .utils.queryutil import GetListParams, get_list_params


router = APIRouter()
TAGS: list[str | Enum] = ['Application Setting']

class ActionResponse(BaseModel):
    success: bool
    message: str


class ApplicationSettingCreate(BaseModel):
    name: str
    value: str = ''
    

class ApplicationSettingResponse(BaseModel):
    id: int
    name: str
    value: str
    created_at: datetime
    updated_at: datetime
    modified_by_id: int


class ApplicationSettingListResponse(BaseModel):
    total: int
    data: list[ApplicationSettingResponse]


class ApplicationSettingUpdate(BaseModel):
    name: str | None = None
    value: str | None = ''


@router.post('/application_settings', response_model=ApplicationSettingResponse, tags=TAGS)
def create_application_setting(
	current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    data: ApplicationSettingCreate,
):
    try:
        obj = ApplicationSetting(
            **data.model_dump(),
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


@router.get('/application_settings', response_model=ApplicationSettingListResponse, tags=TAGS)
def get_application_settings(
	current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    params: Annotated[GetListParams, Depends(get_list_params)],
):
    try:
        total, results = queryutil.get_list(db, ApplicationSetting, params)
        data = [ApplicationSettingResponse(**r.model_dump()) for r in results]
        return ApplicationSettingListResponse(total=total, data=data)
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex


@router.get('/application_settings/{id}', response_model=ApplicationSettingResponse, tags=TAGS)
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


@router.patch('/application_settings/{id}', response_model=ApplicationSettingResponse, tags=TAGS)
def update_application_setting(
	current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    id: int,
    data: ApplicationSettingUpdate,
):
    try:
        obj = ApplicationSetting(id=id, **data.model_dump())
        result = queryutil.update_one(db, obj)
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
