# Generated code for RoleAccessControl model

from enum import Enum
from typing import Annotated

from database import get_async_db
from database.models.role_access_control import RoleAccessControl
from database.models.user import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from .auth import get_current_user
from .utils import queryutil
from .utils.crudutils import ActionResponse, make_crud_schemas
from .utils.queryutil import GetListParams, get_list_params


router = APIRouter()
TAGS: list[str | Enum] = ['RoleAccessControl']


CreateSchema, UpdateSchema, ResponseSchema, ListResponseSchema = make_crud_schemas(RoleAccessControl)
RoleAccessControlCreate = CreateSchema
RoleAccessControlUpdate = UpdateSchema


@router.post('/role_access_controls', response_model=ResponseSchema, tags=TAGS)
async def create_roleaccesscontrol(
    data: RoleAccessControlCreate,
	current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_async_db)],
):
    try:
        obj = RoleAccessControl(**data.model_dump(), modified_by_id=current_user.id)
        result = await queryutil.create_one(db, obj)
        return result
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex


@router.get('/role_access_controls', response_model=ListResponseSchema, tags=['RoleAccessControl'])
async def get_roleaccesscontrols(
	current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_async_db)],
    params: Annotated[GetListParams, Depends(get_list_params)],
):
    try:
        total, results = await queryutil.get_list(db, RoleAccessControl, params)
        data = [ResponseSchema(**r.model_dump()) for r in results]
        return ListResponseSchema(total=total, data=data)
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex


@router.get('/role_access_controls/{id}', response_model=ResponseSchema, tags=['RoleAccessControl'])
async def get_roleaccesscontrol(
	current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_async_db)],
    id: int,
):
    try:
        result = await queryutil.get_one(db, RoleAccessControl, id)
        return result
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex


@router.patch('/role_access_controls/{id}', response_model=ResponseSchema, tags=['RoleAccessControl'])
async def update_roleaccesscontrol(
	current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_async_db)],
    id: int,
    data: RoleAccessControlUpdate,
):
    try:
        data.modified_by_id = current_user.id # type: ignore
        result = await queryutil.update_one(db, RoleAccessControl, id, data)
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
    db: Annotated[AsyncSession, Depends(get_async_db)],
    id: int,
):
    try:
        await queryutil.delete_one(db, RoleAccessControl, id)
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
