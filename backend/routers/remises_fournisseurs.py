from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

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
    "/fournisseurs/{fournisseur_id}/remises",
    response_model=schemas.RemiseFournisseurRead,
    status_code=status.HTTP_201_CREATED
)
def add_remise(
    fournisseur_id: int,
    data: schemas.RemiseFournisseurCreate,
    db: Session = Depends(get_db)
):
    """
    Ajoute une remise pour une catégorie de pièce associée à un fournisseur.
    """
    fournisseur = db.query(models.Fournisseur).get(fournisseur_id)
    if not fournisseur:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fournisseur non trouvé"
        )
    remise = models.RemiseFournisseur(
        fournisseur_id=fournisseur_id,
        **data.dict()
    )
    db.add(remise)
    db.commit()
    db.refresh(remise)
    return remise

@router.get(
    "/fournisseurs/{fournisseur_id}/remises",
    response_model=List[schemas.RemiseFournisseurRead]
)
def list_remises(
    fournisseur_id: int,
    db: Session = Depends(get_db)
):
    """
    Liste toutes les remises d'un fournisseur.
    """
    return (
        db
        .query(models.RemiseFournisseur)
        .filter_by(fournisseur_id=fournisseur_id)
        .all()
    )

@router.put(
    "/remises_fournisseur/{remise_id}",
    response_model=schemas.RemiseFournisseurRead
)
def update_remise(
    remise_id: int,
    data: schemas.RemiseFournisseurCreate,
    db: Session = Depends(get_db)
):
    """
    Met à jour une remise existante.
    """
    remise = db.query(models.RemiseFournisseur).get(remise_id)
    if not remise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remise non trouvée"
        )
    remise.piece_category = data.piece_category
    remise.remise_pourcentage = data.remise_pourcentage
    db.commit()
    db.refresh(remise)
    return remise

@router.delete(
    "/remises_fournisseur/{remise_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_remise(
    remise_id: int,
    db: Session = Depends(get_db)
):
    """
    Supprime une remise par son ID.
    """
    remise = db.query(models.RemiseFournisseur).get(remise_id)
    if not remise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remise non trouvée"
        )
    db.delete(remise)
    db.commit()
    return None
