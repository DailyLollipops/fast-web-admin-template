# Generated code for Notification model

from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import SelectOfScalar

from api.database import get_async_db
from api.database.models.notification import Notification
from api.database.models.user import User
from api.routes.auth import get_authenticated_user
from api.routes.utils import queryutil
from api.routes.utils.crudutils import ActionResponse, make_crud_schemas
from api.routes.utils.queryutil import GetListParams, get_list_params


router = APIRouter()
TAGS: list[str | Enum] = ['Notification']


CreateSchema, UpdateSchema, ResponseSchema, ListResponseSchema = make_crud_schemas(
    Notification,
    addtl_excluded_create_fields=['triggered_by'],
    addtl_excluded_update_fields=['user_id','triggered_by'],
)
NotificationCreate = CreateSchema
NotificationUpdate = UpdateSchema


@router.post('/notifications', response_model=ResponseSchema, tags=TAGS)
async def create_notification(
    data: NotificationCreate,
	current_user: Annotated[User, get_authenticated_user('notifications.create')],
    db: Annotated[AsyncSession, Depends(get_async_db)],
):
    try:
        if not await db.get(User, data.user_id): # type: ignore
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )

        obj = Notification(**data.model_dump(), triggered_by=current_user.id)
        result = await queryutil.create_one(db, obj)
        return result
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex


@router.get('/notifications', response_model=ListResponseSchema, tags=['Notification'])
async def get_notifications(
	current_user: Annotated[User, get_authenticated_user('notifications.read')],
    db: Annotated[AsyncSession, Depends(get_async_db)],
    params: Annotated[GetListParams, Depends(get_list_params)],
):
    try:
        def transform(query: SelectOfScalar[Notification]) -> SelectOfScalar[Notification]:
            return query.where(Notification.user_id == current_user.id)

        total, results = await queryutil.get_list(db, Notification, params, transform=transform)
        data = [ResponseSchema(**r.model_dump()) for r in results]
        return ListResponseSchema(total=total, data=data)
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex


@router.get('/notifications/{id}', response_model=ResponseSchema, tags=['Notification'])
async def get_notification(
	current_user: Annotated[User, get_authenticated_user('notifications.read')],
    db: Annotated[AsyncSession, Depends(get_async_db)],
    id: int,
):
    try:
        def transform(query: SelectOfScalar[Notification]) -> SelectOfScalar[Notification]:
            return query.where(Notification.user_id == current_user.id)

        result = await queryutil.get_one(db, Notification, id, transform=transform)
        return result
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex


@router.patch('/notifications/see_all', response_model=ActionResponse, tags=['Notification'])
async def see_all_notifications(
    current_user: Annotated[User, get_authenticated_user('notifications.see_all')],
    db: Annotated[AsyncSession, Depends(get_async_db)],
):
    try:
        statement = (
            Notification.__table__.update() # type: ignore
            .where(Notification.user_id == current_user.id)
            .values(seen=True)
        )
        await db.exec(statement)
        await db.commit()
        return ActionResponse(
            success=True,
            message='All notifications marked as seen'
        )
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex


@router.patch('/notifications/{id}', response_model=ResponseSchema, tags=['Notification'])
async def update_notification(
	current_user: Annotated[User, get_authenticated_user('notifications.update')],
    db: Annotated[AsyncSession, Depends(get_async_db)],
    id: int,
    data: NotificationUpdate,
):
    try:
        result = await queryutil.update_one(db, Notification, id, data)
        return result
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex


@router.delete('/notifications/{id}', response_model=ActionResponse, tags=['Notification'])
async def delete_notification(
	current_user: Annotated[User, get_authenticated_user('notifications.delete')],
    db: Annotated[AsyncSession, Depends(get_async_db)],
    id: int,
):
    try:
        await queryutil.delete_one(db, Notification, id)
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
