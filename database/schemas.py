from pydantic import BaseModel
from typing import List

class UserBase(BaseModel):
    username: str
    password: str

class MetabolismBase(BaseModel):
    weight: int
    height: int
    age: int
    sex: str

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
    rest: List[int]

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
    camera: List[dict]
    projector: List[dict]