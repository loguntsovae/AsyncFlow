from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime


# Auth Models
class UserCreate(BaseModel):
    """User registration request model."""
    email: EmailStr
    username: str
    password: str


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str


class User(BaseModel):
    """User response model."""
    id: int
    email: EmailStr
    username: str
    is_active: bool
    created_at: datetime


# Order Models
class OrderCreate(BaseModel):
    """Order creation request model."""
    items: List[Dict[str, Any]]
    shipping_address: str


class Order(BaseModel):
    """Order response model."""
    id: int
    status: str
    items: List[Dict[str, Any]]
    shipping_address: str
    created_at: datetime
    updated_at: Optional[datetime]


# Payment Models
class PaymentCreate(BaseModel):
    """Payment creation request model."""
    order_id: int
    amount: float
    payment_method: str


class Payment(BaseModel):
    """Payment response model."""
    id: int
    order_id: int
    amount: float
    status: str
    payment_method: str
    created_at: datetime