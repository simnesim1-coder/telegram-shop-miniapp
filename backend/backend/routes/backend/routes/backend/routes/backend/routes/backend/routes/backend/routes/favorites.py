from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Favorite, User, Product
from pydantic import BaseModel
from typing import List

router = APIRouter()

class FavoriteSchema(BaseModel):
    id: int
    product_id: int
    class Config:
        from_attributes = True

@router.get("", response_model=List[FavoriteSchema])
async def get_favorites(telegram_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    favorites = db.query(Favorite).filter(Favorite.user_id == user.id).all()
    return favorites

@router.post("/{product_id}")
async def add_favorite(product_id: int, telegram_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    existing = db.query(Favorite).filter(Favorite.user_id == user.id, Favorite.product_id == product_id).first()
    if existing:
        return {"status": "ok", "message": "Already in favorites"}
    
    favorite = Favorite(user_id=user.id, product_id=product_id)
    db.add(favorite)
    db.commit()
    return {"status": "ok", "message": "Added to favorites"}

@router.delete("/{product_id}")
async def remove_favorite(product_id: int, telegram_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    favorite = db.query(Favorite).filter(Favorite.user_id == user.id, Favorite.product_id == product_id).first()
    if not favorite:
        raise HTTPException(status_code=404, detail="Not in favorites")
    
    db.delete(favorite)
    db.commit()
    return {"status": "ok"}
