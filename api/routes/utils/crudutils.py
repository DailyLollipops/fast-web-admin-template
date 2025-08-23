from typing import TypeVar

from pydantic import BaseModel, create_model
from sqlmodel import SQLModel


T = TypeVar('T', bound=SQLModel)

class ActionResponse(BaseModel):
    success: bool
    message: str


def make_crud_schemas[T: SQLModel](
    model_cls: type[T],
    addtl_excluded_create_fields: list[str] | None = None,
    addtl_excluded_update_fields: list[str] | None = None,
) -> tuple[type[BaseModel], type[BaseModel], type[BaseModel], type[BaseModel]]:
    """
    Generate Pydantic CRUD schemas dynamically from a SQLModel class.
    Returns: (Create, Update, Response, ListResponse)
    """
    excluded_create_fields = ['modified_by_id', 'created_at', 'updated_at'] + (addtl_excluded_create_fields or [])
    excluded_update_fields = ['created_at', 'updated_at'] + (addtl_excluded_update_fields or [])
    excluded_response_fields = ['password', 'api']

    def get_create_fields() -> dict:
        fields = {}
        for name, field in model_cls.model_fields.items():
            if name in excluded_create_fields:
                continue
            if primary_key := getattr(field, 'primary_key', None):
                if primary_key is True:
                    continue
            fields[name] = (field.annotation, field.default if field.default is not None else ...)
        return fields

    def get_update_fields() -> dict:
        fields = {}
        for name, field in model_cls.model_fields.items():
            if name in excluded_update_fields:
                continue
            if primary_key := getattr(field, 'primary_key', None):
                if primary_key is True:
                    continue
            fields[name] = (field.annotation, None)
        return fields

    def get_response_fields() -> dict:
        fields = {}
        for name, field in model_cls.model_fields.items():
            if name in excluded_response_fields:
                continue
            if hasattr(field, 'sa_relationship'):
                continue
            if name.startswith('_'):
                continue
            fields[name] = (field.annotation, ...)
        return fields

    create_fields = get_create_fields()
    CreateSchema = create_model(f'{model_cls.__name__}Create', **create_fields) # type: ignore

    update_fields = get_update_fields()
    UpdateSchema = create_model(f'{model_cls.__name__}Update', **update_fields) # type: ignore

    response_fields = get_response_fields()
    ResponseSchema = create_model(f'{model_cls.__name__}Response', **response_fields) # type: ignore

    ListResponseSchema = create_model(
        f'{model_cls.__name__}ListResponse',
        total=(int, ...),
        data=(list[ResponseSchema], ...),
    )

    return CreateSchema, UpdateSchema, ResponseSchema, ListResponseSchema
