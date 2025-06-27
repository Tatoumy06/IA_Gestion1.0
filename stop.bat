@echo off
echo Arret du serveur IA Gestion...
REM La commande taskkill force la fermeture de tous les processus pythonw.exe (le serveur invisible)
taskkill /F /IM pythonw.exe >nul 2>&1
echo Serveur arrete.
pause