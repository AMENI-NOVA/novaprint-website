Write-Host "Enregistrement des composants Crystal Reports..." -ForegroundColor Green

# Vérifier si on est en mode administrateur
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "❌ Ce script doit être exécuté en tant qu'administrateur" -ForegroundColor Red
    exit
}

# Chemins possibles pour Crystal Reports
$crystalPaths = @(
    "${env:ProgramFiles(x86)}\SAP BusinessObjects\Crystal Reports for .NET Framework 4.0",
    "${env:ProgramFiles(x86)}\Business Objects\Common\4.0",
    "${env:ProgramFiles(x86)}\SAP BusinessObjects\Crystal Reports for .NET Framework 4.0\Common\SAP BusinessObjects Enterprise XI 4.0"
)

foreach ($basePath in $crystalPaths) {
    if (Test-Path $basePath) {
        Write-Host "`nTraitement du dossier: $basePath" -ForegroundColor Cyan
        
        # Rechercher toutes les DLL Crystal Reports
        Get-ChildItem -Path $basePath -Filter "cr*.dll" -Recurse | ForEach-Object {
            Write-Host "Enregistrement de $($_.FullName)" -ForegroundColor Yellow
            $result = Start-Process "regsvr32.exe" -ArgumentList "/s `"$($_.FullName)`"" -Wait -PassThru
            if ($result.ExitCode -eq 0) {
                Write-Host "✅ Succès" -ForegroundColor Green
            } else {
                Write-Host "❌ Échec (Code: $($result.ExitCode))" -ForegroundColor Red
            }
        }
    }
}

Write-Host "`nVérification des clés de registre..." -ForegroundColor Green
$regPaths = @(
    "HKLM:\SOFTWARE\Classes\CrystalRunTime.Application",
    "HKLM:\SOFTWARE\Classes\CrystalDesignRunTime.Application",
    "HKLM:\SOFTWARE\Classes\Crystal.Application"
)

foreach ($path in $regPaths) {
    if (Test-Path $path) {
        Write-Host "✅ Trouvé: $path" -ForegroundColor Green
    } else {
        Write-Host "❌ Manquant: $path" -ForegroundColor Red
    }
}

Write-Host "`nTerminé!" -ForegroundColor Green
