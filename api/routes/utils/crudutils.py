from typing import TypeVar

from pydantic import BaseModel, create_model
from sqlmodel import SQLModel


T = TypeVar('T', bound=SQLModel)

class ActionResponse(BaseModel):
    success: bool
    message: str


def make_crud_schemas[T: SQLModel](
    model_cls: type[T]
) -> tuple[type[BaseModel], type[BaseModel], type[BaseModel], type[BaseModel]]:
    """
    Generate Pydantic CRUD schemas dynamically from a SQLModel class.
    Returns: (Create, Update, Response, ListResponse)
    """
    fields = model_cls.model_fields
    excluded_create_fields = ['modified_by_id', 'created_at', 'updated_at']
    excluded_update_fields = ['created_at', 'updated_at']
    excluded_response_fields = ['password', 'api']

    create_fields = {
        name: (field.annotation, field.default if field.default is not None else ...)
        for name, field in fields.items()
        if field.primary_key is not True and name not in excluded_create_fields
    }
    CreateSchema = create_model(f'{model_cls.__name__}Create', **create_fields) # type: ignore

    update_fields = {
        name: (field.annotation, None)
        for name, field in fields.items()
        if field.primary_key is not True and name not in excluded_update_fields
    }
    UpdateSchema = create_model(f'{model_cls.__name__}Update', **update_fields) # type: ignore

    response_fields = {
        name: (field.annotation, ...)
        for name, field in fields.items()
        if not name.startswith('_') \
            and not hasattr(field, 'sa_relationship') \
            and name not in excluded_response_fields
    }
    ResponseSchema = create_model(f'{model_cls.__name__}Response', **response_fields) # type: ignore

    ListResponseSchema = create_model(
        f'{model_cls.__name__}ListResponse',
        total=(int, ...),
        data=(list[ResponseSchema], ...),
    )

    return CreateSchema, UpdateSchema, ResponseSchema, ListResponseSchema
