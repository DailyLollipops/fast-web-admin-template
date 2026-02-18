from enum import StrEnum
from typing import Annotated

import pyotp
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from itsdangerous import URLSafeTimedSerializer
from pydantic import BaseModel
from rq import Queue
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from worker.queue import get_email_queue

from api.database import get_async_db
from api.database.models.user import User
from api.routes.auth.core import create_access_token, get_authenticated_user, get_template
from api.settings import settings
from api.worker.tasks.email import send_email


router = APIRouter(tags=['Two-Factor Authentication'])

class TfaMethod(StrEnum):
    AUTHENTICATOR = 'authenticator'
    EMAIL = 'email'

class AuthenticatorSetupResponse(BaseModel):
    tfa_link: str

class EmailSetupResponse(BaseModel):
    message: str
    success: bool

class TfaVerificationResponse(BaseModel):
    verified: bool
    message: str


@router.post('/setup/authenticator', response_model=AuthenticatorSetupResponse)
async def setup_authenticator_tfa_method(
    response: Response,
    current_user: Annotated[User, get_authenticated_user('tfa.setup')],
    db: Annotated[AsyncSession, Depends(get_async_db)],
):
    if not current_user.tfa_secret:
        current_user.tfa_secret = pyotp.random_base32()
        db.add(current_user)
        await db.commit()

    totp = pyotp.TOTP(current_user.tfa_secret)
    totp.now()

    tfa_link = totp.provisioning_uri(name=current_user.email, issuer_name=settings.APP_NAME)

    tfa_token = create_access_token(data={'sub': current_user.email}, salt='user-tfa')
    response.set_cookie(
        key='tfa_token',
        value=tfa_token,
        httponly=True,
        secure=True,
        samesite='lax',
        max_age=settings.TFA_TOKEN_EX,
    )
    
    return AuthenticatorSetupResponse(tfa_link=tfa_link)


@router.post('/setup/email', response_model=EmailSetupResponse)
async def setup_email_tfa_method(
    response: Response,
    current_user: Annotated[User, get_authenticated_user('tfa.setup')],
    db: Annotated[AsyncSession, Depends(get_async_db)],
    email_queue: Annotated[Queue, Depends(get_email_queue)],
):
    if not current_user.tfa_secret:
        current_user.tfa_secret = pyotp.random_base32()
        db.add(current_user)
        await db.commit()

    totp = pyotp.TOTP(current_user.tfa_secret, interval=300)
    totp.now()
    
    template_path = await get_template(db, 'tfa')
    email_queue.enqueue(
        send_email,
        template=template_path,
        data={
            'otp': totp.now(),
            'expiry_minutes': settings.TFA_TOKEN_EX // 60,
        },
        subject='Your Two-Factor Authentication Code',
        recipients=[current_user.email]
    )

    tfa_token = create_access_token(data={'sub': current_user.email}, salt='user-tfa')
    response.set_cookie(
        key='tfa_token',
        value=tfa_token,
        httponly=True,
        secure=True,
        samesite='lax',
        max_age=settings.TFA_TOKEN_EX,
    )

    return EmailSetupResponse(message='Verification code sent to your email', success=True)


@router.post('/send_email', response_model=EmailSetupResponse)
async def send_email_tfa_code(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    email_queue: Annotated[Queue, Depends(get_email_queue)],
    tfa_token: Annotated[str | None, Cookie()] = None,
):
    if not tfa_token:
        raise HTTPException(status_code=401, detail='No TFA token provided')

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Invalid TFA token',
    )

    try:
        serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
        payload = serializer.loads(tfa_token, max_age=settings.ACCESS_TOKEN_EX, salt='user-tfa')
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
    except Exception as ex:
        raise credentials_exception from ex

    result = await db.exec(select(User).where(User.email == username))
    user = result.first()
    if user is None:
        raise credentials_exception

    if not user.tfa_secret:
        raise HTTPException(status_code=400, detail='TFA method not set up')

    totp = pyotp.TOTP(user.tfa_secret, interval=300)
    totp.now()

    template_path = await get_template(db, 'tfa')
    email_queue.enqueue(
        send_email,
        template=template_path,
        data={
            'otp': totp.now(),
            'expiry_minutes': settings.TFA_TOKEN_EX // 60,
        },
        subject='Your Two-Factor Authentication Code',
        recipients=[user.email]
    )


@router.post('/verify/{method}', tags=['Two-Factor Authentication'])
async def verify_tfa_code(
    response: Response,
    method: TfaMethod,
    code: str,
    db: Annotated[AsyncSession, Depends(get_async_db)],
    tfa_token: Annotated[str | None, Cookie()] = None,
):
    if not tfa_token:
        raise HTTPException(status_code=401, detail='No TFA token provided')

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Invalid TFA token',
    )

    try:
        serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
        payload = serializer.loads(tfa_token, max_age=settings.ACCESS_TOKEN_EX, salt='user-tfa')
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
    except Exception as ex:
        raise credentials_exception from ex

    result = await db.exec(select(User).where(User.email == username))
    user = result.first()
    if user is None:
        raise credentials_exception

    if not user.tfa_secret:
        return {'verified': False, 'message': 'TFA method not set up'}

    interval = 300 if method == 'email' else 30
    totp = pyotp.TOTP(user.tfa_secret, interval=interval)
    
    if totp.verify(code):
        response.delete_cookie(key='tfa_token')
        response.set_cookie(
            key='tfa_verified',
            value='1',
            httponly=True,
            secure=True,
            samesite='lax',
            max_age=settings.ACCESS_TOKEN_EX,
        )
        return TfaVerificationResponse(verified=True, message='TFA verification successful')

    return TfaVerificationResponse(verified=False, message='Invalid or expired TFA code')


@router.post('/enable/{method}')
async def enable_tfa_method(
    method: TfaMethod,
    current_user: Annotated[User, get_authenticated_user('tfa.enable')],
    db: Annotated[AsyncSession, Depends(get_async_db)],
):
    if method.value not in current_user.tfa_methods:
        current_user.tfa_methods = current_user.tfa_methods + [method.value]

    db.add(current_user)
    await db.commit()
    return {'success': True, 'message': f'{method.capitalize()} TFA enabled successfully'}


@router.post('/disable/{method}')
async def disable_tfa_method(
    method: TfaMethod,
    current_user: Annotated[User, get_authenticated_user('tfa.disable')],
    db: Annotated[AsyncSession, Depends(get_async_db)],
):
    if method.value in current_user.tfa_methods:
        print(f"Disabling {method.value} TFA for user {current_user.email}")
        current_user.tfa_methods = [m for m in current_user.tfa_methods if m != method.value]

    db.add(current_user)
    await db.commit()
    return {'success': True, 'message': f'{method.capitalize()} TFA disabled successfully'}
