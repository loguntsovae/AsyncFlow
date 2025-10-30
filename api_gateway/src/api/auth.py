from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from core.schemas import User, UserCreate, Token
from core.services import ServiceClient

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=User)
async def register(user_data: UserCreate):
    """
    Register a new user.
    
    - Requires email, username, and password
    - Returns created user information
    """
    return await ServiceClient.forward_request("auth", "register", "POST", user_data.dict())


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login to get access token.
    
    - Requires username and password
    - Returns JWT access token
    """
    return await ServiceClient.forward_request(
        "auth", "token", "POST",
        {"username": form_data.username, "password": form_data.password}
    )


@router.get("/me", response_model=User)
async def get_user_me(token: str):
    """
    Get current user information.
    
    - Requires authentication
    - Returns user profile
    """
    return await ServiceClient.forward_request("auth", "me", "GET", None, token)