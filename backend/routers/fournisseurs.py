from fastapi import APIRouter, Depends, HTTPException, Query
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

@router.post("/", response_model=schemas.FournisseurRead)
def create_fournisseur(f: schemas.FournisseurCreate, db: Session = Depends(get_db)):
    """
    Crée un nouveau fournisseur.
    """
    obj = models.Fournisseur(**f.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/", response_model=List[schemas.FournisseurRead])
def list_fournisseurs(
    q: Optional[str] = Query(None, description="Recherche par nom de fournisseur"),
    db: Session = Depends(get_db)
) -> List[models.Fournisseur]:
    """
    Liste tous les fournisseurs, optionnellement filtrés par nom (insensible à la casse).
    """
    query = db.query(models.Fournisseur)
    if q:
        query = query.filter(models.Fournisseur.nom.ilike(f"%{q}%"))
    return query.all()

@router.get("/{fournisseur_id}", response_model=schemas.FournisseurRead)
def get_fournisseur(fournisseur_id: int, db: Session = Depends(get_db)):
    """
    Récupère un fournisseur par son ID.
    """
    f = db.query(models.Fournisseur).get(fournisseur_id)
    if not f:
        raise HTTPException(status_code=404, detail="Fournisseur non trouvé")
    return f

@router.put("/{fournisseur_id}", response_model=schemas.FournisseurRead)
def update_fournisseur(
    fournisseur_id: int,
    data: schemas.FournisseurCreate,
    db: Session = Depends(get_db)
):
    """
    Met à jour un fournisseur existant.
    """
    f = db.query(models.Fournisseur).get(fournisseur_id)
    if not f:
        raise HTTPException(status_code=404, detail="Fournisseur non trouvé")
    for key, value in data.dict().items():
        setattr(f, key, value)
    db.commit()
    db.refresh(f)
    return f

@router.delete("/{fournisseur_id}")
def delete_fournisseur(fournisseur_id: int, db: Session = Depends(get_db)):
    """
    Supprime un fournisseur par son ID.
    """
    f = db.query(models.Fournisseur).get(fournisseur_id)
    if not f:
        raise HTTPException(status_code=404, detail="Fournisseur non trouvé")
    db.delete(f)
    db.commit()
    return {"message": "Fournisseur supprimé"}
