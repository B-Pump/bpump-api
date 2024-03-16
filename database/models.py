from sqlalchemy import Column, Integer, String, JSON
from database.database import Base

class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, index=True, unique=True, nullable=False)
    password = Column(String, nullable=False)
    programs = Column(JSON, nullable=False)

class Exos(Base):
    __tablename__ = "exos"

    exo_id = Column(Integer, primary_key=True, nullable=False)
    id = Column(String, index=True, unique=True, nullable=False)
    title = Column(String, index=True, nullable=False)
    description = Column(String, index=True, nullable=False)
    category = Column(String, index=True, nullable=False)
    difficulty = Column(Integer, nullable=False)
    muscles = Column(JSON, nullable=False)
    security = Column(JSON, nullable=False)
    needed = Column(JSON, nullable=False)
    calories = Column(Integer, nullable=False)
    camera = Column(JSON, nullable=False)
    projector = Column(JSON, nullable=False)