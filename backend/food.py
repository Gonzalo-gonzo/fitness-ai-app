from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import List, Optional
import random

from database import get_session
from models import Food, User
from auth import get_current_user

router = APIRouter(prefix="/foods", tags=["Foods"])

class FoodIn(BaseModel):
    mat: str
    kcal_per_100g: int
    protein: int
    fett: int
    kolhydrater: int

@router.get("/", response_model=List[Food])
def list_foods(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return session.exec(select(Food).where(Food.user_id == current_user.id)).all()

@router.post("/", status_code=201, response_model=Food)
def add_food(food: FoodIn, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    normalized_name = food.mat.strip().lower()

    exists = session.exec(
        select(Food).where((Food.user_id == current_user.id) & (Food.mat == normalized_name))
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="Livsmedel finns redan")

    new_food = Food(
        user_id=current_user.id,
        mat=normalized_name,
        kcal_per_100g=food.kcal_per_100g,
        protein=food.protein,
        fett=food.fett,
        kolhydrater=food.kolhydrater,
    )
    session.add(new_food)
    session.commit()
    session.refresh(new_food)
    return new_food

# ---------- Kostplan-hjälp ----------
def filter_foods(
    session: Session,
    current_user: User,
    category: Optional[str] = None,
    diet: Optional[str] = None,
    allergies: List[str] = []
) -> List[Food]:
    """Filtrera livsmedel för användaren baserat på kategori, diet och allergier."""
    q = select(Food).where(Food.user_id == current_user.id)
    if category:
        q = q.where(Food.category == category)

    foods = session.exec(q).all()

    # diet/allergi-filter
    result = []
    for f in foods:
        tags = set(f.tags or [])
        if diet == "vegan" and not tags.isdisjoint({"animal", "fish", "dairy", "egg"}):
            continue
        if diet == "vegetarian" and not tags.isdisjoint({"animal", "fish"}):
            continue
        if diet == "pescetarian" and "animal" in tags:
            continue
        if "gluten" in allergies and "contains_gluten" in tags:
            continue
        if "laktos" in allergies and "contains_lactose" in tags:
            continue
        if "nötter" in allergies and "contains_nuts" in tags:
            continue
        result.append(f)

    return result

def pick_food(session: Session, current_user: User, category: str, diet: Optional[str], allergies: List[str]) -> Optional[Food]:
    candidates = filter_foods(session, current_user, category, diet, allergies)
    return random.choice(candidates) if candidates else None

def calc_grams_for_calories(food: Food, target_kcal: float, min_g: int = 20, max_g: int = 400) -> int:
    grams = int(round((target_kcal / max(food.kcal_per_100g, 1)) * 100))
    return max(min_g, min(max_g, grams))
