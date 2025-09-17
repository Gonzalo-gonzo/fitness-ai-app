from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import random

app = FastAPI()

# CORS för lokal utveckling
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # strama åt senare
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Datamodeller ----------
class FoodItem(BaseModel):
    mat: str
    mangd_g: int   # otillagad/rå vikt i gram
    kcal: int
    protein: int
    fett: int
    kolhydrater: int

class PlanResult(BaseModel):
    user: str
    bmr: int
    tdee: int
    calories: int
    macros: Dict[str, int]
    targetWeight: Optional[int] = None
    menu: Dict[str, List[FoodItem]]

class UserInput(BaseModel):
    name: str
    age: int
    weight: float
    height: float
    gender: str
    activity: str
    goal: str
    diet: Optional[str] = None
    allergies: List[str] = []
    targetWeight: Optional[int] = None

# ---------- Hjälpare ----------
def calculate_bmr(weight: float, height: float, age: int, gender: str) -> int:
    if gender == "male":
        return round(10 * weight + 6.25 * height - 5 * age + 5)
    else:
        return round(10 * weight + 6.25 * height - 5 * age - 161)

def activity_factor(level: str) -> float:
    return {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9,
    }.get(level, 1.2)

def create_food_item(base: dict, grams: int) -> FoodItem:
    factor = grams / 100.0
    return FoodItem(
        mat=base["mat"],
        mangd_g=int(grams),
        kcal=round(base["kcal"] * factor),
        protein=round(base["protein"] * factor),
        fett=round(base["fett"] * factor),
        kolhydrater=round(base["kolhydrater"] * factor),
    )

def matches_diet(food: dict, diet: Optional[str]) -> bool:
    tags = set(food.get("tags", []))
    if not diet:
        return True
    if diet == "vegan":
        return tags.isdisjoint({"animal", "fish", "dairy", "egg"})
    if diet == "vegetarian":
        return tags.isdisjoint({"animal", "fish"})
    if diet == "pescetarian":
        return "animal" not in tags
    return True

def matches_allergies(food: dict, allergies: List[str]) -> bool:
    tags = set(food.get("tags", []))
    if "gluten" in allergies and "contains_gluten" in tags:
        return False
    if "laktos" in allergies and "contains_lactose" in tags:
        return False
    if "nötter" in allergies and "contains_nuts" in tags:
        return False
    return True

def filter_foods(category: str, diet: Optional[str], allergies: List[str]) -> List[dict]:
    return [
        f for f in FOOD_DB
        if f["category"] == category
        and matches_diet(f, diet)
        and matches_allergies(f, allergies)
    ]

def calc_grams_for_calories(food: dict, target_kcal: float, min_g: int = 20, max_g: int = 400) -> int:
    grams = int(round((target_kcal / max(food["kcal"], 1)) * 100))
    return max(min_g, min(max_g, grams))

# ---------- Livsmedelsdatabas (~40 st, 100 g rå/okokt) ----------
FOOD_DB = [
    # Protein
    {"mat": "Kycklingfilé", "kcal": 165, "protein": 31, "fett": 3, "kolhydrater": 0, "category": "protein", "tags": ["animal"]},
    {"mat": "Nötfärs 10%", "kcal": 217, "protein": 26, "fett": 12, "kolhydrater": 0, "category": "protein", "tags": ["animal"]},
    {"mat": "Fläskfilé", "kcal": 143, "protein": 21, "fett": 6, "kolhydrater": 0, "category": "protein", "tags": ["animal"]},
    {"mat": "Lax", "kcal": 208, "protein": 20, "fett": 13, "kolhydrater": 0, "category": "fish", "tags": ["fish"]},
    {"mat": "Torsk", "kcal": 82, "protein": 18, "fett": 1, "kolhydrater": 0, "category": "fish", "tags": ["fish"]},
    {"mat": "Tonfisk", "kcal": 132, "protein": 28, "fett": 1, "kolhydrater": 0, "category": "fish", "tags": ["fish"]},
    {"mat": "Ägg", "kcal": 155, "protein": 13, "fett": 11, "kolhydrater": 1, "category": "egg", "tags": ["animal", "egg"]},
    {"mat": "Äggvita", "kcal": 52, "protein": 11, "fett": 0, "kolhydrater": 1, "category": "egg", "tags": ["egg"]},
    {"mat": "Tofu", "kcal": 76, "protein": 8, "fett": 5, "kolhydrater": 2, "category": "protein", "tags": []},
    {"mat": "Kikärtor", "kcal": 164, "protein": 9, "fett": 3, "kolhydrater": 27, "category": "protein", "tags": []},

    # Kolhydrater
    {"mat": "Ris", "kcal": 130, "protein": 2, "fett": 0, "kolhydrater": 28, "category": "carb", "tags": []},
    {"mat": "Potatis", "kcal": 77, "protein": 2, "fett": 0, "kolhydrater": 17, "category": "carb", "tags": []},
    {"mat": "Sötpotatis", "kcal": 86, "protein": 2, "fett": 0, "kolhydrater": 20, "category": "carb", "tags": []},
    {"mat": "Pasta", "kcal": 131, "protein": 5, "fett": 1, "kolhydrater": 25, "category": "carb", "tags": ["contains_gluten"]},
    {"mat": "Quinoa", "kcal": 120, "protein": 4, "fett": 2, "kolhydrater": 21, "category": "carb", "tags": []},
    {"mat": "Havregryn", "kcal": 360, "protein": 13, "fett": 7, "kolhydrater": 60, "category": "carb", "tags": ["contains_gluten"]},
    {"mat": "Bröd (fullkorn)", "kcal": 250, "protein": 9, "fett": 3, "kolhydrater": 46, "category": "carb", "tags": ["contains_gluten"]},
    {"mat": "Knäckebröd", "kcal": 330, "protein": 9, "fett": 1, "kolhydrater": 70, "category": "carb", "tags": ["contains_gluten"]},

    # Frukt
    {"mat": "Banan", "kcal": 90, "protein": 1, "fett": 0, "kolhydrater": 23, "category": "fruit", "tags": []},
    {"mat": "Äpple", "kcal": 52, "protein": 0, "fett": 0, "kolhydrater": 14, "category": "fruit", "tags": []},
    {"mat": "Apelsin", "kcal": 47, "protein": 1, "fett": 0, "kolhydrater": 12, "category": "fruit", "tags": []},
    {"mat": "Blåbär", "kcal": 57, "protein": 1, "fett": 0, "kolhydrater": 14, "category": "fruit", "tags": []},
    {"mat": "Jordgubbar", "kcal": 33, "protein": 1, "fett": 0, "kolhydrater": 8, "category": "fruit", "tags": []},

    # Grönsaker
    {"mat": "Broccoli", "kcal": 35, "protein": 3, "fett": 0, "kolhydrater": 7, "category": "veg", "tags": []},
    {"mat": "Spenat", "kcal": 23, "protein": 3, "fett": 0, "kolhydrater": 4, "category": "veg", "tags": []},
    {"mat": "Paprika", "kcal": 31, "protein": 1, "fett": 0, "kolhydrater": 6, "category": "veg", "tags": []},
    {"mat": "Tomat", "kcal": 18, "protein": 1, "fett": 0, "kolhydrater": 4, "category": "veg", "tags": []},
    {"mat": "Morot", "kcal": 41, "protein": 1, "fett": 0, "kolhydrater": 10, "category": "veg", "tags": []},

    # Mejeri/nötter/fett
    {"mat": "Naturell kvarg", "kcal": 68, "protein": 12, "fett": 0, "kolhydrater": 4, "category": "dairy", "tags": ["dairy", "contains_lactose"]},
    {"mat": "Grekisk yoghurt 10%", "kcal": 120, "protein": 6, "fett": 10, "kolhydrater": 3, "category": "dairy", "tags": ["dairy", "contains_lactose"]},
    {"mat": "Mjölk 1,5%", "kcal": 45, "protein": 3, "fett": 1, "kolhydrater": 5, "category": "dairy", "tags": ["dairy", "contains_lactose"]},
    {"mat": "Mandlar", "kcal": 579, "protein": 21, "fett": 50, "kolhydrater": 22, "category": "nuts", "tags": ["contains_nuts"]},
    {"mat": "Olivolja", "kcal": 884, "protein": 0, "fett": 100, "kolhydrater": 0, "category": "fat", "tags": []},
]

# ---------- Menygenerator ----------
MEAL_SPLIT = {
    "frukost": 0.20,
    "mellanmal_1": 0.10,
    "lunch": 0.30,
    "pre_workout_meal": 0.15,
    "middag": 0.25,
}

MEAL_BLUEPRINTS = {
    "frukost": [("carb", 0.45), ("protein", 0.40), ("fruit", 0.15)],
    "mellanmal_1": [("dairy", 0.50), ("fruit", 0.30), ("nuts", 0.20)],
    "lunch": [("protein", 0.35), ("carb", 0.50), ("veg", 0.15)],
    "pre_workout_meal": [("carb", 0.60), ("protein", 0.30), ("fruit", 0.10)],
    "middag": [("protein", 0.40), ("carb", 0.45), ("veg", 0.15)],
}

def pick_food(category: str, diet: Optional[str], allergies: List[str]) -> Optional[dict]:
    candidates = filter_foods(category, diet, allergies)
    return random.choice(candidates) if candidates else None

def meal_items_for(meal: str, meal_kcal: float, diet: Optional[str], allergies: List[str]) -> List[FoodItem]:
    items: List[FoodItem] = []
    plan = MEAL_BLUEPRINTS[meal]

    for cat, weight in plan:
        food = pick_food(cat, diet, allergies)
        if not food:
            continue
        grams = calc_grams_for_calories(food, meal_kcal * weight)
        items.append(create_food_item(food, grams))

    return items

# ---------- API ----------
@app.post("/generate_plan", response_model=PlanResult)
def generate_plan(data: UserInput):
    bmr = calculate_bmr(data.weight, data.height, data.age, data.gender)
    tdee = round(bmr * activity_factor(data.activity))
    calories = tdee + 400 if data.goal == "bulk" else tdee - 400 if data.goal == "cut" else tdee

    protein_g = round(2.0 * data.weight)
    fat_g     = round(0.9 * data.weight)
    carbs_g   = max(0, round((calories - (protein_g * 4 + fat_g * 9)) / 4))

    menu: Dict[str, List[FoodItem]] = {}
    for meal, ratio in MEAL_SPLIT.items():
        meal_kcal = calories * ratio
        menu[meal] = meal_items_for(meal, meal_kcal, data.diet, data.allergies)

    return {
        "user": data.name,
        "bmr": bmr,
        "tdee": tdee,
        "calories": calories,
        "macros": {"protein_g": protein_g, "fat_g": fat_g, "carbs_g": carbs_g},
        "targetWeight": data.targetWeight,
        "menu": menu,
    }
