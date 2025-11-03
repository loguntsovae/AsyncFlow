from fastapi import APIRouter
from typing import List
from core.schemas import Order, OrderCreate
from core.services import ServiceClient

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=Order)
async def create_order(order: OrderCreate, token: str):
    """
    Create a new order.
    
    - Requires authentication
    - Accepts list of items and shipping address
    - Returns created order details
    """
    return await ServiceClient.forward_request("orders", "", "POST", order.dict(), token)


@router.get("", response_model=List[Order])
async def list_orders(skip: int = 0, limit: int = 10, token: str = None):
    """
    List all orders.
    
    - Requires authentication
    - Supports pagination
    - Returns list of orders
    """
    return await ServiceClient.forward_request(
        "orders", "", "GET",
        params={"skip": skip, "limit": limit},
        token=token
    )


@router.get("/{order_id}", response_model=Order)
async def get_order(order_id: int, token: str):
    """
    Get order details by ID.
    
    - Requires authentication
    - Returns order details
    """
    return await ServiceClient.forward_request("orders", str(order_id), "GET", None, token)