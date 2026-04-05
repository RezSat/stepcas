$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (!(Test-Path .venv\Scripts\Activate.ps1)) {
    Write-Host "Virtual environment missing. Create it first." -ForegroundColor Yellow
    exit 1
}

. .\.venv\Scripts\Activate.ps1

Write-Host "Starting OpenCode server..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root'; . .\.venv\Scripts\Activate.ps1; opencode serve --port 4027"

Start-Sleep -Seconds 3

Write-Host "Starting StepCAS company runner..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root'; . .\.venv\Scripts\Activate.ps1; python .\company\runner.py"

Write-Host "Company started."
