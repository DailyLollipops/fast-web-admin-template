from enum import Enum
from typing import Annotated

import bcrypt
from database import get_db
from database.models.notification import Notification
from database.models.user import User
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import or_
from sqlmodel import Session, delete

from .auth import get_current_user
from .utils import queryutil
from .utils.queryutil import GetListParams, get_list_params


router = APIRouter()
TAGS: list[str | Enum] = ['User']

class UserRole(str, Enum):
    admin = 'admin'
    user = 'user'


class ActionResponse(BaseModel):
    success: bool
    message: str


class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    role: str | None = 'user'
    verified: bool | None = False


class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    name: str


class UserListResponse(BaseModel):
    total: int
    data: list[UserResponse]


class UserUpdate(BaseModel):
    email: str | None = None
    password: str | None = None
    name: str | None = None
    role: str | None = 'user'
    verified: bool | None = False


@router.post('/users', response_model=UserResponse, tags=TAGS)
async def create_user(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    data: UserCreate,
):
    try:
        data.password = bcrypt.hashpw(data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
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


@router.get('/users', response_model=UserListResponse, tags=TAGS)
async def get_users(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    params: Annotated[GetListParams, Depends(get_list_params)],
):
    try:
        total, results = queryutil.get_list(db, User, params)
        data = [UserResponse(**r.model_dump()) for r in results]
        return UserListResponse(total=total, data=data)
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex


@router.get('/users/{id}', response_model=UserResponse, tags=TAGS)
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


@router.patch('/users/{id}', response_model=UserResponse, tags=TAGS)
def update_user(
	current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    id: int,
    data: UserUpdate,
):
    try:
        if data.password:
            data.password = bcrypt.hashpw(
                data.password.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')
        obj = User(id=id, **data.model_dump())
        result = queryutil.update_one(db, obj)
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


@router.get('/me', response_model=UserResponse, tags=TAGS)
async def me(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return current_user
