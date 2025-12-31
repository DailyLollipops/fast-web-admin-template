import secrets
from enum import Enum
from typing import Annotated

from database import get_async_db
from database.models.role_access_control import RoleAccessControl
from database.models.user import User
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from itsdangerous import URLSafeTimedSerializer
from settings import settings
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..utils.crudutils import make_crud_schemas
from .core import create_access_token, get_authenticated_user
from .native import router as native_router


TAGS: list[str | Enum] = ['Authentication (Common)']

router = APIRouter()
router.include_router(native_router, prefix='/auth')

CreateSchema, UpdateSchema, ResponseSchema, ListResponseSchema = make_crud_schemas(User)

class UserAuthSchema(ResponseSchema):
    permissions: list[str]
    api: str | None = None


@router.post('/auth/refresh', tags=TAGS)
async def refresh_token(
    response: Response,
    db: Annotated[AsyncSession, Depends(get_async_db)],
    refresh_token: Annotated[str | None, Cookie()] = None,
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail='No refresh token provided')

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Invalid refresh token',
    )

    try:
        serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
        payload = serializer.loads(refresh_token, max_age=settings.ACCESS_TOKEN_EX, salt='user-refresh')
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
    except Exception as ex:
        raise credentials_exception from ex

    result = await db.exec(select(User).where(User.email == username))
    user = result.first()
    if user is None:
        raise credentials_exception

    access_token = create_access_token(data={'sub': user.email}, salt='user-auth')
    refresh_token = create_access_token(data={'sub': user.email}, salt='user-refresh')

    response.status_code = status.HTTP_200_OK
    response.set_cookie(
        key='access_token',
        value=access_token,
        httponly=True,
        secure=True,
        samesite='lax',
        max_age=settings.ACCESS_TOKEN_EX,
    )
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite='lax',
        max_age=settings.REFRESH_TOKEN_EX,
        path="/api/auth/refresh",
    )
    return response


@router.post('/auth/logout', tags=TAGS)
async def logout_user(response: Response,):
    response.status_code = status.HTTP_200_OK
    response.delete_cookie(key='access_token')
    return response


@router.get('/auth/me', response_model=UserAuthSchema, tags=TAGS)
async def me(
    current_user: Annotated[User, get_authenticated_user('auth', 'me')],
    db: Annotated[AsyncSession, Depends(get_async_db)],
):
    permissions = []
    q = select(RoleAccessControl).where(RoleAccessControl.role == current_user.role)
    if rbac := (await db.exec(q)).first():
        permissions = rbac.permissions or []

    return UserAuthSchema(**current_user.model_dump(), permissions=permissions)


@router.post('/auth/generate_api_key', tags=TAGS)
async def generate_api_key(
    current_user: Annotated[User, get_authenticated_user('auth', 'generate_api_key')],
    db: Annotated[AsyncSession, Depends(get_async_db)],
):
    api_key = secrets.token_urlsafe(32)
    current_user.api = api_key
    current_user.verified = True
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user
