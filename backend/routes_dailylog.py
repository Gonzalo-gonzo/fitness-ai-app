# backend/routes_dailylog.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import date
from typing import List

from backend.database import get_session
from backend.models import DailyLog, MealEntry, Food

router = APIRouter(prefix="/daily-log", tags=["Daily Log"])

# Hämta eller skapa en dagbok för ett visst datum
@router.get("/{log_date}")
def get_daily_log(log_date: date, session: Session = Depends(get_session)):
    log = session.exec(select(DailyLog).where(DailyLog.log_date == log_date)).first()
    if not log:
        log = DailyLog(log_date=log_date)
        session.add(log)
        session.commit()
        session.refresh(log)
    return log

# Sätt mål för ett visst datum
@router.post("/{log_date}/set-goals")
def set_goals(
    log_date: date,
    calories: int,
    protein: int,
    fat: int,
    carbs: int,
    session: Session = Depends(get_session),
):
    log = session.exec(select(DailyLog).where(DailyLog.log_date == log_date)).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    log.calories_goal = calories
    log.protein_goal = protein
    log.fat_goal = fat
    log.carbs_goal = carbs
    session.add(log)
    session.commit()
    session.refresh(log)
    return log

# Lägg till en måltid
@router.post("/{log_date}/add-meal")
def add_meal(
    log_date: date,
    meal_type: str,
    food_id: int,
    grams: float,
    session: Session = Depends(get_session),
):
    log = session.exec(select(DailyLog).where(DailyLog.log_date == log_date)).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")

    food = session.get(Food, food_id)
    if not food:
        raise HTTPException(status_code=404, detail="Food not found")

    factor = grams / 100
    entry = MealEntry(
        log_id=log.id,
        meal_type=meal_type,
        food_id=food.id,
        grams=grams,
        kcal=round(food.kcal_per_100g * factor),
        protein=round(food.protein * factor),
        fat=round(food.fett * factor),
        carbs=round(food.kolhydrater * factor),
    )
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry

# Hämta alla måltider för en dag (inkl totals)
@router.get("/{log_date}/meals")
def get_meals(log_date: date, session: Session = Depends(get_session)):
    log = session.exec(select(DailyLog).where(DailyLog.log_date == log_date)).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")

    totals = {"kcal": 0, "protein": 0, "fat": 0, "carbs": 0}
    for m in log.meals:
        totals["kcal"] += m.kcal
        totals["protein"] += m.protein
        totals["fat"] += m.fat
        totals["carbs"] += m.carbs

    return {"log": log, "meals": log.meals, "totals": totals}
