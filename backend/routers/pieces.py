# backend/routers/pieces.py

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
    response_model=schemas.PieceRead,
    status_code=status.HTTP_201_CREATED
)
def create_piece(
    piece_in: schemas.PieceCreate,
    db: Session = Depends(get_db)
):
    """
    Crée une nouvelle pièce. Vérifie que le fournisseur existe.
    """
    if not db.query(models.Fournisseur).get(piece_in.fournisseur_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fournisseur non trouvé"
        )
    piece = models.Piece(**piece_in.dict())
    db.add(piece)
    db.commit()
    db.refresh(piece)
    return piece

@router.get(
    "/",
    response_model=List[schemas.PieceRead]
)
def list_pieces(
    q: Optional[str] = Query(None, description="Recherche par désignation ou référence"),
    db: Session = Depends(get_db)
):
    """
    Liste toutes les pièces, optionnellement filtrées par désignation ou ref.
    """
    query = db.query(models.Piece)
    if q:
        like = f"%{q}%"
        query = query.filter(
            models.Piece.designation.ilike(like) |
            models.Piece.ref.ilike(like)
        )
    return query.all()

@router.get(
    "/{piece_id}",
    response_model=schemas.PieceRead
)
def get_piece(
    piece_id: int,
    db: Session = Depends(get_db)
):
    """
    Récupère une pièce par son ID.
    """
    piece = db.query(models.Piece).get(piece_id)
    if not piece:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pièce non trouvée"
        )
    return piece

@router.put(
    "/{piece_id}",
    response_model=schemas.PieceRead
)
def update_piece(
    piece_id: int,
    piece_in: schemas.PieceCreate,
    db: Session = Depends(get_db)
):
    """
    Met à jour une pièce existante. Vérifie aussi le fournisseur.
    """
    piece = db.query(models.Piece).get(piece_id)
    if not piece:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pièce non trouvée"
        )
    if not db.query(models.Fournisseur).get(piece_in.fournisseur_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fournisseur non trouvé"
        )
    for key, value in piece_in.dict().items():
        setattr(piece, key, value)
    db.commit()
    db.refresh(piece)
    return piece

@router.delete(
    "/{piece_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_piece(
    piece_id: int,
    db: Session = Depends(get_db)
):
    """
    Supprime une pièce par son ID.
    """
    piece = db.query(models.Piece).get(piece_id)
    if not piece:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pièce non trouvée"
        )
    db.delete(piece)
    db.commit()
    return None

@router.post(
    "/search",
    response_model=List[schemas.PieceRead]
)
def search_pieces(
    designation: Optional[str] = None,
    ref: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Recherche de pièces par désignation et/ou référence.
    """
    query = db.query(models.Piece)
    if designation:
        query = query.filter(models.Piece.designation.ilike(f"%{designation}%"))
    if ref:
        query = query.filter(models.Piece.ref.ilike(f"%{ref}%"))
    return query.all()
