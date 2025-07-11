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
    response_model=schemas.TechnicienRead,
    status_code=status.HTTP_201_CREATED
)
def create_technicien(
    technicien_in: schemas.TechnicienCreate,
    db: Session = Depends(get_db)
):
    """
    Crée un nouveau technicien.
    """
    technicien = models.Technicien(**technicien_in.dict())
    db.add(technicien)
    db.commit()
    db.refresh(technicien)
    return technicien

@router.get(
    "/",
    response_model=List[schemas.TechnicienRead]
)
def list_techniciens(
    q: Optional[str] = Query(None, description="Recherche par nom du technicien"),
    db: Session = Depends(get_db)
):
    """
    Retourne tous les techniciens, filtrés facultativement par nom.
    """
    query = db.query(models.Technicien)
    if q:
        query = query.filter(models.Technicien.nom.ilike(f"%{q}%"))
    return query.all()

@router.get(
    "/{technicien_id}",
    response_model=schemas.TechnicienRead
)
def get_technicien(
    technicien_id: int,
    db: Session = Depends(get_db)
):
    """
    Récupère un technicien par son ID.
    """
    technicien = db.query(models.Technicien).get(technicien_id)
    if not technicien:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Technicien non trouvé"
        )
    return technicien

@router.put(
    "/{technicien_id}",
    response_model=schemas.TechnicienRead
)
def update_technicien(
    technicien_id: int,
    data: schemas.TechnicienCreate,
    db: Session = Depends(get_db)
):
    """
    Met à jour un technicien existant.
    """
    technicien = db.query(models.Technicien).get(technicien_id)
    if not technicien:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Technicien non trouvé"
        )
    for key, value in data.dict().items():
        setattr(technicien, key, value)
    db.commit()
    db.refresh(technicien)
    return technicien

@router.delete(
    "/{technicien_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_technicien(
    technicien_id: int,
    db: Session = Depends(get_db)
):
    """
    Supprime un technicien par son ID.
    """
    technicien = db.query(models.Technicien).get(technicien_id)
    if not technicien:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Technicien non trouvé"
        )
    db.delete(technicien)
    db.commit()
    return None
