# Generated code for RoleAccessControl model

from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from api.database import get_async_db
from api.database.models.role_access_control import RoleAccessControl
from api.database.models.user import User
from api.routes.auth import get_authenticated_user
from api.routes.utils import queryutil
from api.routes.utils.crudutils import ActionResponse, make_crud_schemas
from api.routes.utils.queryutil import GetListParams, get_list_params


router = APIRouter()
TAGS: list[str | Enum] = ['RoleAccessControl']


CreateSchema, UpdateSchema, ResponseSchema, ListResponseSchema = make_crud_schemas(RoleAccessControl)
RoleAccessControlCreate = CreateSchema
RoleAccessControlUpdate = UpdateSchema


@router.post('/role_access_controls', response_model=ResponseSchema, tags=TAGS)
async def create_role_access_control(
    data: RoleAccessControlCreate,
	current_user: Annotated[User, get_authenticated_user('role_access_controls.create')],
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
async def get_role_access_controls(
	current_user: Annotated[User, get_authenticated_user('role_access_controls.read')],
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
async def get_role_access_control(
	current_user: Annotated[User, get_authenticated_user('role_access_controls.read')],
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
async def update_role_access_control(
	current_user: Annotated[User, get_authenticated_user('role_access_controls.update')],
    db: Annotated[AsyncSession, Depends(get_async_db)],
    id: int,
    data: RoleAccessControlUpdate,
):
    try:
        class UpdatedData(RoleAccessControlUpdate):
            modified_by_id: int

        updated_data = UpdatedData(**data.model_dump(), modified_by_id=current_user.id)
        result = await queryutil.update_one(db, RoleAccessControl, id, updated_data)
        return result
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        print(ex)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex


@router.delete('/role_access_controls/{id}', response_model=ActionResponse, tags=['RoleAccessControl'])
async def delete_role_access_control(
	current_user: Annotated[User, get_authenticated_user('role_access_controls.delete')],
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
