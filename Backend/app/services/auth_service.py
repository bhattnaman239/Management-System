from datetime import timedelta
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app import models, schemas, utils
from app.repositories.user_repository import UserRepository
from app.dependency import get_current_user
from log.logging_config import logger


class AuthService:
    @staticmethod
    def register_user(user: schemas.UserCreate, db: Session):
        user.email = user.email.lower()
        logger.info(f"[SIGNUP ATTEMPT] Username: {user.username}, Email: {user.email}")

        if user.password != user.confirm_password:
            logger.warning(f"[SIGNUP FAILED] Passwords do not match for email: {user.email}")
            raise HTTPException(
                status_code=400, detail={"success": False, "message": "Passwords do not match"}
            )

        existing_user = UserRepository.get_user_by_email(db, user.email)
        if existing_user:
            logger.warning(f"[SIGNUP FAILED] Email ({user.email}) is already registered.")
            raise HTTPException(
                status_code=400, detail={"success": False, "message": "Email is already registered"}
            )

        hashed_password = utils.hash_password(user.password)
        new_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)

        try:
            created_user = UserRepository.create_user(db, new_user)
            logger.info(f"[SIGNUP SUCCESS] User {created_user.username} (ID: {created_user.id}) registered successfully.")
            return created_user
        except Exception as e:
            logger.error(f"[SIGNUP ERROR] Unexpected error during signup: {e}")
            raise HTTPException(
                status_code=500, detail={"success": False, "message": f"Unexpected error: {str(e)}"}
            )

    @staticmethod
    def authenticate_user(email: str, password: str, db: Session):
        email = email.lower()
        logger.info(f"[LOGIN ATTEMPT] Email: {email}")

        user = UserRepository.get_user_by_email(db, email)

        if not user or not utils.verify_password(password, user.hashed_password):
            logger.warning(f"[LOGIN FAILED] Incorrect credentials for email: {email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail={"success": False, "message": "Incorrect username or password"}
            )

        logger.info(f"[LOGIN SUCCESS] User {user.username} (ID: {user.id}) authenticated successfully.")
        return user

    @staticmethod
    def get_user_by_id(user_id: int, db: Session):
        logger.info(f"[GET USER ATTEMPT] Fetching user with ID: {user_id}")
        
        user = UserRepository.get_user_by_id(db, user_id)
        if not user:
            logger.warning(f"[GET USER FAILED] User with ID {user_id} not found.")
            raise HTTPException(
                status_code=404, detail={"success": False, "message": "User not found"}
            )

        logger.info(f"[GET USER SUCCESS] Retrieved user {user.username} (ID: {user.id}).")
        return schemas.UserResponse.from_orm(user)

    @staticmethod
    def get_all_users(db: Session):
        logger.info(f"[GET ALL USERS ATTEMPT] Retrieving all users.")

        users = UserRepository.get_all_users(db)
        logger.info(f"[GET ALL USERS SUCCESS] Retrieved {len(users)} users.")
        return [schemas.UserResponse.from_orm(user) for user in users]

    @staticmethod
    def delete_user(user_id: int, db: Session):
        logger.info(f"[DELETE USER ATTEMPT] Deleting user with ID: {user_id}")

        user = UserRepository.get_user_by_id(db, user_id)
        if not user:
            logger.warning(f"[DELETE USER FAILED] User with ID {user_id} not found.")
            raise HTTPException(
                status_code=404, detail={"success": False, "message": "User not found"}
            )

        UserRepository.delete_user(db, user)
        logger.info(f"[DELETE USER SUCCESS] User {user.username} (ID: {user.id}) deleted successfully.")

        return JSONResponse(status_code=200, content={"success": True, "message": "User deleted successfully."})
