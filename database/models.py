from sqlalchemy import Column, Integer, String, JSON
from database.database import Base

class Users(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, index=True, unique=True, nullable=False)
    password = Column(String, nullable=False)
    weight = Column(Integer, index=True, nullable=False)
    height = Column(Integer, index=True, nullable=False)
    age = Column(Integer, index=True, nullable=False)
    sex = Column(String, index=True, nullable=False)

class UsersProgs(Base):
    __tablename__ = "progs_users"

    prog_id = Column(Integer, primary_key=True, nullable=False)
    id = Column(String, index=True, nullable=False)
    owner = Column(String, index=True, nullable=False)
    icon = Column(String, nullable=False)
    title = Column(String, index=True, nullable=False)
    description = Column(String, index=True, nullable=False)
    category = Column(String, index=True, nullable=False)
    difficulty = Column(Integer, nullable=False)
    hint = Column(JSON, nullable=False)
    exercises = Column(JSON, nullable=False)

class DefaultProgs(Base):
    __tablename__ = "progs_default"

    prog_id = Column(Integer, primary_key=True, nullable=False)
    id = Column(String, index=True, nullable=False)
    icon = Column(String, nullable=False)
    title = Column(String, index=True, nullable=False)
    description = Column(String, index=True, nullable=False)
    category = Column(String, index=True, nullable=False)
    difficulty = Column(Integer, nullable=False)
    hint = Column(JSON, nullable=False)
    exercises = Column(JSON, nullable=False)

class Exos(Base):
    __tablename__ = "exos"

    exo_id = Column(Integer, primary_key=True, nullable=False)
    id = Column(String, index=True, unique=True, nullable=False)
    icon = Column(String, nullable=False)
    title = Column(String, index=True, nullable=False)
    description = Column(String, index=True, nullable=False)
    category = Column(String, index=True, nullable=False)
    difficulty = Column(Integer, nullable=False)
    video = Column(String, nullable=False)
    muscles = Column(JSON, nullable=False)
    security = Column(JSON, nullable=False)
    needed = Column(JSON, nullable=False)
    calories = Column(Integer, nullable=False)
    camera = Column(JSON, nullable=False)
    projector = Column(JSON, nullable=False)