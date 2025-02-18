# from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from sqlalchemy.orm import Session
# from app.database import get_db
# from app import models,schemas, utils
# from datetime import timedelta



# router = APIRouter(prefix="/auth", tags=["Authentication"])
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# @router.post("/register", response_model=schemas.UserResponse)
# def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     if user.password != user.confirm_password:
#         raise HTTPException(status_code=400, detail="Passwords do not match")
    
#     db_user = db.query(models.User).filter(models.User.email == user.email).first()
#     if db_user:
#         raise HTTPException(status_code=400, detail="User already registered")
    
#     hashed_password = utils.hash_password(user.password)
#     new_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return new_user


# @router.post("/login")
# def login(
#     form_data: OAuth2PasswordRequestForm = Depends(),
#     db: Session = Depends(get_db)
# ):
#     user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
#     if not user or not utils.verify_password(form_data.password, user.hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Incorrect username or password"
#         )

#     access_token = utils.create_access_token(
#         data={"sub": user.email}, 
#         expires_delta=timedelta(minutes=30)  # Token expires in 30 min
#     )

#     return {"access_token": access_token, "token_type": "bearer"}
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app import models, schemas, utils

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/register", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    
    hashed_password = utils.hash_password(user.password)
    new_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    if not user or not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )

    access_token = utils.create_access_token(
        data={"sub": user.email}, 
        expires_delta=timedelta(minutes=30)
    )

    return {"access_token": access_token, "token_type": "bearer"}
