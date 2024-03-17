from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
import bcrypt
import database.models as models
import database.schemas as schemas
from database.database import engine, SessionLocal
from sqlalchemy.orm import Session

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
        if db.query(models.Users).filter(models.Users.username == user_create.username).first():
            raise HTTPException(status_code=400, detail="This user already exists")
        
        hashed_password = bcrypt.hashpw(user_create.password.encode("utf-8"), bcrypt.gensalt())
        default_programs = [ # The two default programs
            models.Progs(
                owner=user_create.username,
                id="cardio-intense",
                title="Cardio Intense",
                description="Un programme intense axé sur le renforcement cardiovasculaire.",
                category="Cardio",
                difficulty=4,
                hint=["Restez hydraté pendant l'entraînement.", "Écoutez votre corps et ajustez l'intensité si nécessaire."],
                exercises=["burpees", "jumpingjacks"]
            ),
            models.Progs(
                owner=user_create.username,
                id="renfo-corps",
                title="Renfo du corps",
                description="Un programme axé sur le renforcement des muscles du haut du corps.",
                category="Haut du corps",
                difficulty=3,
                hint=["Assurez-vous de maintenir une bonne forme tout au long de l'exercice.", "Écoutez votre corps et ajustez l'intensité si nécessaire."],
                exercises=["chinups", "dips"]
            )
        ]
        
        db_user = models.Users(username=user_create.username, password=hashed_password.decode("utf-8"))

        db.add_all(default_programs)

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return {"status": True, "message": "User registered successfully"}
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to register user. Error {str(error)}")
    
@app.post("/delete")
async def delete(username: str, db: db_dependency):
    try:
        user = db.query(models.Users).filter(models.Users.username == username).first()
        if user:
            db.query(models.Progs).filter(models.Progs.owner == username).delete()
            db.delete(user)
            db.commit()
            return {"status": True, "message": "User and associated data deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Failed to delete user. Error {str(error)}")

@app.post("/login")
async def login(user_create: schemas.UserBase, db: db_dependency):
    try:
        user = db.query(models.Users).filter(models.Users.username == user_create.username).first()

        if user and bcrypt.checkpw(user_create.password.encode("utf-8"), user.password.encode("utf-8")):
            return {"status": True, "message": "User logged in successfully"}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Failed to log in. Error {str(error)}")
    
@app.post("/add_program")
async def add_program(username: str, program: schemas.ProgramBase, db: db_dependency):
    try:
        if db.query(models.Users).filter(models.Users.username == username).first():
            new_program = models.Progs(
                id=program.title.lower().replace(" ", "-"),
                owner=username,
                title=program.title,
                description=program.description,
                category=program.category,
                difficulty=program.difficulty,
                hint=program.hint,
                exercises=program.exercises
            )

            db.add(new_program)
            db.commit()

            return {"status": True, "message": "Program added successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to add program. Error {str(error)}")
    
@app.post("/remove_program")
async def remove_program(username: str, id: str, db: db_dependency):
    try:
        if db.query(models.Users).filter(models.Users.username == username).first():
            program = db.query(models.Progs).filter(models.Progs.id == id).first()
            if program:
                db.delete(program)
                db.commit()

                return {"status": True, "message": "Program removed successfully"}
            else:
                raise HTTPException(status_code=404, detail="Program not found")
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to remove program. Error {str(error)}")

@app.post("/add_exercise")
async def add_exercise(exercise: schemas.ExerciseBase, db: db_dependency):
    try:
        if db.query(models.Exos).filter(models.Exos.id == exercise.id).first():
            raise HTTPException(status_code=400, detail="An exercise with this ID already exists")

        db.add(models.Exos(**exercise.model_dump()))
        db.commit()

        return {"status": True, "message": "The exercise was added successfully"}
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to add exercise. Error {str(error)}")

@app.get("/progs/{id}")
async def read_program(id: str, username: str, db: db_dependency):
    try:
        if not db.query(models.Users).filter(models.Users.username == username).first():
            raise HTTPException(status_code=404, detail="User not found")

        if id == "all":
            return db.query(models.Progs).filter(models.Progs.owner == username).all()
        else:
            program = db.query(models.Progs).filter(models.Progs.owner == username, models.Progs.id == id).first()
            if program:
                return program
            else:
                raise HTTPException(status_code=404, detail="Program not found")
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error while reading programs. Error {str(error)}")

@app.get("/exos/{id}")
async def read_exercise(id: str, db: db_dependency):
    try:
        if id == "all":
            return db.query(models.Exos).all()
        else:
            exercise = db.query(models.Exos).filter(models.Exos.id == id).first()
            if exercise:
                return exercise
            else:
                raise HTTPException(status_code=404, detail="Exercise not found")
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error while reading exercises. Error {str(error)}")