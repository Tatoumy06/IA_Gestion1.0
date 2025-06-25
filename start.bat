@echo off
REM Ce script lance le serveur Python et ouvre le navigateur.

echo Lancement du serveur Flask...
REM La commande "start" lance le serveur dans une nouvelle fenetre de terminal
REM ce qui permet a ce script de continuer son execution.
start "IA Gestion - Serveur" cmd /k python app.py

echo Attente de 3 secondes pour que le serveur demarre...
timeout /t 3 /nobreak > nul

echo Lancement de l'application dans le navigateur...
start http://127.0.0.1:8000/