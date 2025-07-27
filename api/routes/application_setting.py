# Generated code for ApplicationSetting model

from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlmodel import Session, select, asc, desc, func
from typing import Annotated, List, Optional
import json

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
    id: int
    name: str
    value: str
    created_at: datetime
    updated_at: datetime
    modified_by_id: int


class ApplicationSettingListResponse(BaseModel):
    total: int
    data: List[ApplicationSettingResponse]


@router.post('/application_settings', response_model=ApplicationSettingResponse, tags=['ApplicationSetting'])
def create_application_setting(
    data: ApplicationSettingCreate,
	current_user: Annotated[User, Depends(get_current_user)],   
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
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


@router.get('/application_settings', response_model=ApplicationSettingListResponse, tags=['ApplicationSetting'])
def get_application_settings(
	current_user: Annotated[User, Depends(get_current_user)],  
    order_field: str = 'id', 
    order_by: str = 'desc', 
    limit: Optional[int] = None, 
    offset: Optional[int] = None, 
    filters: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    try:
        query = select(ApplicationSetting)
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
                if key not in ApplicationSetting.model_fields:
                    continue
                column = getattr(ApplicationSetting, key)
                query = query.where(column == value)

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

        count_query = select(func.count()).select_from(query.subquery())
        total = db.exec(count_query).first() or 0

        if offset is not None:
            query = query.offset(offset)

        if limit is not None:
            query = query.limit(limit)

        application_settings = db.exec(query).all()
        application_settings = [ApplicationSettingResponse(**d.model_dump()) for d in application_settings]
        return ApplicationSettingListResponse(total=total, data=application_settings)
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


@router.get('/application_settings/{name}', response_model=ApplicationSettingResponse, tags=['ApplicationSetting'])
def get_application_setting(
	current_user: Annotated[User, Depends(get_current_user)],  
    name: str, 
    db: Session = Depends(get_db)
):
    try:
        query = select(ApplicationSetting).where(ApplicationSetting.name == name)
        application_setting = db.exec(query).first()
        if not application_setting:
            raise HTTPException(status_code=404, detail='Application Setting not found')
        return application_setting
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


@router.patch('/application_settings/{name}', response_model=ApplicationSettingResponse, tags=['ApplicationSetting'])
def update_application_setting(
	current_user: Annotated[User, Depends(get_current_user)],  
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
    except Exception as ex:
        raise HTTPException(status_code=error_code, detail=str(ex))


@router.delete('/application_settings/{name}', response_model=ActionResponse, tags=['ApplicationSetting'])
def delete_application_setting(
    name: str,
	current_user: Annotated[User, Depends(get_current_user)],  
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
            message='Application Setting deleted successfully'
        )
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
