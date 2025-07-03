from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import UserRegistration, UserLogin, AuthSuccess
from app.schemas.error import ErrorResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=AuthSuccess,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"model": ErrorResponse, "description": "User with this username already exists"},
        400: {"model": ErrorResponse, "description": "Invalid input data"}
    },
    summary="Register a new user",
    operation_id="registerUser"
)
async def register_user(
    user_data: UserRegistration,
    db: Session = Depends(get_db)
):
    """Register a new user with username and password."""
    auth_service = AuthService(db)
    user = auth_service.register_user(user_data)
    
    # Create token for the new user
    token = auth_service.authenticate_user(user_data)
    
    return AuthSuccess(token=token)


@router.post(
    "/login",
    response_model=AuthSuccess,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"}
    },
    summary="Log in a user",
    operation_id="loginUser"
)
async def login_user(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT token."""
    auth_service = AuthService(db)
    token = auth_service.authenticate_user(user_data)
    
    return AuthSuccess(token=token)
