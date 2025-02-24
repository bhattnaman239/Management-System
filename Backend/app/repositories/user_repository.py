from sqlalchemy.orm import Session
from app import models

class UserRepository:
    @staticmethod
    def get_user_by_email(db: Session, email: str):
        return db.query(models.User).filter(models.User.email == email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        return db.query(models.User).filter(models.User.id == user_id).first()

    @staticmethod
    def get_all_users(db: Session):  
        return db.query(models.User).all()

    @staticmethod
    def create_user(db: Session, user: models.User):
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user: models.User):
        db.delete(user)
        db.commit()
