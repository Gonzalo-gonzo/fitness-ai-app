# backend/main.py
from typing import Dict, List, Optional
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from auth import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlmodel import Session, select

from database import init_db, get_session
from models import User, MealPlan
from auth import get_password_hash, verify_password, create_access_token, get_current_user

app = FastAPI(title="Fitness AI Backend")

# CORS för lokal dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],  # strama åt senare
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

# ---------- Schemas ----------
class RegisterIn(BaseModel):
    username: str
    email: str
    password: str

class LoginIn(BaseModel):
    username: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ---------- Kostplan in/out ----------
class FoodItem(BaseModel):
    mat: str
    mangd_g: int
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
    gender: str            # "male" | "female"
    activity: str          # "sedentary" | "light" | "moderate" | "active" | "very_active"
    goal: str              # "maintain" | "bulk" | "cut"
    diet: Optional[str] = None   # "" | "vegetarian" | "vegan" | "pescetarian"
    allergies: List[str] = []
    targetWeight: Optional[int] = None

# ---------- Register/Login ----------
@app.post("/register", status_code=201)
def register(data: RegisterIn, session: Session = Depends(get_session)):
    # kolla unika fält
    exists = session.exec(select(User).where((User.username == data.username) | (User.email == data.email))).first()
    if exists:
        raise HTTPException(status_code=400, detail="Användarnamn eller e-post upptaget.")
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        is_premium=False,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"id": user.id, "username": user.username, "email": user.email}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Fel användarnamn eller lösenord")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Exempel på en skyddad route
@app.get("/me")
def read_me(current_user: dict = Depends(get_current_user)):
    return {"username": current_user.username, "email": current_user.email}

@app.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_premium": current_user.is_premium,
        "created_at": str(current_user.created_at),
    }

# ---------- Kostplan-beräkning ----------
def calculate_bmr(weight: float, height: float, age: int, gender: str) -> int:
    if gender == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    return round(bmr)

def activity_factor(level: str) -> float:
    return {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9,
    }.get(level, 1.2)

# === Din FOOD_DB och menylogik från tidigare steg ===
# Förkortad här: klistra in din senaste FOOD_DB, MEAL_SPLIT, MEAL_BLUEPRINTS,
# matches_diet/allergies, filter_foods, calc_grams_for_calories, create_food_item, meal_items_for
# --- START: KLIS TRA IN DITT SENASTE BLOCK HÄR ---
import random

FOOD_DB = [
    # (klistra in din 40+ lista här, med "category" och "tags" om du använder dem i filter)
    {"mat": "Kycklingfilé", "kcal": 165, "protein": 31, "fett": 3, "kolhydrater": 0, "category": "protein", "tags": ["animal"]},
    {"mat": "Ris", "kcal": 130, "protein": 2, "fett": 0, "kolhydrater": 28, "category": "carb", "tags": []},
    {"mat": "Potatis", "kcal": 77, "protein": 2, "fett": 0, "kolhydrater": 17, "category": "carb", "tags": []},
    {"mat": "Havregryn", "kcal": 360, "protein": 13, "fett": 7, "kolhydrater": 60, "category": "carb", "tags": ["contains_gluten"]},
    {"mat": "Banan", "kcal": 90, "protein": 1, "fett": 0, "kolhydrater": 23, "category": "fruit", "tags": []},
    {"mat": "Ägg", "kcal": 155, "protein": 13, "fett": 11, "kolhydrater": 1, "category": "egg", "tags": ["egg"]},
    {"mat": "Lax", "kcal": 208, "protein": 20, "fett": 13, "kolhydrater": 0, "category": "fish", "tags": ["fish"]},
    {"mat": "Broccoli", "kcal": 35, "protein": 3, "fett": 0, "kolhydrater": 7, "category": "veg", "tags": []},
    # ... (fortsätt med resten som du redan har)
]

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
    out = []
    for f in FOOD_DB:
        if f.get("category") != category:
            continue
        if not matches_diet(f, diet):
            continue
        if not matches_allergies(f, allergies):
            continue
        out.append(f)
    return out

def calc_grams_for_calories(food: dict, target_kcal: float, min_g: int = 20, max_g: int = 400) -> int:
    grams = int(round((target_kcal / max(food["kcal"], 1)) * 100))
    grams = max(min_g, min(max_g, grams))
    return grams

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

def pick_food(category: str, diet: Optional[str], allergies: List[str]) -> Optional[dict]:
    candidates = filter_foods(category, diet, allergies)
    if not candidates:
        return None
    return random.choice(candidates)

def meal_items_for(meal: str, meal_kcal: float, diet: Optional[str], allergies: List[str]) -> List[FoodItem]:
    items: List[FoodItem] = []
    plan = MEAL_BLUEPRINTS[meal]

    adjusted_plan = []
    for cat, w in plan:
        if cat == "dairy":
            dairy_ok = (diet not in ["vegan"]) and ("laktos" not in allergies)
            adjusted_plan.append(("dairy" if dairy_ok else "protein", w))
        else:
            adjusted_plan.append((cat, w))

    for cat, weight in adjusted_plan:
        food = pick_food(cat, diet, allergies)
        if not food:
            for fb in ["protein", "carb", "veg", "fruit", "nuts", "fish"]:
                food = pick_food(fb, diet, allergies)
                if food:
                    break
        if not food:
            continue
        target_k = meal_kcal * weight
        min_map = {"veg": 60, "fruit": 80, "nuts": 10, "fat": 5}
        grams = calc_grams_for_calories(food, target_k, min_g=min_map.get(food.get("category", ""), 30))
        items.append(create_food_item(food, grams))

    if not items:
        for fb in ["protein", "carb"]:
            food = pick_food(fb, diet, allergies)
            if food:
                grams = calc_grams_for_calories(food, meal_kcal / 2, min_g=40)
                items.append(create_food_item(food, grams))
                break

    return items
# --- SLUT: KLIS TRA IN DITT SENASTE BLOCK HÄR ---

@app.post("/generate_plan", response_model=PlanResult)
def generate_plan(
    data: UserInput,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),  # kräver inloggning
):
    # 1) BMR/TDEE & kalorier
    bmr = calculate_bmr(data.weight, data.height, data.age, data.gender)
    tdee = round(bmr * activity_factor(data.activity))
    if data.goal == "bulk":
        calories = tdee + 400
    elif data.goal == "cut":
        calories = tdee - 400
    else:
        calories = tdee

    # 2) Dagliga makromål
    protein_g = round(2.0 * data.weight)
    fat_g     = round(0.9 * data.weight)
    carbs_g   = max(0, round((calories - (protein_g * 4 + fat_g * 9)) / 4))

    # 3) 5 måltider
    menu: Dict[str, List[FoodItem]] = {}
    for meal, ratio in MEAL_SPLIT.items():
        meal_kcal = calories * ratio
        items = meal_items_for(meal, meal_kcal, data.diet, data.allergies)
        menu[meal] = items

    result: PlanResult = PlanResult(
        user=data.name,
        bmr=int(bmr),
        tdee=int(tdee),
        calories=int(round(calories)),
        macros={"protein_g": protein_g, "fat_g": fat_g, "carbs_g": carbs_g},
        targetWeight=data.targetWeight,
        menu=menu,
    )

    # 4) Spara i DB kopplat till user
    mp = MealPlan(user_id=current_user.id, plan_json=result.dict())
    session.add(mp)
    session.commit()
    session.refresh(mp)

    return result

@app.get("/plans")
def list_plans(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    plans = session.exec(
        select(MealPlan).where(MealPlan.user_id == current_user.id).order_by(MealPlan.created_at.desc())
    ).all()
    return [{"id": p.id, "created_at": str(p.created_at)} for p in plans]

@app.get("/plans/{plan_id}")
def get_plan(
    plan_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    plan = session.get(MealPlan, plan_id)
    if not plan or plan.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Plan hittades inte.")
    return plan.plan_json
