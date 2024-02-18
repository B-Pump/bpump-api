from pydantic import BaseModel
from typing import List

class UserBase(BaseModel):
    username: str
    password: str

class ProgramBase(BaseModel):
    id: str
    title: str
    description: str
    category: str
    difficulty: int
    hint: List[str]
    exercises: List[str]

class EnergeticInfo(BaseModel):
    calories: int

class SugarInfo(BaseModel):
    title: str
    description: str
    category: str
    difficulty: int
    muscles: List[str]
    security: List[str]
    needed: List[str]
    energetic: EnergeticInfo

class ExerciseBase(BaseModel):
    id: str
    sugar: SugarInfo
    cameraTargets: dict
    projectorTargets: List[dict]