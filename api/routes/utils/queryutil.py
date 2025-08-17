import json
from enum import Enum
from typing import Any, TypeVar

from fastapi import HTTPException, Query, status
from pydantic import BaseModel, ValidationError, model_validator
from sqlmodel import Session, SQLModel, asc, desc, func, select


T = TypeVar('T', bound=SQLModel)

class Operands(str, Enum):
    eq = '=='
    neq = '!='
    gt = '>'
    gte = '>='
    lt = '<'
    lte = '<='
    in_ = 'in'
    not_in = 'not_in'


class GetListFilter(BaseModel):
    field: str
    op: Operands
    value: Any


class GetListParams(BaseModel):
    order_field: str = 'id'
    order_by: str = 'desc'
    limit: int | None = None
    offset: int | None = None
    filters: list[GetListFilter] | None = None

    @model_validator(mode='before')
    def check_order_by(cls, values):
        order_by = values.get('order_by')
        if order_by not in {'asc', 'desc'}:
            raise ValueError('order_by must be `asc` or `desc`')
        return values


def get_list_params(
    order_field: str = Query('id', description='Field to order by'),
    order_by: str = Query('asc', description='Order direction: asc or desc'),
    limit: int = Query(10, ge=1, le=100, description='Limit number of results'),
    offset: int = Query(0, ge=0, description='Number of items to skip'),
    filters: str | None = Query(None, description='JSON encoded list of filters'),
) -> GetListParams:
    parsed_filters = None
    if filters:
        try:
            filters_data = json.loads(filters)
            parsed_filters = [GetListFilter.model_validate(item) for item in filters_data]
        except (json.JSONDecodeError, ValidationError) as ex:
            raise ValueError(f"Invalid filters JSON: {ex}") from ex

    return GetListParams(
        order_field=order_field,
        order_by=order_by,
        limit=limit,
        offset=offset,
        filters=parsed_filters,
    )


def create_one(db: Session, data: SQLModel):
    model_cls = type(data)
    unique_fields = [
        field
        for field, info in model_cls.model_fields.items()
        if getattr(info, 'unique', False)
    ]

    q = select(model_cls)
    for field in unique_fields:
        q = q.where(getattr(model_cls, field) == getattr(data, field))

    if db.exec(q).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'{model_cls.__name__} unique constraint failed'
        )

    db.add(data)
    db.commit()
    db.refresh(data)
    return data


def create_many[T: SQLModel](db: Session, data: list[T]):
    model_cls = type(data[0])
    unique_fields = [
        field
        for field, info in model_cls.model_fields.items()
        if getattr(info, 'unique', False)
    ]

    for obj in data:
        q = select(model_cls)
        for field in unique_fields:
            q = q.where(getattr(model_cls, field) == getattr(obj, field))

        if db.exec(q).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'{model_cls.__name__} unique constraint failed'
            )
        
    db.add_all(data)
    db.commit()
    for obj in data:
        db.refresh(obj)
    return data


def get_one[T: SQLModel](db: Session, model_cls: type[T], id: int):
    if result := db.get(model_cls, id):
        return result
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'{model_cls.__name__} not found'
    )


def get_many[T: SQLModel](db: Session, model_cls: type[T], ids: list[int]):
    q = (
        select(model_cls)
        .where(model_cls.id.in_(ids)) # type: ignore
    )
    return db.exec(q).all()


def get_list[T: SQLModel](
    db: Session,
    model_cls: type[T],
    params: GetListParams,
):
    q = select(model_cls)
    if params.filters:
        for filter in params.filters:
            if filter.field not in model_cls.model_fields:
                continue
            
            column = getattr(model_cls, filter.field)
            if filter.op == Operands.eq:
                q = q.where(column == filter.value)
            elif filter.op == Operands.neq:
                q = q.where(column != filter.value)
            elif filter.op == Operands.gt:
                q = q.where(column > filter.value)
            elif filter.op == Operands.gte:
                q = q.where(column >= filter.value)
            elif filter.op == Operands.lt:
                q = q.where(column < filter.value)
            elif filter.op == Operands.lte:
                q = q.where(column <= filter.value)
            elif filter.op == Operands.in_:
                if isinstance(filter.value, list) and filter.value:
                    if column := getattr(model_cls, filter.field, None):
                        q = q.where(column.in_(filter.value))
            elif filter.op == Operands.not_in:
                if isinstance(filter.value, list) and filter.value:
                    if column := getattr(model_cls, filter.field, None):
                        q = q.where(~column.in_(filter.value))

    if params.order_field is not None:
        if params.order_field not in model_cls.model_fields:
            raise HTTPException(
                status_code=400,
                detail=f'{params.order_field} is not a valid field'
            )
        if params.order_by == 'asc':
            q = q.order_by(asc(getattr(model_cls, params.order_field)))
        else:
            q = q.order_by(desc(getattr(model_cls, params.order_field)))

    cq = select(func.count()).select_from(q.subquery())
    total = db.exec(cq).first() or 0

    if params.offset is not None:
        q = q.offset(params.offset)

    if params.limit is not None:
        q = q.limit(params.limit)

    result = db.exec(q).all()
    return total, result


def update_one(db: Session, model_cls: type[SQLModel], id: int, data: BaseModel):
    unique_fields = [
        field
        for field, info in model_cls.model_fields.items()
        if getattr(info, 'unique', False)
    ]

    obj = db.get(model_cls, id)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'{model_cls.__name__} not found'
        )

    q = select(model_cls)
    q = q.where(model_cls.id != id) # type: ignore
    for field in unique_fields:
        q = q.where(getattr(model_cls, field) == getattr(data, field))

    if db.exec(q).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'{model_cls.__name__} unique constraint failed'
        )

    for field in data.model_fields:
        if (value := getattr(data, field, None)) is not None:
            setattr(obj, field, value)

    db.add(obj)
    db.commit()
    db.refresh(data)
    return data


def update_many(db: Session, model_cls: type[SQLModel], ids: list[int], data_list: list[BaseModel]):
    unique_fields = [
        field
        for field, info in model_cls.model_fields.items()
        if getattr(info, 'unique', False)
    ]

    updated_objs = []
    for id, data in zip(ids, data_list, strict=False):
        obj = db.get(model_cls, id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'{model_cls.__name__} not found'
            )

        q = select(model_cls)
        q = q.where(model_cls.id != obj.id) # type: ignore
        for field in unique_fields:
            q = q.where(getattr(model_cls, field) == getattr(obj, field))

        if db.exec(q).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'{model_cls.__name__} unique constraint failed'
            )
        
        for field in data.model_fields:
            if (value := getattr(data, field, None)) is not None:
                setattr(obj, field, value)

        updated_objs.append(obj)

    db.add_all(updated_objs)
    db.commit()
    for obj in updated_objs:
        db.refresh(obj)
    return updated_objs


def delete_one[T: SQLModel](db: Session, model_cls: type[T], id: int):
    result = db.get(model_cls, id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'{model_cls.__name__} not found'
        )
    db.delete(result)
    db.commit()


def delete_many[T: SQLModel](db: Session, model_cls: type[T], ids: list[int]):
    for id in ids:
        result = db.get(model_cls, id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'{model_cls.__name__} not found'
            )
        db.delete(result)
    db.commit()
