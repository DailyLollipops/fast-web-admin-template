import json
from collections.abc import Callable
from enum import Enum
from typing import Any, TypeVar

from fastapi import HTTPException, Query, status
from pydantic import BaseModel, ValidationError, model_validator
from sqlalchemy.orm import selectinload
from sqlmodel import SQLModel, asc, desc, func, inspect, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import SelectOfScalar


T = TypeVar('T', bound=SQLModel)
Q = TypeVar('Q')

class Operands(str, Enum):
    eq = '=='
    neq = '!='
    gt = '>'
    gte = '>='
    lt = '<'
    lte = '<='
    in_ = 'in'
    not_in = 'not_in'
    like = 'like'
    ilike = 'ilike'


class GetListFilter(BaseModel):
    field: str
    operator: Operands
    value: Any


class GetListParams(BaseModel):
    order_field: str = 'id'
    order_by: str = 'desc'
    limit: int | None = None
    offset: int | None = None
    filters: list[GetListFilter] | None = None
    embeds: list[str] = []

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
    embeds: str | None = Query(None, deprecated='List of relationship models to embed to response')
) -> GetListParams:
    parsed_filters = None
    if filters:
        try:
            filters_data = json.loads(filters)
            parsed_filters = [GetListFilter.model_validate(item) for item in filters_data]
        except (json.JSONDecodeError, ValidationError) as ex:
            raise ValueError(f'Invalid filters JSON: {ex}') from ex

    parsed_embeds = []
    if embeds:
        try:
            embeds_data = json.loads(embeds)
            if not isinstance(embeds_data, list):
                raise ValueError('Embed data should be a list of strings')
            parsed_embeds = embeds_data
        except (json.JSONDecodeError, ValidationError, ValueError) as ex:
            raise ValueError(f'Invalid embed JSON: {ex}') from ex

    return GetListParams(
        order_field=order_field,
        order_by=order_by,
        limit=limit,
        offset=offset,
        filters=parsed_filters,
        embeds=parsed_embeds,
    )


async def create_one(db: AsyncSession, data: SQLModel):
    model_cls = type(data)
    unique_fields = [
        field
        for field, info in model_cls.model_fields.items()
        if getattr(info, 'unique', False)
    ]

    q = select(model_cls)
    for field in unique_fields:
        q = q.where(getattr(model_cls, field) == getattr(data, field))

    result = await db.exec(q)
    if result.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'{model_cls.__name__} unique constraint failed'
        )

    db.add(data)
    await db.commit()
    await db.refresh(data)
    return data


async def create_many[T: SQLModel](db: AsyncSession, data: list[T]):
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

        result = await db.exec(q)
        if result.first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'{model_cls.__name__} unique constraint failed'
            )
        
    db.add_all(data)
    await db.commit()
    for obj in data:
        await db.refresh(obj)
    return data


async def get_one[T: SQLModel](
    db: AsyncSession,
    model_cls: type[T],
    id: int,
    transform: Callable[[SelectOfScalar[T]], SelectOfScalar[T]] | None = None,
):
    q = select(model_cls).where(model_cls.id == id) # type: ignore

    if transform is not None:
        q = transform(q)

    result = await db.exec(q)
    if result := result.first():
        return result
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'{model_cls.__name__} not found'
    )


async def get_many[T: SQLModel](
    db: AsyncSession,
    model_cls: type[T],
    ids: list[int],
    transform: Callable[[SelectOfScalar[T]], SelectOfScalar[T]] | None = None,
):
    q = (
        select(model_cls)
        .where(model_cls.id.in_(ids)) # type: ignore
    )

    if transform is not None:
        q = transform(q)

    result = await db.exec(q)
    return result.all()


async def get_list[T: SQLModel](
    db: AsyncSession,
    model_cls: type[T],
    params: GetListParams,
    transform: Callable[[SelectOfScalar[T]], SelectOfScalar[T]] | None = None,
):
    q = select(model_cls)
    
    mapper = inspect(model_cls)
    relationships = [r.key for r in mapper.relationships]
    embeds = set(params.embeds) & set(relationships)
    for embed in embeds:
        if hasattr(model_cls, embed):
            q = q.options(selectinload(getattr(model_cls, embed)))

    if transform is not None:
        q = transform(q)

    if params.filters:
        for filter in params.filters:
            if filter.field not in model_cls.model_fields:
                continue
            
            column = getattr(model_cls, filter.field)
            if filter.operator == Operands.eq:
                q = q.where(column == filter.value)
            elif filter.operator == Operands.neq:
                q = q.where(column != filter.value)
            elif filter.operator == Operands.gt:
                q = q.where(column > filter.value)
            elif filter.operator == Operands.gte:
                q = q.where(column >= filter.value)
            elif filter.operator == Operands.lt:
                q = q.where(column < filter.value)
            elif filter.operator == Operands.lte:
                q = q.where(column <= filter.value)
            elif filter.operator == Operands.in_:
                if isinstance(filter.value, list) and filter.value:
                    if column := getattr(model_cls, filter.field, None):
                        q = q.where(column.in_(filter.value))
            elif filter.operator == Operands.not_in:
                if isinstance(filter.value, list) and filter.value:
                    if column := getattr(model_cls, filter.field, None):
                        q = q.where(~column.in_(filter.value))
            elif filter.operator == Operands.like:
                q = q.where(column.like(f'%{filter.value}%'))
            elif filter.operator == Operands.ilike:
                q = q.where(column.ilike(f'%{filter.value}%'))

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
    cq_result = await db.exec(cq)
    total = cq_result.first() or 0

    if params.offset is not None:
        q = q.offset(params.offset)

    if params.limit is not None:
        q = q.limit(params.limit)

    q_result = await db.exec(q)
    result = q_result.all()
    return total, result


async def update_one(
    db: AsyncSession,
    model_cls: type[T],
    id: int,
    data: BaseModel,
    transform: Callable[[SelectOfScalar[T]], SelectOfScalar[T]] | None = None,
):
    unique_fields = [
        field
        for field, info in model_cls.model_fields.items()
        if info.unique is True and info.primary_key is not True
    ]

    q = select(model_cls).where(model_cls.id == id) # type: ignore
    if transform is not None:
        q = transform(q)

    result = await db.exec(q)
    obj = result.first()
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'{model_cls.__name__} not found'
        )

    data_dict = data.model_dump(exclude_unset=True)
    for field in unique_fields:
        if field in data_dict:
            value = data_dict[field]
            q = select(model_cls).where(
                getattr(model_cls, field) == value,
                model_cls.id != id # type: ignore
            )
            result = await db.exec(q)
            if result.first():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f'{model_cls.__name__} with {field}={value} already exists',
                )

    for field in data.model_fields:
        if (value := getattr(data, field, None)) is not None:
            setattr(obj, field, value)

    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def update_many(
    db: AsyncSession,
    model_cls: type[T],
    ids: list[int],
    data_list: list[BaseModel],
    transform: Callable[[SelectOfScalar[T]], SelectOfScalar[T]] | None = None,
):
    unique_fields = [
        field
        for field, info in model_cls.model_fields.items()
        if getattr(info, 'unique', False) and info.primary_key is not True
    ]

    updated_objs = []
    for id, data in zip(ids, data_list, strict=False):
        q = select(model_cls).where(model_cls.id == id) # type: ignore
        if transform is not None:
            q = transform(q)

        result = await db.exec(q)
        obj = result.first()

        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'{model_cls.__name__} not found'
            )

        data_dict = data.model_dump(exclude_unset=True)
        for field in unique_fields:
            if field in data_dict:
                value = data_dict[field]
                q = select(model_cls).where(
                    getattr(model_cls, field) == value,
                    model_cls.id != id # type: ignore
                )
                result = await db.exec(q)
                if result.first():
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f'{model_cls.__name__} with {field}={value} already exists',
                    )
        
        for field in data.model_fields:
            if (value := getattr(data, field, None)) is not None:
                setattr(obj, field, value)

        updated_objs.append(obj)

    db.add_all(updated_objs)
    await db.commit()
    for obj in updated_objs:
        await db.refresh(obj)
    return updated_objs


async def delete_one[T: SQLModel](
    db: AsyncSession,
    model_cls: type[T],
    id: int,
    transform: Callable[[SelectOfScalar[T]], SelectOfScalar[T]] | None = None,
):
    q = select(model_cls).where(model_cls.id == id) # type: ignore
    if transform is not None:
        q = transform(q)

    result = await db.exec(q)
    obj = result.first()

    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'{model_cls.__name__} not found'
        )
    await db.delete(obj)
    await db.commit()


async def delete_many[T: SQLModel](
    db: AsyncSession,
    model_cls: type[T],
    ids: list[int],
    transform: Callable[[SelectOfScalar[T]], SelectOfScalar[T]] | None = None,
):
    for id in ids:
        q = select(model_cls).where(model_cls.id == id) # type: ignore
        if transform is not None:
            q = transform(q)

        result = await db.exec(q)
        obj = result.first()

        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'{model_cls.__name__} not found'
            )
        await db.delete(obj)
    await db.commit()
