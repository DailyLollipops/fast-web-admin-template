# Generated code for ApplicationSetting model

from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlmodel import Session, select, asc, desc
import typing

from database import get_db
from models.user import User
from models.application_setting import ApplicationSetting
from .auth import get_current_user

router = APIRouter()


class ActionResponse(BaseModel):
    success: bool
    message: str


class ApplicationSettingCreate(BaseModel):
    name: str
    value: str = ''
    

class ApplicationSettingResponse(BaseModel):
    id: int = None
    name: str
    value: str = None
    created_at: datetime = None
    updated_at: datetime = None
    modified_by_id: int
    

@router.post('/application_settings', response_model=ApplicationSettingResponse, tags=['ApplicationSetting'])
def create_application_setting(
    data: ApplicationSettingCreate,
	current_user: typing.Annotated[User, Depends(get_current_user)],   
    db: Session = Depends(get_db)
):
    try:
        if db.exec(select(ApplicationSetting).where(ApplicationSetting.name == data.name)).first():
            raise HTTPException(
                status_code=400,
                detail=f'ApplicationSetting with name of {data.name} already exists'
            )
            
        application_setting = ApplicationSetting(**data.model_dump(), modified_by_id=current_user.id)
        db.add(application_setting)
        db.commit()
        return application_setting
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/application_settings', response_model=typing.List[ApplicationSettingResponse], tags=['ApplicationSetting'])
def get_application_settings(
	current_user: typing.Annotated[User, Depends(get_current_user)],  
    order_field: str = 'id', 
    order_by: str = 'desc', 
    limit: int = None, 
    offset: int = None, 
    db: Session = Depends(get_db)
):
    try:
        query = select(ApplicationSetting)
        if order_field is not None:
            if order_field not in ApplicationSetting.model_fields:
                raise HTTPException(
                    status_code=400,
                    detail=f'{order_field} is not a valid field'
                )
            if order_by == 'asc':
                query = query.order_by(asc(getattr(ApplicationSetting, order_field)))
            else:
                query = query.order_by(desc(getattr(ApplicationSetting, order_field)))
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)
        application_settings = db.exec(query).all()
        return application_settings
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/application_settings/{name}', response_model=ApplicationSettingResponse, tags=['ApplicationSetting'])
def get_application_setting(
	current_user: typing.Annotated[User, Depends(get_current_user)],  
    name: str, 
    db: Session = Depends(get_db)
):
    try:
        query = select(ApplicationSetting).where(ApplicationSetting.name == name)
        application_setting = db.exec(query).first()
        if not application_setting:
            raise HTTPException(status_code=404, detail='Application Setting not found')
        return application_setting
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch('/application_settings/{name}', response_model=ApplicationSettingResponse, tags=['ApplicationSetting'])
def update_application_setting(
	current_user: typing.Annotated[User, Depends(get_current_user)],  
    name: str, 
    value: str = Query(...),
    db: Session = Depends(get_db)
):
    error_code = 500
    try:
        query = select(ApplicationSetting).where(ApplicationSetting.name == name)
        application_setting = db.exec(query).first()
        if not application_setting:
            error_code = 404
            raise Exception('Application Setting not found')
        
        application_setting.value = value
        application_setting.modified_by_id = current_user.id
        db.add(application_setting)
        db.commit()
        db.refresh(application_setting)
        return application_setting
    except Exception as e:
        raise HTTPException(status_code=error_code, detail=str(e))

@router.delete('/application_settings/{name}', response_model=ActionResponse, tags=['ApplicationSetting'])
def delete_application_setting(
    name: str,
	current_user: typing.Annotated[User, Depends(get_current_user)],  
    db: Session = Depends(get_db)
):
    try:
        query = select(ApplicationSetting).where(ApplicationSetting.name == name)
        application_setting = db.exec(query).first()
        if not application_setting:
            raise HTTPException(status_code=404, detail='Application Setting not found')
        db.delete(application_setting)
        db.commit()
        return ActionResponse(
            success=True,
            message=f'Application Setting deleted successfully'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
