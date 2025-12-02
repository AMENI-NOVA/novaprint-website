@echo off
setlocal enabledelayedexpansion

cd /d C:\Apps
call ".\venv\Scripts\activate.bat"

:loop
echo [Flask] Démarrage du serveur (%time%)
python app.py
set "exitcode=%ERRORLEVEL%"

if "%exitcode%"=="0" (
    echo [Flask] Serveur arrêté proprement (code 0). Fin du script.
    goto :end
)

if "%exitcode%"=="-1073741510" (
    echo [Flask] Arrêt demandé (Ctrl+C). Fin du script.
    goto :end
)

echo [Flask] Le serveur a quitté avec le code %exitcode%. Redémarrage dans 2 secondes...
timeout /t 2 /nobreak >nul
goto :loop

:end
echo [Flask] Script terminé.
endlocal





