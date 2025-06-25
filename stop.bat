@echo off
echo Arret du serveur IA Gestion...
REM La commande taskkill force la fermeture de tous les processus pythonw.exe
taskkill /F /IM pythonw.exe
echo Serveur arrete.
pause