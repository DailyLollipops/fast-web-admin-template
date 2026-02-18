import os
from datetime import datetime
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from api.database import get_async_db
from api.database.models.template import Template
from api.database.models.user import User
from api.routes.auth import get_authenticated_user
from api.routes.utils import queryutil
from api.routes.utils.crudutils import ActionResponse, make_crud_schemas
from api.routes.utils.queryutil import GetListParams, get_list_params


router = APIRouter(tags=['Template'])
TEMPLATE_PATH = Path(__file__).parent.parent / 'templates'

CreateSchema, UpdateSchema, ResponseSchema, ListResponseSchema = make_crud_schemas(
    Template,
    addtl_included_create_fields=[('content', str)],
    addtl_included_response_fields=[('content', str)],
    addtl_included_update_fields=[('content', str)],
    addtl_excluded_create_fields=['path'],
    addtl_excluded_response_fields=['path'],
    addtl_excluded_update_fields=['name', 'template_type', 'path'],
)
TemplateCreate = CreateSchema
TemplateUpdate = UpdateSchema


def get_template_content(template: Template) -> str:
    return Path(template.path).read_text() if template.path else ''


@router.post('/templates', response_model=ResponseSchema)
async def create_template(
	current_user: Annotated[User, get_authenticated_user('templates.create')],
    db: Annotated[AsyncSession, Depends(get_async_db)],
    data: TemplateCreate,
):
    try:
        tpl_path = TEMPLATE_PATH / f'{data.template_type}s' # type: ignore
        os.makedirs(tpl_path, exist_ok=True)
        file_path = tpl_path / f'{data.name}.j2' # type: ignore
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(data.content) # type: ignore
        
        obj = Template(**data.model_dump())
        obj.path = str(file_path)
        obj.modified_by_id = current_user.id
        result = await queryutil.create_one(db, obj)
        return ResponseSchema(**result.model_dump(), content=get_template_content(result))
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex


@router.get('/templates', response_model=ListResponseSchema)
async def get_templates(
	current_user: Annotated[User, get_authenticated_user('templates.read')],
    db: Annotated[AsyncSession, Depends(get_async_db)],
    params: Annotated[GetListParams, Depends(get_list_params)],
):
    try:
        total, results = await queryutil.get_list(db, Template, params)
        data = [ResponseSchema(**r.model_dump(), content=get_template_content(r)) for r in results]
        return ListResponseSchema(total=total, data=data)
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex


@router.get('/templates/{id}', response_model=ResponseSchema)
async def get_template(
	current_user: Annotated[User, get_authenticated_user('templates.read')],
    db: Annotated[AsyncSession, Depends(get_async_db)],
    id: int,
):
    try:
        result = await queryutil.get_one(db, Template, id)
        return ResponseSchema(**result.model_dump(), content=get_template_content(result))
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex


@router.patch('/templates/{id}', response_model=ResponseSchema)
async def update_template(
	current_user: Annotated[User, get_authenticated_user('templates.update')],
    db: Annotated[AsyncSession, Depends(get_async_db)],
    id: int,
    data: TemplateUpdate,
):
    try:
        template = await queryutil.get_one(db, Template, id)

        path = Path(template.path)
        file_name = f'{template.name}_{int(datetime.now().timestamp())}{path.suffix}'
        new_path = TEMPLATE_PATH / 'modified' / file_name
        with open(new_path, 'w', encoding='utf-8') as f:
            f.write(data.content) # type: ignore

        template.path = str(new_path)
        template.modified_by_id = current_user.id
        db.add(template)
        await db.commit()
        await db.refresh(template)
        return ResponseSchema(**template.model_dump(), content=get_template_content(template))
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex


@router.delete('/templates/{id}', response_model=ActionResponse)
async def delete_template(
	current_user: Annotated[User, get_authenticated_user('templates.delete')],
    db: Annotated[AsyncSession, Depends(get_async_db)],
    id: int,
):
    try:
        await queryutil.delete_one(db, Template, id)
        return ActionResponse(
            success=True,
            message='Template deleted successfully'
        )
    except HTTPException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        ) from ex
