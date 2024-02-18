import os
import json
from fastapi import HTTPException

def get_user_file_path(username: str) -> str:
    return f"./data/users/{username}.json"

def load_user_data(username: str) -> dict:
    file_path = get_user_file_path(username)
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    else:
        raise HTTPException(status_code=404, detail="User not found")

def save_user_data(username: str, data: dict):
    file_path = get_user_file_path(username)
    with open(file_path, "w") as file:
        json.dump(data, file, indent=2)