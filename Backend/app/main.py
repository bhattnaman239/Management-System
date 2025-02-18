from fastapi import FastAPI,Depends
from app.routes import auth
from app.database import Base, engine
from app import models
from app.deps import get_current_user


# Initialize DB
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include authentication routes
app.include_router(auth.router)


@app.get("/")
def home():
    return {"message": "Welcome to the HR Management System API"}

@app.get("/protected")
def protected_route(current_user: models.User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}, you are authorized to see this content."}