# backend/routers/comptabilite.py

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from .. import models
from ..database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/ca-mensuel")
def ca_mensuel(db: Session = Depends(get_db)):
    """
    Retourne le chiffre d'affaires total du mois en cours.
    """
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    total = (
        db.query(func.sum(models.FactureLigne.quantite * models.FactureLigne.prix_unitaire_ht))
          .join(models.Facture, models.Facture.id == models.FactureLigne.facture_id)
          .filter(models.Facture.date_creation >= month_start)
          .scalar()
    ) or 0.0
    return {"total_ca_mensuel": total}

@router.get("/depenses-par-fournisseur")
def depenses_par_fournisseur(db: Session = Depends(get_db)):
    """
    Retourne, pour chaque fournisseur, le total des dépenses (somme des lignes de factures liées aux pièces fournies).
    """
    results = (
        db.query(
            models.Fournisseur.nom.label("nom_fournisseur"),
            func.sum(models.FactureLigne.quantite * models.FactureLigne.prix_unitaire_ht).label("total_depense")
        )
        .join(models.Piece, models.Piece.fournisseur_id == models.Fournisseur.id)
        .join(models.FactureLigne, models.FactureLigne.piece_id == models.Piece.id)
        .group_by(models.Fournisseur.id)
        .all()
    )
    return [
        {"nom_fournisseur": nom, "total_depense": total or 0.0}
        for nom, total in results
    ]

@router.get("/ca-par-categorie")
def ca_par_categorie(db: Session = Depends(get_db)):
    """
    Retourne, pour chaque catégorie de pièce, le chiffre d'affaires généré.
    """
    results = (
        db.query(
            models.Piece.category.label("categorie"),
            func.sum(models.FactureLigne.quantite * models.FactureLigne.prix_unitaire_ht).label("total_ca")
        )
        .join(models.FactureLigne, models.FactureLigne.piece_id == models.Piece.id)
        .group_by(models.Piece.category)
        .all()
    )
    return [
        {"categorie": categorie, "total_ca": total or 0.0}
        for categorie, total in results
    ]

@router.get("/objectif-ca")
def objectif_ca(
    date: Optional[str] = Query(None, description="Date (YYYY-MM-DD) pour récupérer l'objectif de CA")
):
    """
    Renvoie l'objectif de chiffre d'affaires pour une date donnée.
    (Implémentation vide pour l'instant, renvoie null si pas d'objectif défini.)
    """
    # TODO: récupérer l'objectif depuis une table dédiée si nécessaire
    return {"objectif_ca": None}
