from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select, delete, asc, desc
from sqlalchemy import or_
from enum import Enum
from typing import Annotated, Optional, List
from pydantic import BaseModel
import bcrypt
import json

from models.user import User
from models.notification import Notification
from database import get_db
from utils import notificationutil
from .auth import get_current_user

router = APIRouter()

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
    role: Optional[str] = 'user'
    verified: Optional[bool] = False

class UserResponse(BaseModel):
    id: int
    email: str 
    role: str 
    name: str

@router.post('/users', response_model=UserResponse, tags=['User'])
async def create_user(
    data: UserCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """
    Create a new user.
    Requires `admin` role
    """
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='No access to resource',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    existing_user = db.exec(select(User).where(User.email == data.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email/Username already registered',
        )
    
    data.password = bcrypt.hashpw(data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    new_user = User(**data.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get('/users', response_model=List[UserResponse], tags=['User'])
async def get_users(
    current_user: Annotated[User, Depends(get_current_user)],
    order_field: str = 'id', 
    order_by: str = 'desc', 
    limit: int = None, 
    offset: int = None, 
    filters: str = None, 
    db: Session = Depends(get_db),
):
    """
    Get all users with limited information.
    Requires `admin` role
    """
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='No access to resource',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    try:
        query = select(User)
        if filters:
            filters_dict = {}
            filter_exc = HTTPException(status_code=400, detail='Invalid filter parameter')
            try:
                filters_dict = json.loads(filters)
                if not isinstance(filters_dict, dict):
                    raise filter_exc
            except Exception:
                raise filter_exc
            for key, value in filters_dict.items():
                if key not in User.model_fields:
                    continue
                column = getattr(User, key)
                query = query.where(column == value)
        if order_field is not None:
            if order_field not in User.model_fields:
                raise HTTPException(
                    status_code=400,
                    detail=f'{order_field} is not a valid field'
                )
            if order_by == 'asc':
                query = query.order_by(asc(getattr(User, order_field)))
            else:
                query = query.order_by(desc(getattr(User, order_field)))
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)
        branchs = db.exec(query).all()
        return branchs
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/users/{id}', response_model=UserResponse, tags=['User'])
async def get_user(
    id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """
    Get user info.
    Requires `admin` role
    """
    if not id.isnumeric():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Id must be numeric',
        )
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='No access to resource',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    user = db.exec(select(User).where(User.id == int(id))).first()
    return user

@router.patch("/users/verify/{id}", response_model=UserResponse, tags=['User'])
async def verify_user(
    id: int, 
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Verify user to be able to use application
    """
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=401, detail='No access to resource')
    
    query = select(User).where(User.id == id)
    user = db.exec(query).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.verified = True

    db.add(user)
    db.commit()

    notificationutil.notify_role(
        db=db,
        triggered_by=current_user.id,
        roles=['admin'],
        title='User has been verified',
        body=f'User ID {user.id} has been verified.'
    )

    return user

@router.patch('/users/role/{id}', response_model=UserResponse, tags=['User'])
async def update_user_role(
    id: str,
    role: UserRole,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Update user role.
    Requires `admin` role
    """
    if role not in UserRole:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid role',
        )
    
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='No access to resource',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    
    user = db.exec(select(User).where(User.id == int(id))).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User not found',
        )

    user.role = role
    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@router.delete('/users/{id}', tags=['User'])
async def delete_user(
    id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Delete user.
    Requires `admin` role
    """
    if not id.isnumeric():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Id must be numeric',
        )
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='No access to resource',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    user = db.exec(select(User).where(User.id == int(id))).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User not found',
        )
    if user.role == UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Cannot delete user with admin role',
        )
    query = delete(Notification).where(
        or_(
            Notification.user_id == user.id,
            Notification.triggered_by == user.id
        )
    )
    db.exec(query)
    db.delete(user)
    db.commit()

    return ActionResponse(
        success=True,
        message='User deleted successfully'
    )

@router.get('/me', response_model=UserResponse, tags=['User'])
async def me(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    return current_user
