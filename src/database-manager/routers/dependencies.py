from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from internal import crud, schemas
from internal.database import SessionLocal
from typing import List

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
