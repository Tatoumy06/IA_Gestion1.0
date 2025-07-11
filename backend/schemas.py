# File: backend/__init__.py
# This file can be empty to mark the package

# File: backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./ia_gestion.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# File: backend/models.py
import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class Client(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True)
    prenom = Column(String, nullable=True)
    telephone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    adresse = Column(String, nullable=True)
    code_postal = Column(String, nullable=True)
    ville = Column(String, nullable=True)
    pays = Column(String, nullable=True)
    factures = relationship('Facture', back_populates='client')
    planning_events = relationship('PlanningEvent', back_populates='client')

class Fournisseur(Base):
    __tablename__ = 'fournisseurs'
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True)
    contact_person = Column(String, nullable=True)
    telephone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    adresse = Column(String, nullable=True)
    delai_livraison_moyen = Column(Integer, nullable=True)
    pieces = relationship('Piece', back_populates='fournisseur')
    remises = relationship('RemiseFournisseur', back_populates='fournisseur')

class RemiseFournisseur(Base):
    __tablename__ = 'remises_fournisseur'
    id = Column(Integer, primary_key=True, index=True)
    fournisseur_id = Column(Integer, ForeignKey('fournisseurs.id'))
    piece_category = Column(String, nullable=False)
    remise_pourcentage = Column(Float, nullable=False)
    fournisseur = relationship('Fournisseur', back_populates='remises')

class Assureur(Base):
    __tablename__ = 'assureurs'
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True)
    contact_person = Column(String, nullable=True)
    telephone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    adresse = Column(String, nullable=True)
    delai_paiement_moyen = Column(Integer, nullable=True)

class Expert(Base):
    __tablename__ = 'experts'
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True)
    contact_person = Column(String, nullable=True)
    telephone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    adresse = Column(String, nullable=True)
    delai_reponse_moyen = Column(Integer, nullable=True)

class Technicien(Base):
    __tablename__ = 'techniciens'
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True)
    prenom = Column(String)
    adresse = Column(String)
    code_postal = Column(String)
    ville = Column(String)
    date_naissance = Column(DateTime)
    email = Column(String)
    telephone = Column(String)
    numero_technicien = Column(String, unique=True, index=True)

class Piece(Base):
    __tablename__ = 'pieces'
    id = Column(Integer, primary_key=True, index=True)
    designation = Column(String, index=True)
    ref = Column(String, nullable=True, index=True)
    prix_achat = Column(Float, nullable=True)
    prix_vente = Column(Float, nullable=False)
    category = Column(String, nullable=True)
    fournisseur_id = Column(Integer, ForeignKey('fournisseurs.id'))
    fournisseur = relationship('Fournisseur', back_populates='pieces')

class MainDoeuvre(Base):
    __tablename__ = 'maindoeuvre'
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    taux_horaire = Column(Float, nullable=False)

class PlanningEvent(Base):
    __tablename__ = 'planning'
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    start_datetime = Column(DateTime, default=datetime.datetime.utcnow)
    work_description = Column(Text)
    technician_name = Column(String)
    car_registration = Column(String)
    client = relationship('Client', back_populates='planning_events')

class Facture(Base):
    __tablename__ = 'factures'
    id = Column(Integer, primary_key=True, index=True)
    numero_facture = Column(String, unique=True, index=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    date_creation = Column(DateTime, default=datetime.datetime.utcnow)
    informations_complementaires = Column(Text, nullable=True)
    client = relationship('Client', back_populates='factures')
    lignes = relationship('FactureLigne', back_populates='facture', cascade='all, delete')

class FactureLigne(Base):
    __tablename__ = 'facture_lignes'
    id = Column(Integer, primary_key=True, index=True)
    facture_id = Column(Integer, ForeignKey('factures.id'))
    description = Column(Text)
    quantite = Column(Float)
    prix_unitaire_ht = Column(Float)
    piece_id = Column(Integer, ForeignKey('pieces.id'), nullable=True)
    facture = relationship('Facture', back_populates='lignes')

# File: backend/schemas.py
from pydantic import BaseModel
from typing import Optional, List
import datetime

class ClientBase(BaseModel):
    nom: str
    prenom: Optional[str]
    telephone: Optional[str]
    email: Optional[str]
    adresse: Optional[str]
    code_postal: Optional[str]
    ville: Optional[str]
    pays: Optional[str]

class ClientCreate(ClientBase):
    pass

class ClientRead(ClientBase):
    id: int
    class Config:
        orm_mode = True

class FournisseurBase(BaseModel):
    nom: str
    contact_person: Optional[str]
    telephone: Optional[str]
    email: Optional[str]
    adresse: Optional[str]
    delai_livraison_moyen: Optional[int]

class FournisseurCreate(FournisseurBase):
    pass

class FournisseurRead(FournisseurBase):
    id: int
    class Config:
        orm_mode = True

class RemiseFournisseurBase(BaseModel):
    piece_category: str
    remise_pourcentage: float

class RemiseFournisseurCreate(RemiseFournisseurBase):
    pass

class RemiseFournisseurRead(RemiseFournisseurBase):
    id: int
    fournisseur_id: int
    class Config:
        orm_mode = True

class AssureurBase(BaseModel):
    nom: str
    contact_person: Optional[str]
    telephone: Optional[str]
    email: Optional[str]
    adresse: Optional[str]
    delai_paiement_moyen: Optional[int]

class AssureurCreate(AssureurBase):
    pass

class AssureurRead(AssureurBase):
    id: int
    class Config:
        orm_mode = True

class ExpertBase(BaseModel):
    nom: str
    contact_person: Optional[str]
    telephone: Optional[str]
    email: Optional[str]
    adresse: Optional[str]
    delai_reponse_moyen: Optional[int]

class ExpertCreate(ExpertBase):
    pass

class ExpertRead(ExpertBase):
    id: int
    class Config:
        orm_mode = True

class TechnicienBase(BaseModel):
    nom: str
    prenom: str
    adresse: str
    code_postal: str
    ville: str
    date_naissance: datetime.datetime
    email: str
    telephone: str
    numero_technicien: str

class TechnicienCreate(TechnicienBase):
    pass

class TechnicienRead(TechnicienBase):
    id: int
    class Config:
        orm_mode = True

class PieceBase(BaseModel):
    designation: str
    ref: Optional[str]
    prix_achat: Optional[float]
    prix_vente: float
    category: Optional[str]
    fournisseur_id: int

class PieceCreate(PieceBase):
    pass

class PieceRead(PieceBase):
    id: int
    class Config:
        orm_mode = True

class MainDoeuvreBase(BaseModel):
    description: str
    taux_horaire: float

class MainDoeuvreCreate(MainDoeuvreBase):
    pass

class MainDoeuvreRead(MainDoeuvreBase):
    id: int
    class Config:
        orm_mode = True

class PlanningEventBase(BaseModel):
    client_id: int
    start_datetime: datetime.datetime
    work_description: str
    technician_name: str
    car_registration: str

class PlanningEventCreate(PlanningEventBase):
    pass

class PlanningEventRead(PlanningEventBase):
    id: int
    class Config:
        orm_mode = True

class FactureLigneBase(BaseModel):
    description: str
    quantite: float
    prix_unitaire_ht: float
    piece_id: Optional[int]

class FactureLigneCreate(FactureLigneBase):
    pass

class FactureLigneRead(FactureLigneBase):
    id: int
    class Config:
        orm_mode = True

class FactureBase(BaseModel):
    numero_facture: str
    client_id: int
    informations_complementaires: Optional[str]
    lignes: List[FactureLigneCreate]

class FactureCreate(FactureBase):
    pass

class FactureRead(FactureBase):
    id: int
    date_creation: datetime.datetime
    lignes: List[FactureLigneRead]
    class Config:
        orm_mode = True

# File: backend/main.py
from fastapi import FastAPI
from .database import engine, Base
from .routers import (
    clients, fournisseurs, remises_fournisseur,
    assureurs, experts, techniciens,
    pieces, maindoeuvre, planning,
    factures, comptabilite
)

app = FastAPI(title="IA Gestion API")
# Create all tables once
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(clients.router, prefix="/api/clients", tags=["clients"])
app.include_router(fournisseurs.router, prefix="/api/fournisseurs", tags=["fournisseurs"])
app.include_router(remises_fournisseur.router, prefix="/api/remises", tags=["remises_fournisseur"])
app.include_router(assureurs.router, prefix="/api/assureurs", tags=["assureurs"])
app.include_router(experts.router, prefix="/api/experts", tags=["experts"])
app.include_router(techniciens.router, prefix="/api/techniciens", tags=["techniciens"])
app.include_router(pieces.router, prefix="/api/pieces", tags=["pieces"])
app.include_router(maindoeuvre.router, prefix="/api/maindoeuvre", tags=["maindoeuvre"])
app.include_router(planning.router, prefix="/api/planning", tags=["planning"])
app.include_router(factures.router, prefix="/api/factures", tags=["factures"])
app.include_router(comptabilite.router, prefix="/api/comptabilite", tags=["comptabilite"])
