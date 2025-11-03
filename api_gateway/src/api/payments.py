from fastapi import APIRouter
from core.schemas import Payment, PaymentCreate
from core.services import ServiceClient

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("", response_model=Payment)
async def create_payment(payment: PaymentCreate, token: str):
    """
    Create a new payment.
    
    - Requires authentication
    - Processes payment for an order
    - Returns payment details
    """
    return await ServiceClient.forward_request("billing", "payments", "POST", payment.dict(), token)


@router.get("/{payment_id}", response_model=Payment)
async def get_payment(payment_id: int, token: str):
    """
    Get payment details by ID.
    
    - Requires authentication
    - Returns payment information
    """
    return await ServiceClient.forward_request("billing", f"payments/{payment_id}", "GET", None, token)