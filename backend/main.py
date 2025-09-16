from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ CORS fix
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tillåt frontend på localhost
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Inputmodell
class UserData(BaseModel):
    name: str
    age: int
    weight: float
    height: float
    gender: str
    activity: str
    goal: str
    allergies: list[str] = []   # 👈 nytt
    diet: str = ""              # 👈 nytt
    targetWeight: float | None = None

activity_factors = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}

@app.post("/generate_plan")
def generate_plan(data: UserData):
    # ✅ BMR-beräkning
    if data.gender.lower() == "male":
        bmr = 10 * data.weight + 6.25 * data.height - 5 * data.age + 5
    else:
        bmr = 10 * data.weight + 6.25 * data.height - 5 * data.age - 161

    # ✅ TDEE
    activity_factor = activity_factors.get(data.activity.lower(), 1.2)
    tdee = bmr * activity_factor

    # ✅ Kalorimål
    if data.goal.lower() == "bulk":
        calories = tdee + 400
    elif data.goal.lower() == "cut":
        calories = tdee - 400
    else:
        calories = tdee

    # ✅ Makros
    protein = round(data.weight * 2.0)
    fat = round((0.25 * calories) / 9)
    carbs = round((calories - (protein * 4 + fat * 9)) / 4)

    # ✅ Svar
    return {
        "user": data.name,
        "bmr": round(bmr),
        "tdee": round(tdee),
        "calories": round(calories),
        "macros": {
            "protein_g": protein,
            "fat_g": fat,
            "carbs_g": carbs
        },
        "preferences": {
            "allergies": data.allergies,
            "diet": data.diet
        },
        "targetWeight": data.targetWeight,
        "notes": f"Beräkning baserat på {data.activity} aktivitet, mål: {data.goal}"
    }
