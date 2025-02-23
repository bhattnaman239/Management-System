from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import timedelta
from app.database import get_db
from app import models, schemas, utils

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")  # ✅ Fixed leading "/"

@router.post("/register", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Ensure email is lowercase for consistent lookup
    user.email = user.email.lower()

    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Check if the email or username already exists
    existing_user = db.query(models.User).filter(
        (models.User.email == user.email) | (models.User.username == user.username)
    ).first()
    
    if existing_user:
        if existing_user.email == user.email:
            raise HTTPException(status_code=400, detail="Email is already registered")
        if existing_user.username == user.username:
            raise HTTPException(status_code=400, detail="Username is already taken")

    # Hash the password and create a new user
    hashed_password = utils.hash_password(user.password)
    new_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="A user with this email or username already exists")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    return new_user

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # ✅ Ensure email lookup is case-insensitive
    email_input = form_data.username.lower()

    print(f"🔍 Login Attempt: {email_input}")  # Debugging

    user = db.query(models.User).filter(models.User.email == email_input).first()

    if not user:
        print("❌ User not found in database")  # Debugging
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )

    print(f"✅ Found user: {user.username}")  # Debugging

    if not utils.verify_password(form_data.password, user.hashed_password):
        print("❌ Password does not match")  # Debugging
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )

    # ✅ Generate access token
    access_token = utils.create_access_token(
        data={"sub": user.email}, 
        expires_delta=timedelta(minutes=30)
    )

    print("✅ Login successful, token generated")  # Debugging

    return {"access_token": access_token, "token_type": "bearer"}

# Get all users
@router.get("/users", response_model=list[schemas.UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users
