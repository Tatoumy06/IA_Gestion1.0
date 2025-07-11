# backend/routers/experts.py

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import models, schemas
from ..database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post(
    "/",
    response_model=schemas.ExpertRead,
    status_code=status.HTTP_201_CREATED
)
def create_expert(
    expert_in: schemas.ExpertCreate,
    db: Session = Depends(get_db)
):
    """
    Crée un nouvel expert.
    """
    expert = models.Expert(**expert_in.dict())
    db.add(expert)
    db.commit()
    db.refresh(expert)
    return expert

@router.get(
    "/",
    response_model=List[schemas.ExpertRead]
)
def list_experts(
    q: Optional[str] = Query(None, description="Recherche par nom d'expert"),
    db: Session = Depends(get_db)
):
    """
    Retourne tous les experts, filtrés facultativement par nom.
    """
    query = db.query(models.Expert)
    if q:
        query = query.filter(models.Expert.nom.ilike(f"%{q}%"))
    return query.all()

@router.get(
    "/{expert_id}",
    response_model=schemas.ExpertRead
)
def get_expert(
    expert_id: int,
    db: Session = Depends(get_db)
):
    """
    Récupère un expert par son ID.
    """
    expert = db.query(models.Expert).get(expert_id)
    if not expert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expert non trouvé"
        )
    return expert

@router.put(
    "/{expert_id}",
    response_model=schemas.ExpertRead
)
def update_expert(
    expert_id: int,
    expert_in: schemas.ExpertCreate,
    db: Session = Depends(get_db)
):
    """
    Met à jour un expert existant.
    """
    expert = db.query(models.Expert).get(expert_id)
    if not expert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expert non trouvé"
        )
    for key, value in expert_in.dict().items():
        setattr(expert, key, value)
    db.commit()
    db.refresh(expert)
    return expert

@router.delete(
    "/{expert_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_expert(
    expert_id: int,
    db: Session = Depends(get_db)
):
    """
    Supprime un expert par son ID.
    """
    expert = db.query(models.Expert).get(expert_id)
    if not expert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expert non trouvé"
        )
    db.delete(expert)
    db.commit()
    return None
