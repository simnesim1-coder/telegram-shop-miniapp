from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Cart, CartItem, Product, User
from pydantic import BaseModel
from typing import List

router = APIRouter()

class CartItemSchema(BaseModel):
    id: int
    product_id: int
    quantity: int
    class Config:
        from_attributes = True

class CartSchema(BaseModel):
    id: int
    items: List[CartItemSchema] = []
    class Config:
        from_attributes = True

@router.get("", response_model=CartSchema)
async def get_cart(telegram_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    cart = db.query(Cart).filter(Cart.user_id == user.id).first()
    if not cart:
        cart = Cart(user_id=user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart

@router.post("")
async def add_to_cart(telegram_id: int, product_id: int, quantity: int = 1, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    cart = db.query(Cart).filter(Cart.user_id == user.id).first()
    if not cart:
        cart = Cart(user_id=user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    
    cart_item = db.query(CartItem).filter(CartItem.cart_id == cart.id, CartItem.product_id == product_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        db.add(cart_item)
    db.commit()
    return {"status": "ok", "message": "Added to cart"}

@router.put("/items/{item_id}")
async def update_cart_item(item_id: int, quantity: int, db: Session = Depends(get_db)):
    cart_item = db.query(CartItem).filter(CartItem.id == item_id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    if quantity <= 0:
        db.delete(cart_item)
    else:
        cart_item.quantity = quantity
    db.commit()
    return {"status": "ok"}

@router.delete("/items/{item_id}")
async def delete_cart_item(item_id: int, db: Session = Depends(get_db)):
    cart_item = db.query(CartItem).filter(CartItem.id == item_id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db.delete(cart_item)
    db.commit()
    return {"status": "ok"}

@router.delete("")
async def clear_cart(telegram_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    cart = db.query(Cart).filter(Cart.user_id == user.id).first()
    if cart:
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        db.commit()
    return {"status": "ok"}
