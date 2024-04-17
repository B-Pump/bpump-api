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
        db_user = models.Users(
            username=user_create.username,
            password=hashed_password.decode("utf-8"),
            weight=0,
            height=0,
            age=0,
            sex=""
        )

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
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to log in. Error {str(error)}")

@app.put("/edit_username", tags=["Authentification"])
async def edit_username(old_username: str, new_username: str, db: db_dependency):
    try:
        user = db.query(models.Users).filter(models.Users.username == old_username).first()
        if user:
            user.username = new_username
            db.commit()
            return {"status": True, "message": "Username updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update username. Error {str(error)}")

@app.put("/edit_password", tags=["Authentification"])
async def edit_password(username: str, old_password: str, new_password: str, db: db_dependency):
    try:
        user = db.query(models.Users).filter(models.Users.username == username).first()
        if user:
            if bcrypt.checkpw(old_password.encode("utf-8"), user.password.encode("utf-8")):
                hashed_new_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
                user.password = hashed_new_password.decode("utf-8")
                db.commit()
                return {"status": True, "message": "Password updated successfully"}
            else:
                raise HTTPException(status_code=401, detail="Invalid old password")
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update password. Error {str(error)}")

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
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete user. Error {str(error)}")
    
@app.put("/edit_weight", tags=["Metabolism"])
async def edit_weight(username: str, new_weight: int, db: db_dependency):
    try:
        user = db.query(models.Users).filter(models.Users.username == username).first()
        if user:
            user.weight = new_weight
            db.commit()
            return {"status": True, "message": "User weight updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update weight. Error {str(error)}")

@app.put("/edit_height", tags=["Metabolism"])
async def edit_height(username: str, new_height: int, db: db_dependency):
    try:
        user = db.query(models.Users).filter(models.Users.username == username).first()
        if user:
            user.height = new_height
            db.commit()
            return {"status": True, "message": "User height updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update height. Error {str(error)}")

@app.put("/edit_age", tags=["Metabolism"])
async def edit_age(username: str, new_age: int, db: db_dependency):
    try:
        user = db.query(models.Users).filter(models.Users.username == username).first()
        if user:
            user.age = new_age
            db.commit()
            return {"status": True, "message": "User age updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update age. Error {str(error)}")
    
@app.put("/edit_sex", tags=["Metabolism"])
async def edit_sex(username: str, new_sex: str, db: db_dependency):
    try:
        user = db.query(models.Users).filter(models.Users.username == username).first()
        if user:
            user.sex = new_sex
            db.commit()
            return {"status": True, "message": "User sex updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update sex. Error {str(error)}")

@app.get("/progs/{id}", tags=["Programs"])
async def read_program(id: str, username: str, db: db_dependency):
    try:
        if not db.query(models.Users).filter(models.Users.username == username).first():
            raise HTTPException(status_code=404, detail="User not found")
 
        default_progs = db.query(models.DefaultProgs).all()
        user_progs = db.query(models.UsersProgs).filter(models.UsersProgs.owner == username).all()

        if id == "all":
            return default_progs + user_progs
        elif id.startswith("default_"):
            default_prog = db.query(models.DefaultProgs).filter(models.DefaultProgs.id == id).first()
            if default_prog:
                return default_prog
            else:
                raise HTTPException(status_code=404, detail="Default program not found")
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