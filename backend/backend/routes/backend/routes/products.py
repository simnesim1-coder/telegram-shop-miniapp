from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Product, Category, ProductImage
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class ProductImageSchema(BaseModel):
    id: int
    image_url: str
    order: int
    
    class Config:
        from_attributes = True

class ProductSchema(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    category_id: Optional[int]
    in_stock: bool
    quantity: int
    is_new: bool
    is_popular: bool
    images: List[ProductImageSchema] = []
    
    class Config:
        from_attributes = True

class CategorySchema(BaseModel):
    id: int
    name: str
    slug: str
    order: int
    
    class Config:
        from_attributes = True

@router.get("", response_model=List[ProductSchema])
async def get_products(
    db: Session = Depends(get_db),
    category: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    sort: str = Query("new", regex="^(new|popular|price_asc|price_desc)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    query = db.query(Product)
    
    if category:
        query = query.filter(Product.category_id == category)
    
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    
    if sort == "popular":
        query = query.filter(Product.is_popular == True)
    elif sort == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort == "price_desc":
        query = query.order_by(Product.price.desc())
    else:
        query = query.filter(Product.is_new == True)
    
    products = query.offset(skip).limit(limit).all()
    return products

@router.get("/{product_id}", response_model=ProductSchema)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/category/list", response_model=List[CategorySchema])
async def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).order_by(Category.order).all()
    return categories

@router.get("/trending/popular", response_model=List[ProductSchema])
async def get_popular_products(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50)
):
    products = db.query(Product).filter(Product.is_popular == True).limit(limit).all()
    return products

@router.get("/trending/new", response_model=List[ProductSchema])
async def get_new_products(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50)
):
    products = db.query(Product).filter(Product.is_new == True).order_by(Product.created_at.desc()).limit(limit).all()
    return products
