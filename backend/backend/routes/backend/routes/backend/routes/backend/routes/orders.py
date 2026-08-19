from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Order, OrderItem, Cart, CartItem, Product, User, OrderStatus
from pydantic import BaseModel
from typing import List
from datetime import datetime

router = APIRouter()

class OrderItemSchema(BaseModel):
    product_id: int
    quantity: int
    class Config:
        from_attributes = True

class CreateOrderSchema(BaseModel):
    name: str
    phone: str
    delivery_address: str
    comment: str = None

class OrderSchema(BaseModel):
    id: int
    status: str
    total_amount: float
    name: str
    phone: str
    delivery_address: str
    created_at: datetime
    class Config:
        from_attributes = True

@router.post("", response_model=OrderSchema)
async def create_order(telegram_id: int, order_data: CreateOrderSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    cart = db.query(Cart).filter(Cart.user_id == user.id).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    total = 0
    items_data = []
    for cart_item in cart.items:
        product = db.query(Product).filter(Product.id == cart_item.product_id).first()
        if product:
            total += product.price * cart_item.quantity
            items_data.append((cart_item.product_id, cart_item.quantity, product.price))
    
    order = Order(
        user_id=user.id,
        status=OrderStatus.pending,
        total_amount=total,
        name=order_data.name,
        phone=order_data.phone,
        delivery_address=order_data.delivery_address,
        comment=order_data.comment
    )
    db.add(order)
    db.flush()
    
    for product_id, quantity, price in items_data:
        order_item = OrderItem(
            order_id=order.id,
            product_id=product_id,
            quantity=quantity,
            price_at_order=price
        )
        db.add(order_item)
    
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
    db.refresh(order)
    return order

@router.get("", response_model=List[OrderSchema])
async def get_user_orders(telegram_id: int, skip: int = Query(0), limit: int = Query(20), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    orders = db.query(Order).filter(Order.user_id == user.id).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    return orders

@router.get("/{order_id}", response_model=OrderSchema)
async def get_order(order_id: int, telegram_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user or order.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return order
