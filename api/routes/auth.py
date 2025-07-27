from fastapi import APIRouter, HTTPException, Header, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select
from itsdangerous import URLSafeTimedSerializer
from passlib.context import CryptContext
from typing import Annotated, Optional
from pydantic import BaseModel

from models.application_setting import ApplicationSetting
from models.template import Template
from models.user import User
from constants import ApplicationSettings, VerificationMethod
from database import get_db
from settings import settings
from utils import notificationutil, emailutil

import bcrypt


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/login', auto_error=False)
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
ACCESS_TOKEN_EXPIRATION = 3600


class Token(BaseModel):
    access_token: str
    token_type: str


async def get_current_user(
    api_key: Annotated[Optional[str], Header()] = None,
    token: Annotated[Optional[str], Depends(oauth2_scheme)] = None,
    db: Session = Depends(get_db)
):
    user = None
    if api_key:
        try:
            user =  await get_user_by_api_key(db, api_key)
        except HTTPException as e:
            print(f"API Key authentication failed: {str(e)}")
            pass

    if token:
        try:
            user = await get_user_by_jwt_token(db, token)
        except HTTPException as e:
            print(f"Token authentication failed: {str(e)}")
            pass 

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    if not user.verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not verified"
        )
    
    return user


async def get_user_by_api_key(
    db: Session = Depends(get_db), 
    api_key: Annotated[Optional[str], Header()] = None
):
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key missing"
        )
    user = db.exec(select(User).where(User.api == api_key)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return user


async def get_user_by_jwt_token(
    db: Annotated[Session, Depends(get_db)], 
    token: Annotated[str, Depends(oauth2_scheme)] = None
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
    except Exception:
        raise credentials_exception
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
    db: Session = Depends(get_db),
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
        base_url = db.exec(
            select(ApplicationSetting)
            .where(ApplicationSetting.name == ApplicationSettings.BASE_URL)
        ).first().value
        email_verification_template_path = db.exec(
            select(Template)
            .where(ApplicationSetting.name == 'email_verification')
        ).first().path
        verification_url = f'{base_url}/api/auth/verify_email?token={verification_token}'
        data = {
            'name': new_user.name,
            'verification_url': verification_url
        }
        await emailutil.send_email(
            db=db,
            template=email_verification_template_path,
            data=data,
            subject='Verify your email address',
            recipients=[new_user.email]
        )

    return Token(access_token=access_token, token_type='bearer')

@router.post('/auth/login', tags=['Authentication'])
async def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
) -> Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail='User not found')
    if not user.verified:
        raise HTTPException(status_code=401, detail='User not verified. Please contact admin for more details!')

    access_token = create_access_token(data={'sub': user.email}, salt='user-auth')
    return Token(access_token=access_token, token_type='bearer')

@router.get('/auth/verify_email', response_model=ActionResponse, tags=['Authentication'])
async def verify_email(token: str, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
        payload = serializer.loads(token, max=ACCESS_TOKEN_EXPIRATION, salt='user-verification')
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    
    user = db.exec(select(User).where(User.email == username)).first()
    if user is None:
        raise credentials_exception
    
    user.verified = True
    db.add(user)
    db.commit()
    return ActionResponse(success=True, message='Email successfully verified')
