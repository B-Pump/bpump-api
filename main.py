from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
import json
import bcrypt
import database.models as models
import database.schemas as schemas
from database.database import engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

app = FastAPI()
models.Base.metadata.create_all(bind=engine)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/")
def root():
    return "Welcome to the B-Pump api !"

@app.post("/register")
async def register(user_create: schemas.UserBase, db: db_dependency):
    try:
        hashed_password = bcrypt.hashpw(user_create.password.encode("utf-8"), bcrypt.gensalt())
        default_programs = [
            {
                "id": "cardio-intense",
                "title": "Cardio Intense",
                "description": "Un programme intense axé sur le renforcement cardiovasculaire.",
                "category": "Cardio",
                "difficulty": 4,
                "hint": ["Restez hydraté pendant l'entraînement.", "Écoutez votre corps et ajustez l'intensité si nécessaire."],
                "exercises": ["burpees", "jumpingjacks"],
            },
            {
                "id": "renfo-corps",
                "title": "Renfo du corps",
                "description": "Un programme axé sur le renforcement des muscles du haut du corps.",
                "category": "Haut du corps",
                "difficulty": 3,
                "hint": ["Assurez-vous de maintenir une bonne forme tout au long de l'exercice.", "Écoutez votre corps et ajustez l'intensité si nécessaire."],
                "exercises": ["chinups", "dips"],
            },
        ]
        
        db_user = models.User(username=user_create.username, password=hashed_password.decode("utf-8"), programs=default_programs)

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return {"message": "User registered successfully"}
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Username '{user_create.username}' already exists.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to register user. Error: {str(e)}")

@app.post("/login")
async def login(username: str, password: str, db: db_dependency):
    try:
        user = db.query(models.User).filter(models.User.username == username).first()

        if user and bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
            return {"message": "User logged in successfully"}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log in. Error: {str(e)}")

@app.post("/add_program/{username}")
async def add_program(username: str, program: schemas.ProgramBase, db: db_dependency):
    try:
        db_user = db.query(models.User).filter(models.User.username == username).first()

        if db_user:
            program_dict = {
                "id": program.title.lower().replace(" ", "-"),
                "title": program.title,
                "description": program.description,
                "category": program.category,
                "difficulty": program.difficulty,
                "hint": program.hint,
                "exercises": program.exercises
            }

            db_user.programs = db_user.programs + [program_dict]
            db.commit()
            
            return {"message": "Program added successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to add program. Error: {str(e)}")
    
@app.post("/add_exercise")
async def add_exercise(exercise: schemas.ExerciseBase):
    try:
        with open("./data/exercises.json", "r") as file:
            exercises = json.load(file)

        if any(item["id"] == exercise.id for item in exercises):
            raise HTTPException(status_code=400, detail="An exercise with this ID already exists")

        exercises.append(exercise.dict())

        with open("./data/exercises.json", "w") as file:
            json.dump(exercises, file, indent=2)

        return {"message": "The exercise was added successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error creating exercise")
    
@app.get("/progs/{id}/{username}")
async def read_program(id: str, username: str, db: db_dependency):
    try:
        db_user = db.query(models.User).filter(models.User.username == username).first()
        if id == "all":
            if db_user:
                return db_user.programs or []
            else:
                raise HTTPException(status_code=404, detail="User not found")
        else:
            if db_user and db_user.programs:
                program = next((p for p in db_user.programs if p.get("id") == id), None)
                
                if program:
                    return program
                else:
                    raise HTTPException(status_code=404, detail=f"Program with id '{id}' not found")
            else:
                raise HTTPException(status_code=404, detail="User or programs not found")
    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error while reading programs")


@app.get("/exos/{id}")
async def read_exercise(id: str):
    try:
        if id == "all":
            with open("./data/exercises.json", "r") as file:
                return json.load(file)
        else:
            with open("./data/exercises.json", "r") as file:
                exercises = json.load(file)
                exercise = next((item for item in exercises if item["id"] == id), None)
                if exercise:
                    return exercise
                else:
                    raise HTTPException(status_code=404, detail="Exercise not found")
    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error while reading exercises")