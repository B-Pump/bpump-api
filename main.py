from fastapi import FastAPI, HTTPException, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from utils import get_user_file_path, load_user_data, save_user_data
import os
import bcrypt
import json

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def root():
    return "Welcome to the B-Pump api !"

class User(BaseModel):
    username: str
    password: str

class Program(BaseModel):
    title: str
    description: str
    exercises: list

@app.post("/register")
async def register(user: User):
    try:
        file_path = get_user_file_path(user.username)
        if os.path.exists(file_path):
            raise HTTPException(status_code=400, detail="Username already exists")
        else:
            hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
            new_user = {
                "username": user.username, 
                "password": hashed_password.decode("utf-8"), 
                "progs": [ # Two default programs 
                    {
                        "id": "cardio-intense",
                        "title": "Cardio Intense",
                        "description": "Un programme intense ax\u00e9 sur le renforcement cardiovasculaire.",
                        "category": "Cardio",
                        "difficulty": 4,
                        "hint": [
                            "Restez hydrat\u00e9 pendant l'entraînement.",
                            "\u00c9coutez votre corps et ajustez l'intensit\u00e9 si n\u00e9cessaire.",
                        ],
                        "exercises": ["burpees", "jumpingjacks"],
                    },
                    {
                        "id": "renfo-corps",
                        "title": "Renfo du corps",
                        "description": "Un programme ax\u00e9 sur le renforcement des muscles du haut du corps.",
                        "category": "Haut du corps",
                        "difficulty": 3,
                        "hint": [
                            "Assurez-vous de maintenir une bonne forme tout au long de l'exercice.",
                            "\u00c9coutez votre corps et ajustez l'intensit\u00e9 si n\u00e9cessaire.",
                        ],
                        "exercises": ["chinups", "dips"],
                    },
                ]
            }
            save_user_data(user.username, new_user)
            return {"status": True, "user": new_user}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error while creating account")

@app.post("/login")
async def login(user: User):
    try:
        user_data = load_user_data(user.username)
        password_match = bcrypt.checkpw(user.password.encode("utf-8"), user_data["password"].encode("utf-8"))
        if password_match:
            return {"status": True, "user": user_data}
        else:
            raise HTTPException(status_code=401, detail="Username or password incorrect")
    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error while logging in")

@app.post("/create/prog")
async def create_program(program: Program, username: str = Body(...)):
    try:
        user_data = load_user_data(username)
        user_data.setdefault("progs", []).append({
            "id": program.title.lower().replace(" ", "-"),
            "title": program.title,
            "description": program.description,
            "exercises": program.exercises
        })
        save_user_data(username, user_data)
        return {"status": True, "message": "Program created successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error while creating program")

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

@app.get("/progs/{id}")
async def get_program(id: str, username: str = Query(...)):
    try:
        user_data = load_user_data(username)
        programs = user_data.get("progs", [])
        if id == "all":
            return programs
        else:
            program = next((p for p in programs if p["id"] == id), None)
            if program:
                return program
            else:
                raise HTTPException(status_code=404, detail="Program not found")
    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error while reading programs")