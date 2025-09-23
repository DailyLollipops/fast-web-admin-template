import secrets
from enum import Enum
from typing import Annotated

import bcrypt
from constants import ApplicationSettings, VerificationMethod
from database import get_async_db
from database.models.application_setting import ApplicationSetting
from database.models.role_access_control import RoleAccessControl
from database.models.template import Template
from database.models.user import User
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from itsdangerous import URLSafeTimedSerializer
from passlib.context import CryptContext
from pydantic import BaseModel
from rq import Queue
from settings import settings
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from worker.queue import get_email_queue, get_notification_queue
from worker.tasks.email import send_email
from worker.tasks.notification import notify_role, notify_user

from .utils.crudutils import ActionResponse, make_crud_schemas


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/login', auto_error=False)
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
ACCESS_TOKEN_EXPIRATION = 3600
TAGS: list[str | Enum] = ['Authentication']

CreateSchema, UpdateSchema, ResponseSchema, ListResponseSchema = make_crud_schemas(User)

class UserAuthSchema(ResponseSchema):
    permissions: list[str]
    api: str | None = None


class RegisterForm(BaseModel):
    name: str
    email: str
    password: str
    confirm_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str


async def can_access(db: AsyncSession, resource: str, action: str, role: str):
    auth_resources = ['auth.*']
    q = select(RoleAccessControl).where(RoleAccessControl.role == role)
    q_result = await db.exec(q)
    result = q_result.first()
    
    if not result:
        return False
    
    permissions = result.permissions + auth_resources
    # Permission format: <resource>.<action>
    for permission in permissions:
        if permission == '*':
            return True

        p_resource = permission.split('.')[0]
        p_action = permission.split('.')[1]

        if p_resource in [resource, '*'] and p_action in [action, '*']:
            return True
    
    return False


async def get_current_user(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_async_db)],
    api_key: Annotated[str | None, Header()] = None,
    token: Annotated[str | None, Depends(oauth2_scheme)] = None,
):
    user = None
    if api_key:
        try:
            user =  await get_user_by_api_key(db, api_key)
        except HTTPException as e:
            print(f'API Key authentication failed: {str(e)}')
            pass

    if token:
        try:
            user = await get_user_by_jwt_token(db, token)
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
    
    action_map = {
        'POST': 'create',
        'GET': 'read',
        'PATCH': 'update',
        'PUT': 'update',
        'DELETE': 'delete',
    }

    resource = request.url.path.split('/')[2]
    action = action_map.get(request.method, '')
    if not await can_access(db, resource, action, user.role):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='No access to resource'
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


async def get_user_by_jwt_token(
    db: AsyncSession,
    token: Annotated[str, Depends(oauth2_scheme)] = ''
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
        payload = serializer.loads(token, max_age=ACCESS_TOKEN_EXPIRATION, salt='user-auth')
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


async def authenticate_user(username: str, password: str, db: AsyncSession):
    query = select(User).where(User.email == username)
    result = await db.exec(query)
    user = result.first()
    if not user:
        return None
    if not pwd_context.verify(password, user.password):
        return None
    return user


def create_access_token(data: dict, salt: str | bytes | None = None):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    token = serializer.dumps(data, salt)
    return token


async def get_setting(db: AsyncSession, name: str):
    result = await db.exec(
        select(ApplicationSetting)
        .where(ApplicationSetting.name == name)
    )
    return result.first()


@router.post('/auth/register', tags=TAGS)
async def register_user(
    data: RegisterForm,
    db: Annotated[AsyncSession, Depends(get_async_db)],
    notification_queue: Annotated[Queue, Depends(get_notification_queue)],
    email_queue: Annotated[Queue, Depends(get_email_queue)]
) -> Token:
    if data.password != data.confirm_password:
        raise HTTPException(
            status_code=400,
            detail='Passwords do not match'
        )

    result = await db.exec(select(User).where(User.email == data.email))
    existing_user = result.first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail='Email/Username already registered'
        )

    verification_setting = await get_setting(db, ApplicationSettings.USER_VERIFICATION)

    if not verification_setting:
        raise Exception('User verification setting not found. Perhaps you forgot to run migration?')

    verification_value = verification_setting.value
    hashed_password = bcrypt.hashpw(data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    new_user = User(
        name=data.name,
        email=data.email,
        password=hashed_password,
        verified=True if verification_setting.value == VerificationMethod.NONE else False
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    access_token = create_access_token(data={'sub': data.email}, salt='user-auth')
    notification_queue.enqueue(
        notify_role,
        triggered_by=new_user.id,
        category='registration',
        roles=['admin'],
        title='New user has been created',
        body=f'A new user has been created by an admin with email: {new_user.email}'
    )

    notification_queue.enqueue(
        notify_user,
        triggered_by=2,
        category='registration',
        user_id=new_user.id,
        title='Welcome to the app',
        body=f'Hello {new_user.name}, welcome to the app!'
    )

    if verification_value == VerificationMethod.EMAIL:
        verification_token = create_access_token(data={'sub': data.email}, salt='user-verification')

        base_url_setting = await get_setting(db, ApplicationSettings.BASE_URL)
        if not base_url_setting:
            raise Exception('Email base url setting not found. Perhaps you forgot to run migration?')
        
        template_result = await db.exec(
            select(Template)
            .where(ApplicationSetting.name == 'email_verification')
        )
        email_template_setting = template_result.first()
        if not email_template_setting:
            raise Exception('Email template path setting not found. Perhaps you forgot to run migration?')
        
        base_url = base_url_setting.value
        email_verification_template_path = email_template_setting.path
        verification_url = f'{base_url}/api/auth/verify_email?token={verification_token}'
        new_data = {
            'name': new_user.name,
            'verification_url': verification_url
        }

        email_queue.enqueue(
            send_email,
            template=email_verification_template_path,
            data=new_data,
            subject='Verify your email address',
            recipients=[new_user.email]
        )

    return Token(access_token=access_token, token_type='bearer')


@router.post('/auth/login', tags=TAGS)
async def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> Token:
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail='User not found')
    if not user.verified:
        raise HTTPException(status_code=401, detail='User not verified. Please contact admin for more details!')

    access_token = create_access_token(data={'sub': user.email}, salt='user-auth')
    return Token(access_token=access_token, token_type='bearer')


@router.get('/auth/verify_email', response_model=ActionResponse, tags=TAGS)
async def verify_email(
    token: str,
    db: Annotated[AsyncSession, Depends(get_async_db)],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
        payload = serializer.loads(token, max_age=ACCESS_TOKEN_EXPIRATION, salt='user-verification')
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
    except Exception as ex:
        raise credentials_exception from ex
    
    result = await db.exec(select(User).where(User.email == username))
    user = result.first()
    if user is None:
        raise credentials_exception
    
    user.verified = True
    db.add(user)
    await db.commit()
    return ActionResponse(success=True, message='Email successfully verified')


@router.post('/auth/reset_password', response_model=ActionResponse, tags=TAGS)
async def reset_password(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_async_db)],
    data: PasswordChangeRequest,
):
    user = await authenticate_user(current_user.email, data.current_password, db)

    if not user:
        raise HTTPException(status_code=401, detail='Current password is incorrect')
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail='New passwords do not match')
    hashed_password = bcrypt.hashpw(data.new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user.password = hashed_password
    db.add(user)
    await db.commit()
    return ActionResponse(success=True, message='Password successfully changed')

@router.get('/auth/me', response_model=UserAuthSchema, tags=TAGS)
async def me(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_async_db)],
):
    permissions = []
    q = select(RoleAccessControl).where(RoleAccessControl.role == current_user.role)
    if rbac := (await db.exec(q)).first():
        permissions = rbac.permissions or []

    return UserAuthSchema(**current_user.model_dump(), permissions=permissions)


@router.post('/auth/generate_api_key', tags=TAGS)
async def generate_api_key(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_async_db)],
):
    api_key = secrets.token_urlsafe(32)
    current_user.api = api_key
    current_user.verified = True
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user
