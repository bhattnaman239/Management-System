from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from log.logging_config import logger

from app import models
from app.database import Base, engine
from app.dependency import get_current_user
from app.routes import auth
from app.models import User

logger.info("Imported modules successfully.")
Base.metadata.create_all(bind=engine)
logger.info("Database initialized successfully.")  

app = FastAPI()
logger.info("FastAPI application started.")  

app.include_router(auth.router)
logger.info("Authentication routes included.")  

@app.get("/")
def home():
    try:
        logger.info("[HOME ENDPOINT] Accessed successfully.")
        response_data = {"message": "Welcome to the HR Management System API"}
        return JSONResponse(content=response_data, status_code=200)
    except Exception as e:
        logger.error(f"[HOME ENDPOINT ERROR] Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/protected")
def protected_route(current_user: User = Depends(get_current_user)):
    logger.info(f"Protected route accessed by {current_user.username}.") 
    return {"message": f"Hello {current_user.username}, you are authorized to see this content."}
