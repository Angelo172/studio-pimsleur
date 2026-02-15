@echo off
color 0A
echo =========================================================
echo      LANCEMENT DE PIMSLEUR MAKER EN COURS...
echo =========================================================
echo.

:: 1. Lancer le serveur Python (Backend) dans une fenetre separee
start "Backend" cmd /k "cd /d ""C:\Users\LE SACRE\studio-pimsleur\backend"" && venv\Scripts\activate && python app.py"

:: 2. Lancer l'interface Vue.js (Frontend) dans une fenetre separee
start "Frontend" cmd /k "cd /d ""C:\Users\LE SACRE\studio-pimsleur\frontend"" && npm run dev"

:: 3. Patienter 4 secondes pour que les serveurs demarrent bien
echo Chargement des moteurs IA... Veuillez patienter...
timeout /t 4 /nobreak > NUL

:: 4. Ouvrir la page web automatiquement
start http://localhost:5173

exit