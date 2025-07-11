# backend/routers/clients.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import schemas
from .. import models
from ..database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:   yield db
    finally: db.close()

@router.post("/", response_model=schemas.ClientRead)
def create_client(client: schemas.ClientCreate, db: Session = Depends(get_db)):
    db_client = models.Client(**client.dict())
    db.add(db_client); db.commit(); db.refresh(db_client)
    return db_client

@router.get("/", response_model=List[schemas.ClientRead])
def list_clients(q: Optional[str] = Query(None), db: Session = Depends(get_db)):
    query = db.query(models.Client)
    if q:
        like = f"%{q}%"
        query = query.filter(
            models.Client.nom.ilike(like) |
            models.Client.prenom.ilike(like) |
            models.Client.email.ilike(like)
        )
    return query.all()

# … et les autres endpoints (GET/{id}, PUT/{id}, DELETE/{id}, /search)
