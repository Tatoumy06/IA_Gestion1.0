# backend/routers/factures.py

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.responses import FileResponse
import io
from reportlab.pdfgen import canvas

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
    response_model=schemas.FactureRead,
    status_code=status.HTTP_201_CREATED
)
def create_facture(
    facture_in: schemas.FactureCreate,
    db: Session = Depends(get_db)
):
    """
    Crée une nouvelle facture avec ses lignes.
    """
    # Vérifier que le client existe
    client = db.query(models.Client).get(facture_in.client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client non trouvé"
        )
    # Créer l'entité Facture
    facture = models.Facture(
        numero_facture=facture_in.numero_facture,
        client_id=facture_in.client_id,
        informations_complementaires=facture_in.informations_complementaires
    )
    db.add(facture)
    db.commit()
    db.refresh(facture)

    # Ajouter les lignes
    for ligne_in in facture_in.lignes:
        ligne = models.FactureLigne(
            facture_id=facture.id,
            description=ligne_in.description,
            quantite=ligne_in.quantite,
            prix_unitaire_ht=ligne_in.prix_unitaire_ht,
            piece_id=ligne_in.piece_id
        )
        db.add(ligne)
    db.commit()
    db.refresh(facture)

    return facture

@router.get(
    "/search",
    response_model=List[schemas.FactureRead]
)
def search_factures(
    q: str = Query(..., description="Recherche par numéro ou nom client"),
    db: Session = Depends(get_db)
):
    """
    Recherche de factures par numéro ou nom de client (insensible à la casse).
    """
    like = f"%{q}%"
    return (
        db.query(models.Facture)
          .join(models.Client)
          .filter(
              models.Facture.numero_facture.ilike(like) |
              models.Client.nom.ilike(like)
          )
          .all()
    )

@router.get(
    "/{facture_id}",
    response_model=schemas.FactureRead
)
def get_facture(
    facture_id: int,
    db: Session = Depends(get_db)
):
    """
    Récupère une facture par son ID.
    """
    facture = db.query(models.Facture).get(facture_id)
    if not facture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facture non trouvée"
        )
    return facture

@router.get(
    "/{facture_id}/pdf",
    response_class=FileResponse
)
def facture_pdf(
    facture_id: int,
    db: Session = Depends(get_db)
):
    """
    Génère et renvoie le PDF de la facture.
    """
    facture = db.query(models.Facture).get(facture_id)
    if not facture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facture non trouvée"
        )

    # Création du PDF en mémoire
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.setFont("Helvetica", 12)
    y = 800
    c.drawString(50, y, f"Facture : {facture.numero_facture}")
    y -= 30
    c.drawString(50, y, f"Client : {facture.client.nom} {facture.client.prenom or ''}")
    y -= 30
    c.drawString(50, y, f"Date : {facture.date_creation.strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 40

    # Lignes de facture
    total = 0.0
    for ligne in facture.lignes:
        line_text = f"{ligne.description} x{ligne.quantite} @ {ligne.prix_unitaire_ht:.2f}€"
        c.drawString(50, y, line_text)
        total += ligne.quantite * ligne.prix_unitaire_ht
        y -= 20
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = 800

    # Total
    y -= 20
    c.drawString(50, y, f"Total HT : {total:.2f}€")

    c.showPage()
    c.save()
    buf.seek(0)

    return FileResponse(
        buf,
        media_type="application/pdf",
        filename=f"facture_{facture.numero_facture}.pdf"
    )

@router.delete(
    "/{facture_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_facture(
    facture_id: int,
    db: Session = Depends(get_db)
):
    """
    Supprime une facture et ses lignes par son ID.
    """
    facture = db.query(models.Facture).get(facture_id)
    if not facture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facture non trouvée"
        )
    db.delete(facture)
    db.commit()
    return None
