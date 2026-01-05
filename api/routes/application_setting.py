from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from api.database import get_async_db
from api.database.models.application_setting import ApplicationSetting
from api.database.models.user import User
from api.routes.auth.core import get_authenticated_user
from api.routes.utils import queryutil
from api.routes.utils.crudutils import ActionResponse, make_crud_schemas
from api.routes.utils.queryutil import GetListParams, get_list_params


router = APIRouter()
TAGS: list[str | Enum] = ['Application Setting']


CreateSchema, UpdateSchema, ResponseSchema, ListResponseSchema = make_crud_schemas(
    ApplicationSetting,
    addtl_excluded_create_fields=['modified_by_id'],
    addtl_excluded_update_fields=['modified_by_id'],
)
ApplicationSettingCreate = CreateSchema
ApplicationSettingUpdate = UpdateSchema


@router.post('/application_settings', response_model=ResponseSchema, tags=TAGS)
async def create_application_setting(
	current_user: Annotated[User, get_authenticated_user('application_settings.create')],
    db: Annotated[AsyncSession, Depends(get_async_db)],
    data: ApplicationSettingCreate,
):
    try:
        fields = data.model_dump()
        obj = ApplicationSetting(
            **fields,
            modified_by_id=current_user.id
        )
        result = await queryutil.create_one(db, obj)
        return result
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex


@router.get('/application_settings', response_model=ListResponseSchema, tags=TAGS)
async def get_application_settings(
	current_user: Annotated[User, get_authenticated_user('application_settings.read')],
    db: Annotated[AsyncSession, Depends(get_async_db)],
    params: Annotated[GetListParams, Depends(get_list_params)],
):
    try:
        total, results = await queryutil.get_list(db, ApplicationSetting, params)
        data = [ResponseSchema(**r.model_dump()) for r in results]
        return ListResponseSchema(total=total, data=data)
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex


@router.get('/application_settings/{id}', response_model=ResponseSchema, tags=TAGS)
async def get_application_setting(
	current_user: Annotated[User, get_authenticated_user('application_settings.read')],
    db: Annotated[AsyncSession, Depends(get_async_db)],
    id: int,
):
    try:
        result = await queryutil.get_one(db, ApplicationSetting, id)
        return result
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex


@router.patch('/application_settings/{id}', response_model=ResponseSchema, tags=TAGS)
async def update_application_setting(
	current_user: Annotated[User, get_authenticated_user('application_settings.update')],
    db: Annotated[AsyncSession, Depends(get_async_db)],
    id: int,
    data: ApplicationSettingUpdate,
):
    class ModifiedData(ApplicationSettingUpdate):
        modified_by_id: int

    try:
        modified = ModifiedData(**data.model_dump(), modified_by_id=current_user.id)
        result = await queryutil.update_one(db, ApplicationSetting, id, modified)
        return result
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex


@router.delete('/application_settings/{id}', response_model=ActionResponse, tags=TAGS)
async def delete_application_setting(
	current_user: Annotated[User, get_authenticated_user('application_settings.delete')],
    db: Annotated[AsyncSession, Depends(get_async_db)],
    id: int,
):
    try:
        await queryutil.delete_one(db, ApplicationSetting, id)
        return ActionResponse(
            success=True,
            message='Application Setting deleted successfully'
        )
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex
