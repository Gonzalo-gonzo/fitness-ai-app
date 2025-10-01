# backend/main.py
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlmodel import Session, select
from datetime import timedelta
from typing import Dict, List, Optional
import random
from fastapi import FastAPI
from backend.routes_dailylog import router as dailylog_router

from backend.database import get_session, init_db
from backend.models import User, MealPlan, Food
from backend.auth import (
    get_password_hash,
    create_access_token,
    get_current_user,
    authenticate_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)



app = FastAPI(title="Fitness AI Backend")

@app.on_event("startup")
def on_startup():
    init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(dailylog_router)

# ---------- Foods ----------
@app.post("/foods", status_code=201)
def add_food(
    food: Food,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # kräver: mat, kcal_per_100g, protein, fett, kolhydrater
    if not food.mat or food.kcal_per_100g is None:
        raise HTTPException(status_code=400, detail="Fält saknas (mat/kcal_per_100g)")

    normalized = food.mat.strip().lower()
    exists = session.exec(select(Food).where(Food.mat_normalized == normalized)).first()
    if exists:
        raise HTTPException(status_code=400, detail="Livsmedel finns redan globalt")

    new_food = Food(
        mat=food.mat.strip(),
        mat_normalized=normalized,
        kcal_per_100g=food.kcal_per_100g,
        protein=food.protein,
        fett=food.fett,
        kolhydrater=food.kolhydrater,
        category=food.category,
        tags=food.tags,
    )
    session.add(new_food)
    session.commit()
    session.refresh(new_food)
    return new_food

@app.get("/foods")
def list_foods(session: Session = Depends(get_session)):
    return session.exec(select(Food)).all()

# ---------- Auth / Users ----------
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

@app.post("/register", status_code=201)
def register(data: RegisterIn, session: Session = Depends(get_session)):
    exists = session.exec(
        select(User).where((User.username == data.username) | (User.email == data.email))
    ).first()
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
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_premium": current_user.is_premium,
        "created_at": str(current_user.created_at),
    }

# ---------- Kostplan ----------
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
    gender: str
    activity: str
    goal: str
    diet: Optional[str] = None
    allergies: List[str] = []
    targetWeight: Optional[int] = None

def calculate_bmr(weight: float, height: float, age: int, gender: str) -> int:
    if gender == "male":
        return round(10 * weight + 6.25 * height - 5 * age + 5)
    return round(10 * weight + 6.25 * height - 5 * age - 161)

def activity_factor(level: str) -> float:
    return {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9,
    }.get(level, 1.2)

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

def matches_diet(food: Food, diet: Optional[str]) -> bool:
    tags = set(food.tags or [])
    if not diet:
        return True
    if diet == "vegan":
        return tags.isdisjoint({"animal", "fish", "dairy", "egg"})
    if diet == "vegetarian":
        return tags.isdisjoint({"animal", "fish"})
    if diet == "pescetarian":
        return "animal" not in tags
    return True

def matches_allergies(food: Food, allergies: List[str]) -> bool:
    tags = set(food.tags or [])
    if "gluten" in allergies and "contains_gluten" in tags:
        return False
    if "laktos" in allergies and "contains_lactose" in tags:
        return False
    if "nötter" in allergies and "contains_nuts" in tags:
        return False
    return True

def pick_food(session: Session, category: str, diet: Optional[str], allergies: List[str]) -> Optional[Food]:
    candidates = session.exec(select(Food).where(Food.category == category)).all()
    candidates = [f for f in candidates if matches_diet(f, diet) and matches_allergies(f, allergies)]
    return random.choice(candidates) if candidates else None

def calc_grams_for_calories(food: Food, target_kcal: float, min_g: int = 20, max_g: int = 400) -> int:
    grams = int(round((target_kcal / max(food.kcal_per_100g, 1)) * 100))
    return max(min_g, min(max_g, grams))

def create_food_item(food: Food, grams: int) -> FoodItem:
    factor = grams / 100.0
    return FoodItem(
        mat=food.mat,
        mangd_g=int(grams),
        kcal=round(food.kcal_per_100g * factor),
        protein=round(food.protein * factor),
        fett=round(food.fett * factor),
        kolhydrater=round(food.kolhydrater * factor),
    )


def meal_items_for(session: Session, meal: str, meal_kcal: float, diet: Optional[str], allergies: List[str]) -> List[FoodItem]:
    items: List[FoodItem] = []
    plan = MEAL_BLUEPRINTS[meal]
    for cat, weight in plan:
        food = pick_food(session, cat, diet, allergies)
        if not food:
            continue
        target_k = meal_kcal * weight
        grams = calc_grams_for_calories(food, target_k)
        items.append(create_food_item(food, grams))
    return items

@app.post("/generate_plan", response_model=PlanResult)
def generate_plan(
    data: UserInput,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    bmr = calculate_bmr(data.weight, data.height, data.age, data.gender)
    tdee = round(bmr * activity_factor(data.activity))
    calories = tdee + 400 if data.goal == "bulk" else tdee - 400 if data.goal == "cut" else tdee

    protein_g = round(2.0 * data.weight)
    fat_g = round(0.9 * data.weight)
    carbs_g = max(0, round((calories - (protein_g * 4 + fat_g * 9)) / 4))

    menu: Dict[str, List[FoodItem]] = {}
    for meal, ratio in MEAL_SPLIT.items():
        meal_kcal = calories * ratio
        items = meal_items_for(session, meal, meal_kcal, data.diet, data.allergies)
        menu[meal] = items if items else []

    result = PlanResult(
        user=data.name,
        bmr=bmr,
        tdee=tdee,
        calories=calories,
        macros={"protein_g": protein_g, "fat_g": fat_g, "carbs_g": carbs_g},
        targetWeight=data.targetWeight,
        menu=menu,
    )

    mp = MealPlan(user_id=current_user.id, plan_json=result.dict())
    session.add(mp)
    session.commit()
    session.refresh(mp)
    return result

@app.get("/plans")
def list_plans(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    plans = session.exec(
        select(MealPlan).where(MealPlan.user_id == current_user.id).order_by(MealPlan.created_at.desc())
    ).all()
    return [{"id": p.id, "created_at": str(p.created_at)} for p in plans]

@app.get("/plans/{plan_id}")
def get_plan(plan_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    plan = session.get(MealPlan, plan_id)
    if not plan or plan.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Plan hittades inte.")
    return plan.plan_json
