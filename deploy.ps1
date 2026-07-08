#Requires -Version 5.1
<#
.SYNOPSIS
  Sincroniza content/ e publica o prototipo-med no GitHub Pages (gh-pages).

.USAGE
  .\deploy.ps1          # sync completo + deploy
  .\deploy.ps1 -Area cg # sync so de CG + deploy
  .\deploy.ps1 -Sync    # so sincroniza, sem deploy
  .\deploy.ps1 -Deploy  # so faz deploy (sem sync)
#>
param(
  [string]$Area = "all",
  [switch]$Sync,
  [switch]$Deploy
)

$REPO = "C:\ARAGORN\aragorn_quiz"
$ErrorActionPreference = "Stop"

# Se nenhuma flag especifica, faz os dois
if (-not $Sync -and -not $Deploy) { $Sync = $true; $Deploy = $true }

if ($Sync) {
  Write-Host "`n[1/2] Sincronizando content/ com os bancos do git..."
  & "$REPO\sync_content.ps1" -Area $Area
}

if ($Deploy) {
  Write-Host "`n[2/2] Publicando no GitHub Pages..."

  # Commita tudo que mudou em prototipo-med/content/
  $changed = git -C $REPO status --short "prototipo-med/content/"
  if ($changed) {
    git -C $REPO add "prototipo-med/content/"
    git -C $REPO commit -m "chore: sync content — $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    Write-Host "  commit: content atualizado"
  } else {
    Write-Host "  content sem mudancas, pulando commit"
  }

  # Subtree push para gh-pages
  Write-Host "  calculando SHA do subtree..."
  $sha = git -C $REPO subtree split --prefix prototipo-med HEAD
  Write-Host "  SHA: $sha"
  Write-Host "  fazendo push para gh-pages..."
  git -C $REPO push origin "${sha}:gh-pages" --force
  Write-Host "`nDeploy concluido! Site em: https://nexorengine.github.io/plataforma-nexor/"
}
