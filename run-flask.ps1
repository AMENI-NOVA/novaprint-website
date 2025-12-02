Set-Location "C:\Apps"
.\venv\Scripts\Activate.ps1

function Start-FlaskServer {
    Write-Host "[Flask] Démarrage du serveur ($(Get-Date -Format 'HH:mm:ss'))."
    python app.py
    return $LASTEXITCODE
}

try {
    while ($true) {
        $exitCode = Start-FlaskServer
        if ($exitCode -eq 0 -or $exitCode -eq -1073741510 -or $exitCode -eq 3221225786) {
            Write-Host "[Flask] Serveur arrêté proprement (code $exitCode). Fin du script."
            break
        }

        Write-Warning "[Flask] Le serveur s'est arrêté avec le code $exitCode. Redémarrage dans 2 secondes..."
        Start-Sleep -Seconds 2
    }
}
finally {
    Write-Host "[Flask] Script terminé."
}
