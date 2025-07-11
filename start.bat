@echo off
REM -------------------------------------------------------------------
REM start.bat — Démarrage du serveur FastAPI pour IA_Gestion1.0
REM -------------------------------------------------------------------

REM 1. Active l’environnement Conda nommé « tf310 »
call conda activate tf310

REM 2. Se positionne dans le dossier contenant ce script
pushd %~dp0

REM 3. Démarre Uvicorn sur le host et port souhaités
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

REM 4. Restaure le répertoire initial (optionnel)
popd
