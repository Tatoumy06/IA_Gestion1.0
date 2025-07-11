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
    response_model=schemas.AssureurRead,
    status_code=status.HTTP_201_CREATED
)
def create_assureur(
    assureur_in: schemas.AssureurCreate,
    db: Session = Depends(get_db)
):
    """
    Crée un nouvel assureur.
    """
    assureur = models.Assureur(**assureur_in.dict())
    db.add(assureur)
    db.commit()
    db.refresh(assureur)
    return assureur

@router.get(
    "/",
    response_model=List[schemas.AssureurRead]
)
def list_assureurs(
    q: Optional[str] = Query(None, description="Recherche par nom d'assureur"),
    db: Session = Depends(get_db)
):
    """
    Retourne tous les assureurs, filtrés facultativement par nom.
    """
    query = db.query(models.Assureur)
    if q:
        query = query.filter(models.Assureur.nom.ilike(f"%{q}%"))
    return query.all()

@router.get(
    "/{assureur_id}",
    response_model=schemas.AssureurRead
)
def get_assureur(
    assureur_id: int,
    db: Session = Depends(get_db)
):
    """
    Récupère un assureur par son ID.
    """
    assureur = db.query(models.Assureur).get(assureur_id)
    if not assureur:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assureur non trouvé"
        )
    return assureur

@router.put(
    "/{assureur_id}",
    response_model=schemas.AssureurRead
)
def update_assureur(
    assureur_id: int,
    data: schemas.AssureurCreate,
    db: Session = Depends(get_db)
):
    """
    Met à jour un assureur existant.
    """
    assureur = db.query(models.Assureur).get(assureur_id)
    if not assureur:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assureur non trouvé"
        )
    for key, value in data.dict().items():
        setattr(assureur, key, value)
    db.commit()
    db.refresh(assureur)
    return assureur

@router.delete(
    "/{assureur_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_assureur(
    assureur_id: int,
    db: Session = Depends(get_db)
):
    """
    Supprime un assureur par son ID.
    """
    assureur = db.query(models.Assureur).get(assureur_id)
    if not assureur:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assureur non trouvé"
        )
    db.delete(assureur)
    db.commit()
    return None
