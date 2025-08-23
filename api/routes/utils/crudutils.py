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
    if addtl_excluded_update_fields is None:
        addtl_excluded_update_fields = []
    if addtl_excluded_create_fields is None:
        addtl_excluded_create_fields = []
    def get_fields(exclude: list[str]) -> dict:
        fields = {}
        for name, field in model_cls.model_fields.items():
            if name in exclude:
                continue
            if primary_key := getattr(field, 'primary_key', None):
                if primary_key is True:
                    continue
            fields[name] = (field.annotation, field.default if field.default is not None else ...)
        return fields

    fields = model_cls.model_fields
    excluded_create_fields = ['modified_by_id', 'created_at', 'updated_at'] + (addtl_excluded_create_fields or [])
    excluded_update_fields = ['created_at', 'updated_at'] + (addtl_excluded_update_fields or [])
    excluded_response_fields = ['password', 'api']

    create_fields = get_fields(excluded_create_fields)
    CreateSchema = create_model(f'{model_cls.__name__}Create', **create_fields) # type: ignore

    update_fields = get_fields(excluded_update_fields)
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
