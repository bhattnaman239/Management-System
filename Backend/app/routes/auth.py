from datetime import timedelta
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from log.logging_config import logger
from app import schemas, utils
from app.database import get_db
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/register")
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    new_user = AuthService.register_user(user, db)
    return JSONResponse(
        status_code=201,
        content={"success": True, "message": "User registered successfully.", "data": {"id": new_user.id,"username": new_user.username, "email": new_user.email}},
    )


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = AuthService.authenticate_user(form_data.username, form_data.password, db)
    access_token = utils.create_access_token(
        data={"sub": user.email}, expires_delta=timedelta(minutes=30)
    )

    return JSONResponse(
        status_code=200,
        content={"success": True, "message": "Login successful", "data": {"access_token": access_token, "token_type": "bearer"}},
    )


@router.get("/users")
def get_all_users(db: Session = Depends(get_db)):
    users = AuthService.get_all_users(db)
    users_data = [user.model_dump() for user in users]
    return JSONResponse(
        status_code=200,
        content={"success": True, "message": "Users retrieved successfully.", "data": users_data},
    )


@router.get("/users/{user_id}")
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = AuthService.get_user_by_id(user_id, db)
    return JSONResponse(
        status_code=200,
        content={"success": True, "message": "User retrieved successfully.", "data": user.model_dump()},
    )


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    result = AuthService.delete_user(user_id, db)
    return JSONResponse(
        status_code=200,
        content={"success": True, "message": "User deleted successfully."},
    )
