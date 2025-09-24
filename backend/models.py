# backend/models.py
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, JSON

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    email: str = Field(index=True, unique=True, nullable=False)
    hashed_password: str
    is_premium: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MealPlan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    # lagra hela resultatet från generate_plan (inkl. menu) som JSON
    plan_json: dict = Field(sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
