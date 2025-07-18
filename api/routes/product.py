# Generated code for Product model

from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlmodel import Session, select, asc, desc
import typing
import json

from database import get_db
from models.user import User
from models.product import Product
from .auth import get_current_user
from utils import uploadutil

router = APIRouter()


class ActionResponse(BaseModel):
    success: bool
    message: str


class ProductCreate(BaseModel):
    name: str
    description: str
    image: str
    created_at: datetime = None
    updated_at: datetime = None
    

class ProductResponse(BaseModel):
    id: int | None = None
    name: str
    description: str = None
    image: str = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    

class ProductUpdate(BaseModel):
    name: str = None
    description: str = None
    image: str = None
    created_at: datetime = None
    updated_at: datetime = None
    

@router.post('/products', response_model=ProductResponse, tags=['Product'])
def create_product(
    data: ProductCreate,
	current_user: typing.Annotated[User, Depends(get_current_user)],   
    db: Session = Depends(get_db)
):
    try:
        if db.exec(select(Product).where(Product.name == data.name)).first():
            raise HTTPException(
                status_code=400,
                detail=f'Product with name of {data.name} already exists'
            )
        
        path = uploadutil.save_base64_image(data.image, data.name, 'static/uploads')
        converted_data = data.model_dump()
        converted_data['image'] = path
        product = Product(**converted_data)
        db.add(product)
        db.commit()
        return product
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/products', response_model=typing.List[ProductResponse], tags=['Product'])
def get_products(
	current_user: typing.Annotated[User, Depends(get_current_user)],  
    order_field: str = 'id', 
    order_by: str = 'desc', 
    limit: int = None, 
    offset: int = None, 
    filters: str = None, 
    db: Session = Depends(get_db)
):
    try:
        query = select(Product)
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
                if key not in Product.model_fields:
                    continue
                column = getattr(Product, key)
                query = query.where(column == value)
        if order_field is not None:
            if order_field not in Product.model_fields:
                raise HTTPException(
                    status_code=400,
                    detail=f'{order_field} is not a valid field'
                )
            if order_by == 'asc':
                query = query.order_by(asc(getattr(Product, order_field)))
            else:
                query = query.order_by(desc(getattr(Product, order_field)))
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)
        products = db.exec(query).all()
        return products
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/products/{id}', response_model=ProductResponse, tags=['Product'])
def get_product(
	current_user: typing.Annotated[User, Depends(get_current_user)],  
    id: int, 
    db: Session = Depends(get_db)
):
    try:
        query = select(Product).where(Product.id == id)
        product = db.exec(query).first()
        if not product:
            raise HTTPException(status_code=404, detail='Product not found')
        return product
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch('/products/{id}', response_model=ProductResponse, tags=['Product'])
def update_product(
    id: int, 
    data: ProductUpdate,
	current_user: typing.Annotated[User, Depends(get_current_user)],  
    db: Session = Depends(get_db)
):
    try:
        query = select(Product).where(Product.id == id)
        product = db.exec(query).first()
        if not product:
            raise HTTPException(
                status_code=404,
                detail='Product not found'
            )
            
        if db.exec(select(Product).where(Product.name == data.name).where(Product.id != product.id)).first():
            raise HTTPException(
                status_code=400,
                detail=f'Product with name of {data.name} already exists'
            )
            
        path = uploadutil.save_base64_image(data.image, data.name, 'static/uploads')
        data_dict = data.model_dump()
        data_dict['image'] = path
        for field in data_dict:
            if hasattr(product, field) and data_dict[field]:
                setattr(product, field, data_dict[field])
        
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete('/products/{id}', response_model=ActionResponse, tags=['Product'])
def delete_product(
    id: int,
	current_user: typing.Annotated[User, Depends(get_current_user)],  
    db: Session = Depends(get_db)
):
    try:
        query = select(Product).where(Product.id == id)
        product = db.exec(query).first()
        if not product:
            raise HTTPException(status_code=404, detail='Product not found')
        db.delete(product)
        db.commit()
        return ActionResponse(
            success=True,
            message=f'Product deleted successfully'
        )
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
