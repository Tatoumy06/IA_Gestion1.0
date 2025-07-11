from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import SessionLocal

router = APIRouter()

# Dependency pour obtenir une session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post(
    "/",
    response_model=schemas.MainDoeuvreRead,
    status_code=status.HTTP_201_CREATED
)
def create_main_doeuvre(
    md_in: schemas.MainDoeuvreCreate,
    db: Session = Depends(get_db)
):
    """
    Crée une nouvelle ligne de main-d'œuvre.
    """
    md = models.MainDoeuvre(**md_in.dict())
    db.add(md)
    db.commit()
    db.refresh(md)
    return md

@router.post(
    "/search",
    response_model=List[schemas.MainDoeuvreRead]
)
def search_main_doeuvre(
    md_in: schemas.MainDoeuvreCreate,
    db: Session = Depends(get_db)
):
    """
    Recherche de main-d'œuvre par description (insensible à la casse).
    """
    return (
        db.query(models.MainDoeuvre)
          .filter(models.MainDoeuvre.description.ilike(f"%{md_in.description}%"))
          .all()
    )

@router.put(
    "/{md_id}",
    response_model=schemas.MainDoeuvreRead
)
def update_main_doeuvre(
    md_id: int,
    md_in: schemas.MainDoeuvreCreate,
    db: Session = Depends(get_db)
):
    """
    Met à jour une entrée main-d'œuvre existante.
    """
    md = db.query(models.MainDoeuvre).get(md_id)
    if not md:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Main-d'œuvre non trouvée"
        )
    md.description = md_in.description
    md.taux_horaire = md_in.taux_horaire
    db.commit()
    db.refresh(md)
    return md

@router.delete(
    "/{md_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_main_doeuvre(
    md_id: int,
    db: Session = Depends(get_db)
):
    """
    Supprime une entrée main-d'œuvre par son ID.
    """
    md = db.query(models.MainDoeuvre).get(md_id)
    if not md:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Main-d'œuvre non trouvée"
        )
    db.delete(md)
    db.commit()
    return None
