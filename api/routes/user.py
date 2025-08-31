import uuid
from enum import Enum
from pathlib import Path
from typing import Annotated

import bcrypt
from database import get_async_db
from database.models.notification import Notification
from database.models.user import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlmodel import delete
from sqlmodel.ext.asyncio.session import AsyncSession

from .auth import get_current_user
from .utils import queryutil
from .utils.crudutils import ActionResponse, make_crud_schemas
from .utils.fileutil import save_base64_image
from .utils.queryutil import GetListParams, get_list_params


router = APIRouter()
TAGS: list[str | Enum] = ['User']
PROFILE_DIR = Path(__file__).resolve().parent.parent / "static" / "profiles"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)


CreateSchema, UpdateSchema, ResponseSchema, ListResponseSchema = make_crud_schemas(User)
UserCreate = CreateSchema
UserUpdate = UpdateSchema


@router.post('/users', response_model=ResponseSchema, tags=TAGS)
async def create_user(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_async_db)],
    data: UserCreate,
):
    try:
        data.password = bcrypt.hashpw(data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8') # type: ignore

        if data.profile: # type: ignore
            uuid_str = str(uuid.uuid4())
            file_path = PROFILE_DIR / uuid_str
            if saved_path := save_base64_image(data.profile, str(file_path)): # type: ignore
                data.profile = f'/static/profiles/{Path(saved_path).name}' # type: ignore

        obj = User(**data.model_dump())
        result = await queryutil.create_one(db, obj)
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
    db: Annotated[AsyncSession, Depends(get_async_db)],
    params: Annotated[GetListParams, Depends(get_list_params)],
):
    try:
        total, results = await queryutil.get_list(db, User, params)
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
    db: Annotated[AsyncSession, Depends(get_async_db)],
    id: int,
):
    try:
        result = await queryutil.get_one(db, User, id)
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
    db: Annotated[AsyncSession, Depends(get_async_db)],
    id: int,
    data: UserUpdate,
):
    try:
        if data.password: # type: ignore
            data.password = bcrypt.hashpw( # type: ignore
                data.password.encode('utf-8'), # type: ignore
                bcrypt.gensalt()
            ).decode('utf-8')

        if data.profile: # type: ignore
            uuid_str = str(uuid.uuid4())
            file_path = PROFILE_DIR / uuid_str
            if saved_path := save_base64_image(data.profile, str(file_path)): # type: ignore
                data.profile = f'/static/profiles/{Path(saved_path).name}' # type: ignore

        result = await queryutil.update_one(db, User, id, data)
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
    db: Annotated[AsyncSession, Depends(get_async_db)],
    id: str,
):
    query = delete(Notification).where(
        or_(
            Notification.user_id == current_user.id, # type: ignore
            Notification.triggered_by == current_user.id # type: ignore
        )
    )
    await db.exec(query) # type: ignore
    await db.delete(current_user)
    await db.commit()

    return ActionResponse(
        success=True,
        message='User deleted successfully'
    )
