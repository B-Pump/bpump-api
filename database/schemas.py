from pydantic import BaseModel
from typing import List

class UserBase(BaseModel):
    username: str
    password: str

class ProgramBase(BaseModel):
    id: str
    owner: str
    icon: str
    title: str
    description: str
    category: str
    difficulty: int
    hint: List[str]
    exercises: List[str]

class ExerciseBase(BaseModel):
    id: str
    icon: str
    title: str
    description: str
    category: str
    difficulty: int
    video: str
    muscles: List[str]
    security: List[str]
    needed: List[str]
    calories: int
    camera: dict
    projector: List[dict]