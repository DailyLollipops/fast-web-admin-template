from typing import Annotated

import pyotp
from constants import ApplicationSettings, VerificationMethod
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from itsdangerous import URLSafeTimedSerializer
from passlib.context import CryptContext
from pydantic import BaseModel
from rq import Queue
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.database import get_async_db
from api.database.models.user import User
from api.settings import settings
from api.worker.queue import get_email_queue, get_notification_queue
from api.worker.tasks.email import send_email
from api.worker.tasks.notification import notify_role, notify_user

from ..utils.crudutils import ActionResponse, make_crud_schemas
from .core import create_access_token, get_authenticated_user, get_setting, get_template


router = APIRouter(tags=['Authentication (Native)'])
pwd_context = CryptContext(schemes=['argon2'], deprecated='auto')

CreateSchema, UpdateSchema, ResponseSchema, ListResponseSchema = make_crud_schemas(User)

class UserAuthSchema(ResponseSchema):
    permissions: list[str]
    api: str | None = None


class RegisterForm(BaseModel):
    name: str
    email: str
    password: str
    confirm_password: str


class ResetPasswordRequestForm(BaseModel):
    email: str


class ResetPasswordForm(BaseModel):
    new_password: str
    confirm_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UpdatePasswordForm(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str


async def authenticate_user(username: str, password: str, db: AsyncSession):
    query = select(User).where(User.email == username)
    result = await db.exec(query)
    user = result.first()
    if not user:
        return None
    if not pwd_context.verify(password, user.password):
        return None
    return user


@router.post('/register')
async def register_user(
    response: Response,
    data: RegisterForm,
    db: Annotated[AsyncSession, Depends(get_async_db)],
    notification_queue: Annotated[Queue, Depends(get_notification_queue)],
    email_queue: Annotated[Queue, Depends(get_email_queue)]
) -> Response:
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

    verification_method = await get_setting(db, ApplicationSettings.USER_VERIFICATION)
    hashed_password = pwd_context.hash(data.password)

    new_user = User(
        name=data.name,
        email=data.email,
        provider='native',
        password=hashed_password,
        verified=True if verification_method == VerificationMethod.NONE else False,
        tfa_secret=pyotp.random_base32(),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

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

    if verification_method == VerificationMethod.EMAIL:
        verification_token = create_access_token(data={'sub': data.email}, salt='user-verification')
        base_url = await get_setting(db, ApplicationSettings.BASE_URL)
        template_path = await get_template(db, 'email_verification')
        verification_url = f'{base_url}/api/verify_email?token={verification_token}'
        new_data = {
            'name': new_user.name,
            'verification_url': verification_url
        }

        email_queue.enqueue(
            send_email,
            template=template_path,
            data=new_data,
            subject='Verify your email address',
            recipients=[new_user.email]
        )

    access_token = create_access_token(data={'sub': data.email}, salt='user-auth')
    refresh_token = create_access_token(data={'sub': data.email}, salt='user-refresh')

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
        path="/api/refresh",
    )
    return response


@router.post('/login')
async def login_user(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_async_db)],
    remember: bool = False,
    tfa_verified: Annotated[str | None, Cookie()] = None,
):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail='User not found')
    if not user.verified:
        raise HTTPException(status_code=401, detail='User not verified. Please contact admin for more details!')

    if user.tfa_methods and not tfa_verified:
        tfa_token = create_access_token(data={'sub': user.email}, salt='user-tfa')
        response.set_cookie(
            key='tfa_token',
            value=tfa_token,
            httponly=True,
            secure=True,
            samesite='lax',
            max_age=settings.TFA_TOKEN_EX,
        )
        return {
            'tfa_required': True,
            'tfa_methods': user.tfa_methods
        }
        
    if tfa_verified and tfa_verified != '1':
        raise HTTPException(status_code=401, detail='Invalid TFA verification status')

    access_token = create_access_token(data={'sub': user.email}, salt='user-auth')
    refresh_token = create_access_token(data={'sub': user.email}, salt='user-refresh')

    response.delete_cookie(key='tfa_token')
    response.delete_cookie(key='tfa_verified')
    response.status_code = status.HTTP_200_OK
    response.set_cookie(
        key='access_token',
        value=access_token,
        httponly=True,
        secure=True,
        samesite='lax',
        max_age=settings.ACCESS_TOKEN_EX,
    )

    if remember:
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite='lax',
            max_age=settings.REFRESH_TOKEN_EX,
            path="/api/refresh",
        )

    data = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer',
    }
    return data


@router.post('/forgot_password', response_model=ActionResponse)
async def forgot_password(
    data: ResetPasswordRequestForm,
    db: Annotated[AsyncSession, Depends(get_async_db)],
    email_queue: Annotated[Queue, Depends(get_email_queue)]
):
    response = ActionResponse(
        success=True,
        message='Password reset link has been sent to your email',
    )
    result = await db.exec(select(User).where(User.email == data.email))
    user = result.first()
    if not user:
        return response
    
    reset_token = create_access_token(data={'sub': data.email}, salt='forgot-password')
    base_url = await get_setting(db, ApplicationSettings.BASE_URL)
    template_path = await get_template(db, 'reset_password')
    reset_url = f'{base_url}/reset-password?token={reset_token}'
    new_data = {
        'name': user.name,
        'reset_password_url': reset_url
    }

    email_queue.enqueue(
        send_email,
        template=template_path,
        data=new_data,
        subject='Reset your password',
        recipients=[user.email]
    )

    return response


@router.post('/reset_password', response_model=ActionResponse)
async def reset_password(
    token: str,
    data: ResetPasswordForm,
    db: Annotated[AsyncSession, Depends(get_async_db)],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail='New passwords do not match')

    try:
        serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
        payload = serializer.loads(token, max_age=settings.EMAIL_TOKEN_EX, salt='forgot-password')
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
    except Exception as ex:
        raise credentials_exception from ex
    
    result = await db.exec(select(User).where(User.email == username))
    user = result.first()
    if user is None:
        raise credentials_exception
    
    hashed_password = hashed_password = pwd_context.hash(data.new_password)
    user.password = hashed_password
    db.add(user)
    await db.commit()
    return ActionResponse(success=True, message='Password successfully changed')


@router.get('/verify_email', response_model=ActionResponse)
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
        payload = serializer.loads(token, max_age=settings.EMAIL_TOKEN_EX, salt='user-verification')
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


@router.post('/update_password', response_model=ActionResponse)
async def update_password(
    current_user: Annotated[User, get_authenticated_user('auth.update_password')],
    db: Annotated[AsyncSession, Depends(get_async_db)],
    data: UpdatePasswordForm,
):
    user = await authenticate_user(current_user.email, data.current_password, db)

    if not user:
        raise HTTPException(status_code=401, detail='Current password is incorrect')
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail='New passwords do not match')
    hashed_password = hashed_password = pwd_context.hash(data.new_password)

    user.password = hashed_password
    db.add(user)
    await db.commit()
    return ActionResponse(success=True, message='Password successfully changed')
