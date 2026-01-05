from typing import Annotated

from fastapi import Cookie, Depends, Header, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from itsdangerous import URLSafeTimedSerializer
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.database import get_async_db
from api.database.models.application_setting import ApplicationSetting
from api.database.models.role_access_control import RoleAccessControl
from api.database.models.template import Template
from api. database.models.user import User
from api.settings import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/login', auto_error=False)
ACCESS_TOKEN_EXPIRATION = 3600


async def can_access(
    db: AsyncSession,
    required_permission: str | None = None,
    role: str | None = None,
) -> bool:
    if required_permission is None or role is None:
        return True

    auth_resources = ['auth.*']
    q = select(RoleAccessControl).where(RoleAccessControl.role == role)
    q_result = await db.exec(q)
    result = q_result.first()
    
    if not result:
        return False
    
    resource = required_permission.rsplit('.', maxsplit=1)[0]
    permissions = result.permissions + auth_resources

    # Permission format: <resource>.<action>
    if '*' in permissions:
        return True

    if f'{resource}.*' in permissions:
        return True

    return required_permission in permissions


async def get_current_user(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_async_db)],
    api_key: Annotated[str | None, Header()] = None,
    access_token: Annotated[str | None, Cookie()] = None,
):
    user = None
    if api_key:
        try:
            user =  await get_user_by_api_key(db, api_key)
        except HTTPException as e:
            print(f'API Key authentication failed: {str(e)}')
            pass

    if access_token:
        try:
            user = await get_user_by_jwt_token(db, access_token)
        except HTTPException as e:
            print(f'Token authentication failed: {str(e)}')
            pass

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication required'
        )
    
    if not user.verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User not verified'
        )

    return user


async def get_user_by_api_key(
    db: AsyncSession,
    api_key: Annotated[str | None, Header()] = None
):
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='API key missing'
        )
    result = await db.exec(select(User).where(User.api == api_key))
    user = result.first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid API key'
        )
    return user


async def get_user_by_jwt_token(db: AsyncSession, token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
        payload = serializer.loads(token, max_age=settings.ACCESS_TOKEN_EX, salt='user-auth')
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
    except Exception as ex:
        raise credentials_exception from ex
    result = await db.exec(select(User).where(User.email == username))
    user = result.first()
    if user is None:
        raise credentials_exception
    return user


def get_authenticated_user(required_permission: str):
    async def dependency(
        db: Annotated[AsyncSession, Depends(get_async_db)],
        current_user: Annotated[User, Depends(get_current_user)],
        scheme: Annotated[str | None, Depends(oauth2_scheme)] = None,
    ) -> User:
        if not await can_access(db, required_permission, current_user.role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No access to {required_permission}",
            )
        return current_user

    return Depends(dependency)


def create_access_token(data: dict, salt: str | bytes | None = None):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    token = serializer.dumps(data, salt)
    return token


async def get_setting(db: AsyncSession, name: str):
    result = await db.exec(
        select(ApplicationSetting)
        .where(ApplicationSetting.name == name)
    )
    setting = result.first()
    if not setting:
        raise Exception('User verification setting not found. Perhaps you forgot to run migration?')
    return setting.value


async def get_template(db: AsyncSession, name: str):
    result = await db.exec(
        select(Template)
        .where(Template.name == name)
    )
    template = result.first()
    if not template:
        raise Exception('Email template path setting not found. Perhaps you forgot to run migration?')
    return template.path
