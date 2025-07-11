# backend/main.py
from fastapi import FastAPI
from .database import engine, Base
from .routers import (
    clients,
    fournisseurs, 
    remises_fournisseurs,
    assureurs, 
    experts, 
    techniciens,
    pieces, 
    maindoeuvre, 
    planning,
    factures, 
    comptabilite, 
    factures
)

app = FastAPI(title="IA Gestion API")
Base.metadata.create_all(bind=engine)

app.include_router(clients.router,              prefix="/api/clients",       tags=["clients"])
app.include_router(fournisseurs.router,         prefix="/api/fournisseurs",  tags=["fournisseurs"])
app.include_router(remises_fournisseurs.router, prefix="/api",               tags=["remises_fournisseurs"])
app.include_router(assureurs.router,            prefix="/api/assureurs",     tags=["assureurs"])
app.include_router(experts.router,              prefix="/api/experts",       tags=["experts"])
app.include_router(techniciens.router,          prefix="/api/techniciens",   tags=["techniciens"])
app.include_router(pieces.router,               prefix="/api/pieces",        tags=["pieces"])
app.include_router(maindoeuvre.router,          prefix="/api/maindoeuvre",   tags=["maindoeuvre"])
app.include_router(planning.router,             prefix="/api/planning",      tags=["planning"])
app.include_router(factures.router,             prefix="/api/factures",      tags=["factures"])
app.include_router(comptabilite.router,         prefix="/api/comptabilite",  tags=["comptabilite"])

class Config: orm_mode = True

class FournisseurBase(BaseModel):
    nom: str
    contact_person: Optional[str]
    telephone: Optional[str]
    email: Optional[str]
    adresse: Optional[str]
    delai_livraison_moyen: Optional[int]

class FournisseurCreate(FournisseurBase): pass
class FournisseurRead(FournisseurBase):
    id: int
    class Config: orm_mode = True

class RemiseFournisseurBase(BaseModel):
    piece_category: str
    remise_pourcentage: float

class RemiseFournisseurCreate(RemiseFournisseurBase): pass
class RemiseFournisseurRead(RemiseFournisseurBase):
    id: int
    fournisseur_id: int
    class Config: orm_mode = True

class AssureurBase(BaseModel):
    nom: str
    contact_person: Optional[str]
    telephone: Optional[str]
    email: Optional[str]
    adresse: Optional[str]
    delai_paiement_moyen: Optional[int]

class AssureurCreate(AssureurBase): pass
class AssureurRead(AssureurBase):
    id: int
    class Config: orm_mode = True

class ExpertBase(BaseModel):
    nom: str
    contact_person: Optional[str]
    telephone: Optional[str]
    email: Optional[str]
    adresse: Optional[str]
    delai_reponse_moyen: Optional[int]

class ExpertCreate(ExpertBase): pass
class ExpertRead(ExpertBase):
    id: int
    class Config: orm_mode = True

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

class TechnicienCreate(TechnicienBase): pass
class TechnicienRead(TechnicienBase):
    id: int
    class Config: orm_mode = True

class PieceBase(BaseModel):
    designation: str
    ref: Optional[str]
    prix_achat: Optional[float]
    prix_vente: float
    category: Optional[str]
    fournisseur_id: int

class PieceCreate(PieceBase): pass
class PieceRead(PieceBase):
    id: int
    class Config: orm_mode = True

class MainDoeuvreBase(BaseModel):
    description: str
    taux_horaire: float

class MainDoeuvreCreate(MainDoeuvreBase): pass
class MainDoeuvreRead(MainDoeuvreBase):
    id: int
    class Config: orm_mode = True

class PlanningEventBase(BaseModel):
    client_id: int
    start_datetime: datetime.datetime
    work_description: str
    technician_name: str
    car_registration: str

class PlanningEventCreate(PlanningEventBase): pass
class PlanningEventRead(PlanningEventBase):
    id: int
    class Config: orm_mode = True

class FactureLigneBase(BaseModel):
    description: str
    quantite: float
    prix_unitaire_ht: float
    piece_id: Optional[int]

class FactureLigneCreate(FactureLigneBase): pass
class FactureLigneRead(FactureLigneBase):
    id: int
    class Config: orm_mode = True

class FactureBase(BaseModel):
    numero_facture: str
    client_id: int
    informations_complementaires: Optional[str]
    lignes: List[FactureLigneCreate]

class FactureCreate(FactureBase): pass
class FactureRead(FactureBase):
    id: int
    date_creation: datetime.datetime
    lignes: List[FactureLigneRead]
    class Config: orm_mode = True