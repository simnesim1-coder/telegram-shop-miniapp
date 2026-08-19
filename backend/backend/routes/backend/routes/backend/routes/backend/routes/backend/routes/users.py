from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Address
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class AddressSchema(BaseModel):
    id: int
    address: str
    is_default: bool
    class Config:
        from_attributes = True

class UserSchema(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    is_admin: bool
    addresses: List[AddressSchema] = []
    class Config:
        from_attributes = True

class UpdateUserSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None

class CreateAddressSchema(BaseModel):
    address: str
    is_default: bool = False

@router.get("/profile", response_model=UserSchema)
async def get_profile(telegram_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/profile")
async def update_profile(telegram_id: int, data: UpdateUserSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if data.first_name:
        user.first_name = data.first_name
    if data.last_name:
        user.last_name = data.last_name
    if data.phone:
        user.phone = data.phone
    
    db.commit()
    return {"status": "ok"}

@router.get("/addresses", response_model=List[AddressSchema])
async def get_addresses(telegram_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return db.query(Address).filter(Address.user_id == user.id).all()

@router.post("/addresses")
async def create_address(telegram_id: int, data: CreateAddressSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if data.is_default:
        db.query(Address).filter(Address.user_id == user.id).update({"is_default": False})
    
    address = Address(user_id=user.id, address=data.address, is_default=data.is_default)
    db.add(address)
    db.commit()
    return {"status": "ok", "id": address.id}
