from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select, delete
from sqlalchemy import or_
from enum import Enum
from typing import Annotated, Optional, List
from pydantic import BaseModel
import bcrypt

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

@router.post('/users', tags=['User'])
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

    new_user = User(**data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return ActionResponse(
        success=True,
        message=f'User created successfully with ID of {new_user.id}'
    )

@router.get('/users', response_model=List[UserResponse], tags=['User'])
async def get_users(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    role: Optional[UserRole] = None,
    verified: Optional[bool] = None
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
    query = select(User)
    if role:
        query = query.where(User.role == role)
    if verified is not None:
        query = query.where(User.verified == verified)
    users = db.exec(query).all()
    return users

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

@router.patch("/users/verify/{id}", response_model=ActionResponse, tags=['User'])
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

    return ActionResponse(
        success=True,
        message='User verified successfully'
    )

@router.patch('/users/role/{id}', tags=['User'])
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

    return ActionResponse(
        success=True,
        message='User role updated successfully'
    )

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
