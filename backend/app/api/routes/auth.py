from fastapi import APIRouter, HTTPException, status

from app.api.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserPublic
from app.services.auth_service import AuthService
from app.services.errors import AuthError, ConflictError

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register_user(payload: RegisterRequest) -> UserPublic:
    service = AuthService()
    try:
        user = service.register_user(
            email=payload.email,
            password=payload.password,
            is_admin=payload.is_admin,
        )
    except ConflictError as exception:
        raise HTTPException(status_code=409, detail=str(exception)) from exception

    return UserPublic(id=user.id, email=user.email, is_admin=user.is_admin)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    service = AuthService()
    try:
        token = service.login(email=payload.email, password=payload.password)
    except AuthError as exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exception)) from exception

    return TokenResponse(access_token=token)
