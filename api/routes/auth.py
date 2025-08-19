from typing import Annotated

import bcrypt
from constants import ApplicationSettings, VerificationMethod
from database import get_db
from database.models.application_setting import ApplicationSetting
from database.models.role_access_control import RoleAccessControl
from database.models.template import Template
from database.models.user import User
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from itsdangerous import URLSafeTimedSerializer
from passlib.context import CryptContext
from pydantic import BaseModel
from settings import settings
from sqlmodel import Session, select

from .utils import emailutil, notificationutil


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/login', auto_error=False)
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
ACCESS_TOKEN_EXPIRATION = 3600

class Token(BaseModel):
    access_token: str
    token_type: str


def can_access(db: Session, resource: str, action: str, role: str):
    q = select(RoleAccessControl).where(RoleAccessControl.role == role)
    result = db.exec(q).first()
    
    if not result:
        return False
    
    # Permission format: <resource>.<action>
    for permission in result.permissions:
        if permission == '*':
            return True

        p_resource = permission.split('.')[0]
        p_action = permission.split('.')[1]

        if p_resource in [resource, '*'] and p_action in [action, '*']:
            return True
    
    return False


async def get_current_user(
    request: Request,
    api_key: Annotated[str | None, Header()] = None,
    token: Annotated[str | None, Depends(oauth2_scheme)] = None,
):
    db: Session = next(get_db())
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
    resource = request.url.path.split('/')[1]
    action = action_map.get(request.method, '')
    if not can_access(db, resource, action, user.role):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='No access to resource'
        )

    return user


async def get_user_by_api_key(
    db: Session,
    api_key: Annotated[str | None, Header()] = None
):
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='API key missing'
        )
    user = db.exec(select(User).where(User.api == api_key)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid API key'
        )
    return user


async def get_user_by_jwt_token(
    db: Session,
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
    user = db.exec(select(User).where(User.email == username)).first()
    if user is None:
        raise credentials_exception
    return user


def authenticate_user(username: str, password: str, db: Session):
    query = select(User).where(User.email == username)
    user = db.exec(query).first()
    if not user:
        return None
    if not pwd_context.verify(password, user.password):
        return None
    return user


def create_access_token(data: dict, salt: str | bytes | None = None):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    token = serializer.dumps(data, salt)
    return token


class RegisterForm(BaseModel):
    name: str
    email: str
    password: str
    confirm_password: str


class ActionResponse(BaseModel):
    success: bool
    message: str


@router.post('/auth/register', tags=['Authentication'])
async def register_user(
    data: RegisterForm,
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    if data.password != data.confirm_password:
        raise HTTPException(
            status_code=400,
            detail='Passwords do not match'
        )

    existing_user = db.exec(select(User).where(User.email == data.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail='Email/Username already registered'
        )

    verification_setting = db.exec(
        select(ApplicationSetting)
        .where(ApplicationSetting.name == ApplicationSettings.USER_VERIFICATION)
    ).first()

    if not verification_setting:
        raise Exception('User verification setting not found. Perhaps you forgot to run migration?')

    hashed_password = bcrypt.hashpw(data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    new_user = User(
        name=data.name,
        email=data.email,
        password=hashed_password,
        verified=True if verification_setting.value == VerificationMethod.NONE else False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(data={'sub': data.email}, salt='user-auth')

    notificationutil.notify_role(
        db=db,
        triggered_by=new_user.id,
        roles=['admin'],
        title='New user has been created',
        body=f'A new user has been created by an admin with email: {new_user.email}'
    )
    notificationutil.notify_user(
        db=db,
        triggered_by=2,
        user_id=new_user.id,
        title='Welcome to the app',
        body=f'Hello {new_user.name}, welcome to the app!'
    )

    if verification_setting.value == VerificationMethod.EMAIL:
        verification_token = create_access_token(data={'sub': data.email}, salt='user-verification')

        base_url_setting = db.exec(
            select(ApplicationSetting)
            .where(ApplicationSetting.name == ApplicationSettings.BASE_URL)
        ).first()
        if not base_url_setting:
            raise Exception('Email base url setting not found. Perhaps you forgot to run migration?')
        
        email_template_setting = db.exec(
            select(Template)
            .where(ApplicationSetting.name == 'email_verification')
        ).first()
        if not email_template_setting:
            raise Exception('Email template path setting not found. Perhaps you forgot to run migration?')
        
        base_url = base_url_setting.value
        email_verification_template_path = email_template_setting.path
        verification_url = f'{base_url}/api/auth/verify_email?token={verification_token}'
        new_data = {
            'name': new_user.name,
            'verification_url': verification_url
        }
        await emailutil.send_email(
            db=db,
            template=email_verification_template_path,
            data=new_data,
            subject='Verify your email address',
            recipients=[new_user.email]
        )

    return Token(access_token=access_token, token_type='bearer')


@router.post('/auth/login', tags=['Authentication'])
async def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail='User not found')
    if not user.verified:
        raise HTTPException(status_code=401, detail='User not verified. Please contact admin for more details!')

    access_token = create_access_token(data={'sub': user.email}, salt='user-auth')
    return Token(access_token=access_token, token_type='bearer')


@router.get('/auth/verify_email', response_model=ActionResponse, tags=['Authentication'])
async def verify_email(
    token: str,
    db: Annotated[Session, Depends(get_db)],
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
    
    user = db.exec(select(User).where(User.email == username)).first()
    if user is None:
        raise credentials_exception
    
    user.verified = True
    db.add(user)
    db.commit()
    return ActionResponse(success=True, message='Email successfully verified')
