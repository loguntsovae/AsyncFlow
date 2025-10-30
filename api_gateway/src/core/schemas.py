from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


# Base Models
class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Auth Models
class UserCreate(BaseSchema):
    """User registration request model."""
    email: EmailStr
    username: str
    password: str


class Token(BaseSchema):
    """Token response model."""
    access_token: str
    token_type: str


class User(BaseSchema):
    """User response model."""
    id: int
    email: EmailStr
    username: str
    is_active: bool
    created_at: datetime


# Order Models
class OrderCreate(BaseSchema):
    """Order creation request model."""
    items: List[Dict[str, Any]]
    shipping_address: str


class Order(BaseSchema):
    """Order response model."""
    id: int
    status: str
    items: List[Dict[str, Any]]
    shipping_address: str
    created_at: datetime
    updated_at: Optional[datetime]


# Payment Models
class PaymentCreate(BaseSchema):
    """Payment creation request model."""
    order_id: int
    amount: float
    payment_method: str


class Payment(BaseSchema):
    """Payment response model."""
    id: int
    order_id: int
    amount: float
    status: str
    payment_method: str
    created_at: datetime