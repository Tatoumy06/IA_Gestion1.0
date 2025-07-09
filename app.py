# backend/app.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import databases, sqlalchemy, os
def get_database_url():
    # Configurer via variable d'environnement
    return os.getenv('DATABASE_URL', 'sqlite:///./db.sqlite')

database = databases.Database(get_database_url())
metadata = sqlalchemy.MetaData()

# Définition des tables
dossiers = sqlalchemy.Table(
    'dossiers', metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('titre', sqlalchemy.String, nullable=False),
    sqlalchemy.Column('description', sqlalchemy.Text),
    sqlalchemy.Column('statut', sqlalchemy.String),
)
taches = sqlalchemy.Table(
    'taches', metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('dossier_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('dossiers.id')),
    sqlalchemy.Column('description', sqlalchemy.String, nullable=False),
    sqlalchemy.Column('date_echeance', sqlalchemy.Date, nullable=False),
    sqlalchemy.Column('rappel_envoye', sqlalchemy.Boolean, default=False),
)
objectifs = sqlalchemy.Table(
    'objectifs_ca', metadata,
    sqlalchemy.Column('date', sqlalchemy.Date, primary_key=True),
    sqlalchemy.Column('objectif_ca', sqlalchemy.Float),
)

# ORM engine
engine = sqlalchemy.create_engine(
    get_database_url(), connect_args={"check_same_thread": False} if 'sqlite' in get_database_url() else {}
)
metadata.create_all(engine)

# Pydantic models
class Dossier(BaseModel):
    id: Optional[int]
    titre: str
    description: Optional[str]
    statut: Optional[str]

class Tache(BaseModel):
    id: Optional[int]
    dossier_id: int
    description: str
    date_echeance: str  # format YYYY-MM-DD
    rappel_envoye: Optional[bool] = False

class ObjectifCA(BaseModel):
    date: str
    objectif_ca: float

class QuestionIA(BaseModel):
    dossier_id: int
    message: str

class Conseil(BaseModel):
    conseil: str

app = FastAPI(title="Backend IA Gestion Entreprise")

# CORS pour le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Endpoints Dossiers
@app.get("/api/dossiers", response_model=List[Dossier])
async def list_dossiers():
    rows = await database.fetch_all(dossiers.select())
    return rows

@app.post("/api/dossiers", response_model=Dossier)
async def create_dossier(d: Dossier):
    query = dossiers.insert().values(titre=d.titre, description=d.description, statut=d.statut)
    d.id = await database.execute(query)
    return d

@app.get("/api/dossiers/{dossier_id}", response_model=Dossier)
async def get_dossier(dossier_id: int):
    row = await database.fetch_one(dossiers.select().where(dossiers.c.id == dossier_id))
    if not row:
        raise HTTPException(status_code=404, detail="Dossier non trouvé")
    return row

@app.put("/api/dossiers/{dossier_id}", response_model=Dossier)
async def update_dossier(dossier_id: int, d: Dossier):
    await database.execute(
        dossiers.update().where(dossiers.c.id == dossier_id)
        .values(titre=d.titre, description=d.description, statut=d.statut)
    )
    return {**d.dict(), "id": dossier_id}

# Endpoints Tâches / Planning
@app.get("/api/planning", response_model=List[Tache])
async def get_planning(start_date: str, end_date: str):
    query = taches.select().where(
        taches.c.date_echeance.between(start_date, end_date)
    )
    return await database.fetch_all(query)

# Endpoint Objectif CA
@app.get("/api/comptabilite/objectif-ca", response_model=ObjectifCA)
async def get_objectif_ca(date: str):
    row = await database.fetch_one(objectifs.select().where(objectifs.c.date == date))
    if not row:
        return {"date": date, "objectif_ca": None}
    return row

# Endpoint IA Conseil
import openai
openai.api_key = os.getenv('OPENAI_API_KEY', '')

@app.post("/api/ia/conseil", response_model=Conseil)
async def ia_conseil(q: QuestionIA):
    # Récupérer le dossier
    dossier = await database.fetch_one(dossiers.select().where(dossiers.c.id == q.dossier_id))
    context = f"Dossier #{dossier['id']} - {dossier['titre']}: {dossier['description']}"
    system_msg = {"role":"system","content":"Tu es un assistant professionnel pour la gestion de dossiers."}
    user_msg = {"role":"user","content":f"Contexte: {context}\nQuestion: {q.message}"}
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[system_msg, user_msg]
    )
    return {"conseil": resp.choices[0].message.content}

# Lancer via: uvicorn backend.app:app --reload

# worker/tasks.py
from celery import Celery
from datetime import date
import requests

celery = Celery(
    'tasks',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
)

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Rappel quotidien à 08:00
    sender.add_periodic_task(
        crontab(hour=8, minute=0),
        send_daily_reminders.s()
    )

@celery.task
def send_daily_reminders():
    today = date.today().isoformat()
    r = requests.get(f"http://localhost:8000/api/planning?start_date={today}&end_date={today}")
    for t in r.json():
        # Envoi notification (e-mail, push…)
        notify_user(t['dossier_id'], f"Rappel: {t['description']} prévu à {t['date_echeance']}")
        # Marquer comme envoyé (optionnel)
        requests.post(f"http://localhost:8000/api/taches/{t['id']}/mark_sent")

# Note: implémente notify_user et endpoint mark_sent côté API.
