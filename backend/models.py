from typing import Optional, List
from datetime import datetime, date
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON, Integer, String, Date, ForeignKey, Float
from sqlalchemy.orm import relationship

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    is_premium: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MealPlan(SQLModel, table=True):
    __tablename__ = "meal_plans"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    plan_json: dict = Field(sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Food(SQLModel, table=True):
    __tablename__ = "foods"
    id: Optional[int] = Field(default=None, primary_key=True)
    mat: str = Field(index=True)
    mat_normalized: str = Field(index=True, unique=True)
    kcal_per_100g: int
    protein: float
    fett: float
    kolhydrater: float
    category: Optional[str] = Field(default=None, index=True)
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))

# ✅ Nu använder vi `date` som typ, inte ett variabelnamn
class DailyLog(SQLModel, table=True):
    __tablename__ = "daily_logs"
    id: Optional[int] = Field(default=None, primary_key=True)
    log_date: date = Field(index=True, unique=True)  
    calories_goal: int = 0
    protein_goal: int = 0
    fat_goal: int = 0
    carbs_goal: int = 0

class MealEntry(SQLModel, table=True):
    __tablename__ = "meal_entries"
    id: Optional[int] = Field(default=None, primary_key=True)
    log_id: int = Field(foreign_key="daily_logs.id")
    meal_type: str
    food_id: int = Field(foreign_key="foods.id")
    grams: float
    kcal: float
    protein: float
    fat: float
    carbs: float
