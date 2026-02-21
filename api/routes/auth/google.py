from typing import Annotated

import pyotp
from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse
from itsdangerous import URLSafeTimedSerializer
from loguru import logger
from pydantic import BaseModel
from rq import Queue
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from worker.queue import get_notification_queue
from worker.tasks.notification import notify_role, notify_user

from api.database import get_async_db
from api.database.models.user import User
from api.routes.auth.core import create_access_token
from api.settings import settings


router = APIRouter(tags=['Authentication (Google)'])
oauth = OAuth()

oauth.register(
    name='google',
    client_id=settings.GOOGLE_OAUTH_CLIENT_ID,
    client_secret=settings.GOOGLE_OAUTH_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    },
)


class GoogleUserSchema(BaseModel):
    email: str
    name: str
    sub: str


class OAuthStateSchema(BaseModel):
    next_url: str = ''
    tfa_url: str = ''
    remember: bool = False


def create_oauth_state_token(data: dict, salt: str | bytes | None = None):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    token = serializer.dumps(data, salt)
    return token


def verify_oauth_state(state_token: str) -> OAuthStateSchema:
    try:
        serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
        payload = serializer.loads(state_token, salt='oauth-state')
        return OAuthStateSchema(**payload)
    except Exception as ex:
        print(f'Error verifying OAuth state: {ex}')
        return OAuthStateSchema()


@router.get('/login')
async def google_login(request: Request, next_url: str = '/', remember: bool = False):
    redirect_uri = request.url_for('google_callback')
    state = OAuthStateSchema(next_url=next_url, remember=remember)
    state_token = create_oauth_state_token(data=state.model_dump(), salt='oauth-state')
    return await oauth.google.authorize_redirect(  # type: ignore
        request,
        redirect_uri,
        state=state_token,
        prompt='select_account',
    )


@router.get('/callback', name='google_callback')
async def google_callback(
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_async_db)],
    notification_queue: Annotated[Queue, Depends(get_notification_queue)],
    tfa_verified: Annotated[str | None, Cookie()] = None,
    state: str = '',
):
    oauth_state = verify_oauth_state(state)
    logger.debug(f'OAuth state: {oauth_state}')
    token = await oauth.google.authorize_access_token(request) # type: ignore
    user_info = token.get('userinfo')

    if not user_info:
        raise HTTPException(status_code=400, detail='Google authentication failed')
    
    google_user = GoogleUserSchema(**user_info)

    result = await db.exec(select(User).where(User.email == google_user.email))
    user = result.first()
    if not user:
        user = User(
            email=google_user.email,
            name=google_user.name,
            provider='google',
            provider_id=google_user.sub,
            verified=True,
            tfa_secret=pyotp.random_base32(),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        notification_queue.enqueue(
            notify_role,
            triggered_by=user.id,
            category='registration',
            roles=['admin'],
            title='New user has been created',
            body=f'A new user has been created by an admin with email: {user.email}'
        )

        notification_queue.enqueue(
            notify_user,
            triggered_by=2,
            category='registration',
            user_id=user.id,
            title='Welcome to the app',
            body=f'Hello {user.name}, welcome to the app!'
        )

    if user.tfa_methods and not tfa_verified:
        tfa_token = create_access_token(data={'sub': user.email}, salt='user-tfa')
        user_info = create_access_token(data=user_info, salt='user-info')
        response = HTMLResponse(content=f"""
            <script>
                if (window.opener) {{
                    window.opener.postMessage("tfa-required?tfa_token={tfa_token}&user_info={user_info}&methods={','.join(user.tfa_methods)}", window.location.origin);
                    window.close();
                }} else {{
                    window.location.href = "/2fa";
                }}
            </script>
        """)  # noqa: E501

        response.set_cookie(
            key='tfa_token',
            value=tfa_token,
            httponly=True,
            secure=True,
            samesite='lax',
            max_age=settings.TFA_TOKEN_EX,
        )

        return response
        
    if tfa_verified and tfa_verified != '1':
        raise HTTPException(status_code=401, detail='Invalid TFA verification status')

    access_token = create_access_token(data={'sub': user.email}, salt='user-auth')
    refresh_token = create_access_token(data={'sub': user.email}, salt='user-refresh')
    response = HTMLResponse(content="""
        <script>
            if (window.opener) {
                window.opener.postMessage("login-success", window.location.origin);
                window.close();
            } else {
                window.location.href = "/";
            }
        </script>
        """
    )

    response.delete_cookie(key='tfa_token')
    response.delete_cookie(key='tfa_verified')
    response.delete_cookie(key='user_info')
    response.set_cookie(
        key='access_token',
        value=access_token,
        httponly=True,
        secure=True,
        samesite='lax',
        max_age=settings.ACCESS_TOKEN_EX,
    )

    if oauth_state.remember:
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite='lax',
            max_age=settings.REFRESH_TOKEN_EX,
        )

    return response


@router.post('/login_2fa')
async def login_2fa(
    response: Response,
    db: Annotated[AsyncSession, Depends(get_async_db)],
    tfa_verified: Annotated[str, Cookie()],
    user_info: Annotated[str, Cookie()],
    remember: bool = False,
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Invalid user_info token',
    )

    if tfa_verified != '1':
        raise HTTPException(status_code=401, detail='TFA verification required')

    try:
        serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
        payload = serializer.loads(user_info, max_age=settings.ACCESS_TOKEN_EX, salt='user-info')
    except Exception as ex:
        raise credentials_exception from ex
    
    google_user = GoogleUserSchema(**payload)
    result = await db.exec(select(User).where(User.email == google_user.email))
    user = result.first()
    if not user:
        raise HTTPException(status_code=400, detail='User not found')

    access_token = create_access_token(data={'sub': user.email}, salt='user-auth')
    refresh_token = create_access_token(data={'sub': user.email}, salt='user-refresh')

    response.delete_cookie(key='tfa_token')
    response.delete_cookie(key='tfa_verified')
    response.delete_cookie(key='user_info')
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
        )

    data = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer',
    }
    return data
