from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
import bcrypt
import database.models as models
import database.schemas as schemas
from database.database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI(title="B-Pump API", docs_url="/")
models.Base.metadata.create_all(bind=engine)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.post("/register", tags=["Authentification"])
async def register(user_create: schemas.UserBase, db: db_dependency):
    try:
        if db.query(models.Users).filter(models.Users.username == user_create.username).first():
            raise HTTPException(status_code=400, detail="This user already exists")
        
        hashed_password = bcrypt.hashpw(user_create.password.encode("utf-8"), bcrypt.gensalt())
        default_programs = [ # The two default programs
            models.DefaultProgs(
                id="default_1",
                icon="https://i.imgur.com/IRVJqkw.jpeg",
                title="Bas du Corps Explosif",
                description="Ce programme est conçu pour renforcer et tonifier les muscles des jambes et des fesses en utilisant des exercices explosifs.",
                category="Bas du corps",
                difficulty=4,
                hint=["Assure-toi de bien respirer pendant les exercices et concentre-toi sur la forme pour éviter les blessures.", "Écoutez votre corps et ajustez l'intensité si nécessaire."],
                exercises=["squats", "lunges", "deadlift", "jumpingjacks"]
            ),
            models.DefaultProgs(
                id="default_2",
                icon="https://i.imgur.com/BzzXIim.jpeg",
                title="Cardio HIIT",
                description="Cet entraînement cardiovasculaire haute intensité (HIIT) est parfait pour brûler des calories et améliorer ta condition physique globale.",
                category="Cardio",
                difficulty=3,
                hint=["Faites attention à votre respiration et gardez un rythme soutenu tout au long de l'entraînement.", "Écoutez votre corps et ajustez l'intensité si nécessaire."],
                exercises=["burpees", "jumpingjacks", "squats", "plank"]
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
    
@app.post("/login", tags=["Authentification"])
async def login(user_create: schemas.UserBase, db: db_dependency):
    try:
        user = db.query(models.Users).filter(models.Users.username == user_create.username).first()

        if user and bcrypt.checkpw(user_create.password.encode("utf-8"), user.password.encode("utf-8")):
            return {"status": True, "message": "User logged in successfully"}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Failed to log in. Error {str(error)}")
    
@app.delete("/delete", tags=["Authentification"])
async def delete(username: str, db: db_dependency):
    try:
        user = db.query(models.Users).filter(models.Users.username == username).first()
        if user:
            db.query(models.UsersProgs).filter(models.UsersProgs.owner == username).delete()
            db.delete(user)
            db.commit()
            return {"status": True, "message": "User and associated data deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Failed to delete user. Error {str(error)}")
    
@app.get("/progs/{id}", tags=["Programs"])
async def read_program(id: str, username: str, db: db_dependency):
    try:
        if not db.query(models.Users).filter(models.Users.username == username).first():
            raise HTTPException(status_code=404, detail="User not found")
 
        default_progs = db.query(models.DefaultProgs).all()
        user_progs = db.query(models.UsersProgs).filter(models.UsersProgs.owner == username).all()

        if id == "all":
            return default_progs + user_progs
        else:
            program = db.query(models.UsersProgs).filter(models.UsersProgs.owner == username, models.UsersProgs.id == id).first()
            if program:
                return program
            else:
                raise HTTPException(status_code=404, detail="Program not found")
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error while reading programs. Error {str(error)}")
    
@app.post("/add_program", tags=["Programs"])
async def add_program(username: str, program: schemas.ProgramBase, db: db_dependency):
    try:
        if db.query(models.Users).filter(models.Users.username == username).first():
            new_program = models.UsersProgs(
                id=program.title.lower().replace(" ", "-"),
                owner=username,
                icon=program.icon,
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
    
@app.put("/edit_program", tags=["Programs"])
async def edit_program(username: str, program: schemas.ProgramBase, db: db_dependency):
    try:
        existing_program = db.query(models.UsersProgs).filter(models.UsersProgs.owner == username, models.UsersProgs.id == program.id).first()
        if existing_program:
            existing_program.icon = program.icon
            existing_program.title = program.title
            existing_program.description = program.description
            existing_program.category = program.category
            existing_program.difficulty = program.difficulty
            existing_program.hint = program.hint
            existing_program.exercises = program.exercises

            db.commit()
            return {"status": True, "message": "Program updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Program not found or does not belong to the user")
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update program. Error {str(error)}")
    
@app.delete("/remove_program", tags=["Programs"])
async def remove_program(username: str, id: str, db: db_dependency):
    try:
        if db.query(models.Users).filter(models.Users.username == username).first():
            program = db.query(models.UsersProgs).filter(models.UsersProgs.id == id).first()
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

@app.get("/exos/{id}", tags=["Exercises"])
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

@app.post("/add_exercise", tags=["Exercises"])
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
    
@app.put("/edit_exercise", tags=["Exercises"])
async def edit_exercise(exercise: schemas.ExerciseBase, db: db_dependency):
    try:
        existing_exercise = db.query(models.Exos).filter(models.Exos.id == exercise.id).first()
        if existing_exercise:
            existing_exercise.icon = exercise.icon
            existing_exercise.title = exercise.title
            existing_exercise.description = exercise.description
            existing_exercise.category = exercise.category
            existing_exercise.difficulty = exercise.difficulty
            existing_exercise.video = exercise.video
            existing_exercise.muscles = exercise.muscles
            existing_exercise.security = exercise.security
            existing_exercise.needed = exercise.needed
            existing_exercise.calories = exercise.calories
            existing_exercise.camera = exercise.camera
            existing_exercise.projector = exercise.projector

            db.commit()
            return {"status": True, "message": "Exercise updated successfully"}
        else:
            raise HTTPException(status_code=400, detail="Exercise not found")
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update exercise. Error {str(error)}")
    
@app.delete("/remove_exercise", tags=["Exercises"])
async def remove_exercise(id: str, db: db_dependency):
    try:
        exercise = db.query(models.Exos).filter(models.Exos.id == id).first()
        if exercise:
            db.delete(exercise)
            db.commit()

            return {"status": True, "message": "Exercise removed successfully"}
        else:
            raise HTTPException(status_code=404, detail="Exercise not found")
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to remove Exercise. Error {str(error)}")