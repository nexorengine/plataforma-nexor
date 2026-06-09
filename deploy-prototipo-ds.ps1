$repo = "C:\ARAGORN\aragorn_quiz"
$zip  = "$env:USERPROFILE\Downloads\prototipo-ds.zip"
$dest = "$repo\prototipo-ds"

if (-not (Test-Path $zip)) {
    Write-Host "ERRO: nao encontrei $zip" -ForegroundColor Red
    exit 1
}

Write-Host "Extraindo..." -ForegroundColor Cyan
Expand-Archive -Path $zip -DestinationPath $repo -Force
Write-Host "OK" -ForegroundColor Green

Set-Location $repo
git add prototipo-ds/
git commit -m "prototipo-ds v1 — design system propagado"
git push origin main

Write-Host "Acesse: https://nexorengine.com/prototipo-ds/" -ForegroundColor Yellow
