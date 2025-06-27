@echo off
REM Ce script lance le serveur Python en arriere-plan et ouvre le navigateur.

echo Lancement du serveur Flask...
REM Utilisation de "start /B" pour lancer le processus en arriere-plan dans la meme fenetre,
REM et "pythonw.exe" pour qu'il n'ait pas de console. La combinaison le rend invisible.
start /B "" pythonw.exe app.py

echo Attente de 2 secondes pour que le serveur demarre...
timeout /t 2 /nobreak > nul

echo Lancement de l'application dans le navigateur...
start http://127.0.0.1:8000/