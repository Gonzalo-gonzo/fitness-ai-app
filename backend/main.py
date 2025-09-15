from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 👈 tillåt alla domäner (kan begränsas senare)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Inputmodell
class UserData(BaseModel):
    name: str
    age: int
    weight: float   # kg
    height: float   # cm
    gender: str     # "male" eller "female"
    activity: str   # sedentary, light, moderate, active, very_active
    goal: str       # bulk, cut, maintain

# Aktivitetsfaktorer
activity_factors = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}

@app.post("/generate_plan")
def generate_plan(data: UserData):
    # 1) BMR (Mifflin–St Jeor)
    if data.gender.lower() == "male":
        bmr = 10 * data.weight + 6.25 * data.height - 5 * data.age + 5
    else:  # female
        bmr = 10 * data.weight + 6.25 * data.height - 5 * data.age - 161

    # 2) TDEE
    activity_factor = activity_factors.get(data.activity.lower(), 1.2)
    tdee = bmr * activity_factor

    # 3) Justera enligt mål
    if data.goal.lower() == "bulk":
        calories = tdee + 400
    elif data.goal.lower() == "cut":
        calories = tdee - 400
    else:  # maintain
        calories = tdee

    # 4) Makronutrienter
    protein = round(data.weight * 2.0)  # 2g per kg kroppsvikt
    protein_kcal = protein * 4

    fat = round((0.25 * calories) / 9)  # 25% av kalorier
    fat_kcal = fat * 9

    carbs = round((calories - (protein_kcal + fat_kcal)) / 4)
    
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
        "notes": f"Beräkning baserat på {data.activity} aktivitet och mål: {data.goal}"
    }
