# Generated code for RoleAccessControl model

from datetime import datetime
from enum import Enum
from typing import Annotated

from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models.role_access_control import RoleAccessControl
from models.user import User
from pydantic import BaseModel
from sqlmodel import Session

from .auth import get_current_user
from .utils import queryutil
from .utils.queryutil import GetListParams, get_list_params


router = APIRouter()
TAGS: list[str | Enum] = ['RoleAccessControl']

class ActionResponse(BaseModel):
    success: bool
    message: str


class RoleAccessControlCreate(BaseModel):
    role: str
    permissions: list[str] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    


class RoleAccessControlResponse(BaseModel):
    id: int | None = None
    modified_by_id: int
    role: str
    permissions: list[str] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    


class RoleAccessControlUpdate(BaseModel):
    role: str | None = None
    permissions: list[str] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    


class RoleAccessControlListResponse(BaseModel):
    total: int
    data: list[RoleAccessControlResponse]


@router.post('/role_access_controls', response_model=RoleAccessControlResponse, tags=TAGS)
async def create_roleaccesscontrol(
    data: RoleAccessControlCreate,
	current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    try:
        obj = RoleAccessControl(**data.model_dump(), modified_by_id=current_user.id)
        result = queryutil.create_one(db, obj)
        return result
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex


@router.get('/role_access_controls', response_model=RoleAccessControlListResponse, tags=['RoleAccessControl'])
async def get_roleaccesscontrols(
	current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    params: Annotated[GetListParams, Depends(get_list_params)],
):
    try:
        total, results = queryutil.get_list(db, RoleAccessControl, params)
        data = [RoleAccessControlResponse(**r.model_dump()) for r in results]
        return RoleAccessControlListResponse(total=total, data=data)
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex


@router.get('/role_access_controls/{id}', response_model=RoleAccessControlResponse, tags=['RoleAccessControl'])
async def get_roleaccesscontrol(
	current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    id: int,
):
    try:
        result = queryutil.get_one(db, RoleAccessControl, id)
        return result
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex


@router.patch('/role_access_controls/{id}', response_model=RoleAccessControlResponse, tags=['RoleAccessControl'])
async def update_roleaccesscontrol(
	current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    id: int,
    data: RoleAccessControlUpdate,
):
    try:
        obj = RoleAccessControl(id=id, **data.model_dump(), modified_by_id=current_user.id)
        result = queryutil.update_one(db, obj)
        return result
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex


@router.delete('/role_access_controls/{id}', response_model=ActionResponse, tags=['RoleAccessControl'])
async def delete_roleaccesscontrol(
	current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    id: int,
):
    try:
        queryutil.delete_one(db, RoleAccessControl, id)
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
