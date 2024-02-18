from sqlalchemy import Column, Integer, String, JSON
from database.database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    password = Column(String, index=True)
    programs = Column(JSON)