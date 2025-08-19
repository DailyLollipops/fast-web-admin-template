from enum import Enum
from typing import Annotated

import bcrypt
from database import get_db
from database.models.notification import Notification
from database.models.role_access_control import RoleAccessControl
from database.models.user import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlmodel import Session, delete, select

from .auth import get_current_user
from .utils import queryutil
from .utils.crudutils import ActionResponse, make_crud_schemas
from .utils.queryutil import GetListParams, get_list_params


router = APIRouter()
TAGS: list[str | Enum] = ['User']


CreateSchema, UpdateSchema, ResponseSchema, ListResponseSchema = make_crud_schemas(User)
UserCreate = CreateSchema
UserUpdate = UpdateSchema


class UserAuthSchema(ResponseSchema):
    permissions: list[str]


@router.post('/users', response_model=ResponseSchema, tags=TAGS)
async def create_user(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    data: UserCreate,
):
    try:
        data.password = bcrypt.hashpw(data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8') # type: ignore
        obj = User(**data.model_dump())
        result = queryutil.create_one(db, obj)
        return result
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex


@router.get('/users', response_model=ListResponseSchema, tags=TAGS)
async def get_users(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    params: Annotated[GetListParams, Depends(get_list_params)],
):
    try:
        total, results = queryutil.get_list(db, User, params)
        data = [ResponseSchema(**r.model_dump()) for r in results]
        return ListResponseSchema(total=total, data=data)
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex


@router.get('/users/{id}', response_model=ResponseSchema, tags=TAGS)
async def get_user(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    id: int,
):
    try:
        result = queryutil.get_one(db, User, id)
        return result
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex


@router.patch('/users/{id}', response_model=ResponseSchema, tags=TAGS)
async def update_user(
	current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    id: int,
    data: UserUpdate,
):
    try:
        if data.password: # type: ignore
            data.password = bcrypt.hashpw( # type: ignore
                data.password.encode('utf-8'), # type: ignore
                bcrypt.gensalt()
            ).decode('utf-8')
        result = queryutil.update_one(db, User, id, data)
        return result
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex


@router.delete('/users/{id}', tags=TAGS)
async def delete_user(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    id: str,
):
    query = delete(Notification).where(
        or_(
            Notification.user_id == current_user.id, # type: ignore
            Notification.triggered_by == current_user.id # type: ignore
        )
    )
    db.exec(query) # type: ignore
    db.delete(current_user)
    db.commit()

    return ActionResponse(
        success=True,
        message='User deleted successfully'
    )


@router.get('/me', response_model=UserAuthSchema, tags=TAGS)
async def me(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    permissions = []
    q = select(RoleAccessControl).where(User.role == current_user.role)
    if rbac := db.exec(q).first():
        permissions = rbac.permissions or []

    return UserAuthSchema(**current_user.model_dump(), permissions=permissions)
