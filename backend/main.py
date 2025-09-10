from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UserData(BaseModel):
    name: str
    age: int
    weight: float
    height: float
    gender: str
    activity: str
    goal: str
    training_type: str
    include_foods: list[str] = []
    exclude_foods: list[str] = []

@app.post("/generate_plan")
def generate_plan(data: UserData):
    return {
        "message": f"Plan genererad för {data.name}",
        "calories": 2200,
        "macros": {"protein": 150, "fat": 70, "carbs": 250}
    }
