# app/models.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    gender = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    phone = Column(String)
    email = Column(String)
    location = Column(String)
    photo_url = Column(String) 

    @staticmethod
    def from_api_data(user: dict) -> "User":
        return User(
            gender=user["gender"],
            first_name=user["name"]["first"],
            last_name=user["name"]["last"],
            email=user["email"],
            phone=user["phone"],
            location=f"{user['location']['city']}, {user['location']['country']}",
            photo_url=user["picture"]["thumbnail"],
        )