#Requires -Version 5.1
<#
.SYNOPSIS
  Sincroniza content/quizzes/ e content/flashcards/ do prototipo-med
  com os bancos de conteudo do repositorio (quizzes/med/ e flashcards/med/).

.USAGE
  .\sync_content.ps1              # sincroniza tudo
  .\sync_content.ps1 -Area cg    # so cirurgia_geral
  .\sync_content.ps1 -Area go    # so gineco_obstetricia
  .\sync_content.ps1 -Dry        # mostra o que faria sem escrever
#>
param(
  [string]$Area = "all",
  [switch]$Dry
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$REPO  = "C:\ARAGORN\aragorn_quiz"
$DEST  = "$REPO\prototipo-med\content"
$UTF8  = [System.Text.Encoding]::UTF8

# ─── helpers ──────────────────────────────────────────────────────────────────

function GitShow($commit, $path) {
  try {
    $ErrorActionPreference = 'SilentlyContinue'
    $out = & git -C $REPO show "${commit}:${path}" 2>$null
    $ErrorActionPreference = 'Stop'
    if ($LASTEXITCODE -ne 0 -or -not $out) { return $null }
    return ($out -join "`n") | ConvertFrom-Json
  } catch { return $null }
  finally { $ErrorActionPreference = 'Stop' }
}

function WriteJson($path, $obj) {
  $json = $obj | ConvertTo-Json -Depth 8
  if ($Dry) { Write-Host "  [DRY] -> $path"; return }
  $dir = Split-Path $path -Parent
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  [System.IO.File]::WriteAllText($path, $json, $UTF8)
}

# ─── quiz converters ──────────────────────────────────────────────────────────

# CG: questions[], options["A. texto",...], correct=1-indexed int
function ConvertQuizCG($src) {
  $qs = $src.questions | ForEach-Object {
    $opts = $_.options | ForEach-Object { $_ -replace '^[A-D]\.\s*','' }
    [ordered]@{
      q   = $_.text
      opts= @($opts)
      c   = [int]$_.correct - 1
      exp = $_.justification_correct
    }
  }
  return $qs
}

# GO: questions[], options={A:"",B:"",C:"",D:""}, correct="B"
function ConvertQuizGO($src) {
  $qs = $src.questions | ForEach-Object {
    $opts = @($_.options.A, $_.options.B, $_.options.C, $_.options.D) | Where-Object { $_ }
    $letter = $_.correct.ToString().ToUpper()
    $idx = @('A','B','C','D').IndexOf($letter)
    [ordered]@{
      q   = $_.question
      opts= $opts
      c   = $idx
      exp = $_.explanation
    }
  }
  return $qs
}

# CM/PREV: questoes[], alternativas=["texto",...], correct=matching text
function ConvertQuizQuestoes($src) {
  $qs = $src.questoes | ForEach-Object {
    $alts = @($_.alternativas)
    $correctText = $_.correct
    $idx = -1
    for ($i = 0; $i -lt $alts.Count; $i++) {
      if ($alts[$i].Contains($correctText) -or $correctText.Contains($alts[$i])) {
        $idx = $i; break
      }
    }
    if ($idx -lt 0) { $idx = 0 } # fallback
    [ordered]@{
      q   = $_.pergunta
      opts= $alts
      c   = $idx
      exp = $_.justification_correct
    }
  }
  return $qs
}

# ─── flashcard converters ─────────────────────────────────────────────────────

# CG: flashcards key, {camada, frente, verso}
function ConvertFlashCG($src) {
  return $src.flashcards | ForEach-Object {
    [ordered]@{ l=$_.camada; f=$_.frente; v=$_.verso }
  }
}

# GO/CM/PREV: cards key, {layer, front, back}
function ConvertFlashCards($src) {
  return $src.cards | ForEach-Object {
    [ordered]@{ l=$_.layer; f=$_.front; v=$_.back }
  }
}

# ─── write quiz ───────────────────────────────────────────────────────────────

function SyncQuiz($area, $dominio, $quizNum, $src, $converter) {
  if (-not $src) { return }
  $pad = $quizNum.ToString().PadLeft(3,'0')
  $qs  = & $converter $src
  if (-not $qs -or $qs.Count -eq 0) { Write-Host "  SKIP quiz $pad (0 questions)"; return }
  $out = [ordered]@{
    area      = $area
    dominio   = $dominio
    quiz      = "quiz_$pad"
    total     = $qs.Count
    questions = @($qs)
  }
  $dest = "$DEST\quizzes\$area\$dominio\quiz_$pad.json"
  WriteJson $dest $out
  Write-Host "  quiz_$pad : $($qs.Count) questoes"
}

# ─── write flashcards ─────────────────────────────────────────────────────────

function SyncFlash($area, $dominio, $src, $converter) {
  if (-not $src) { return }
  $cards = & $converter $src
  if (-not $cards -or $cards.Count -eq 0) { Write-Host "  SKIP flash (0 cards)"; return }
  $out = [ordered]@{
    area   = $area
    dominio= $dominio
    total  = $cards.Count
    cards  = @($cards)
  }
  $dest = "$DEST\flashcards\$area\$dominio\flashcards.json"
  WriteJson $dest $out
  Write-Host "  flashcards : $($cards.Count) cards"
}

# ─── CIRURGIA GERAL ───────────────────────────────────────────────────────────

function SyncCG {
  Write-Host "`n=== CIRURGIA GERAL ==="

  # Commit que tinha os flashcards antes da limpeza
  $flashCommit = "76aa46e"

  $cgMap = @(
    [ordered]@{ d=1; slug="abdome_agudo";                                  qpfx="";      fpfx="" },
    [ordered]@{ d=2; slug="hepatobiliar_pancreas";                         qpfx="_d2";   fpfx="_d2" },
    [ordered]@{ d=3; slug="trauma_urgencia";                               qpfx="_d3";   fpfx="_d3" },
    [ordered]@{ d=4; slug="perioperatorio";                                qpfx="_d4";   fpfx="_d4" },
    [ordered]@{ d=5; slug="hernias_parede_abdominal";                      qpfx="_d5";   fpfx="_d5" },
    [ordered]@{ d=6; slug="trato_digestivo_superior";                      qpfx="_d6";   fpfx="_d6" },
    [ordered]@{ d=7; slug="trato_digestivo_inferior_coloproctologia";      qpfx="_d7";   fpfx="_d7" },
    [ordered]@{ d=8; slug="cirurgia_vascular";                             qpfx="_d8";   fpfx="_d8" },
    [ordered]@{ d=9; slug="queimaduras";                                   qpfx="_d9";   fpfx="_d9" }
  )

  foreach ($m in $cgMap) {
    $base = "quizzes/med/cirurgia_geral/quiz$($m.qpfx)"
    $q1 = GitShow "HEAD" "${base}_001_pt.json"
    $q2 = GitShow "HEAD" "${base}_002_pt.json"
    if (-not $q1 -and -not $q2) { continue }

    Write-Host "  D$($m.d) $($m.slug)"
    SyncQuiz "cirurgia_geral" $m.slug 1 $q1 ${Function:ConvertQuizCG}
    SyncQuiz "cirurgia_geral" $m.slug 2 $q2 ${Function:ConvertQuizCG}

    $flashPath = "static/flashcards/med/cirurgia_geral/flashcards$($m.fpfx)_pt.json"
    $flash = GitShow $flashCommit $flashPath
    SyncFlash "cirurgia_geral" $m.slug $flash ${Function:ConvertFlashCG}
  }
}

# ─── GINECO-OBSTETRICIA ───────────────────────────────────────────────────────

function SyncGO {
  Write-Host "`n=== GINECO-OBSTETRICIA ==="
  $flashCommit = "fad0521"

  $goSlugs = @(
    "pre_natal","parto_normal","puerperio_aleitamento","complicacoes_obstetricas",
    "ginecologia_geral","doencas_uterinas_anexiais","infeccoes_genitais_dsts",
    "cancer_ginecologico","uroginecologia_piso_pelvico"
  )

  foreach ($slug in $goSlugs) {
    $base = "quizzes/med/gineco_obstetricia/$slug"
    $q1 = GitShow "HEAD" "$base/quiz_001_pt.json"
    $q2 = GitShow "HEAD" "$base/quiz_002_pt.json"
    if (-not $q1 -and -not $q2) { continue }

    Write-Host "  $slug"
    SyncQuiz "gineco_obstetricia" $slug 1 $q1 ${Function:ConvertQuizGO}
    SyncQuiz "gineco_obstetricia" $slug 2 $q2 ${Function:ConvertQuizGO}

    $flash = GitShow "HEAD" "flashcards/med/gineco_obstetricia/$slug/flashcards_pt.json"
    if (-not $flash) { $flash = GitShow $flashCommit "flashcards/med/gineco_obstetricia/$slug/flashcards_pt.json" }
    SyncFlash "gineco_obstetricia" $slug $flash ${Function:ConvertFlashCards}
  }
}

# ─── CLINICA MEDICA ───────────────────────────────────────────────────────────

function SyncCM {
  Write-Host "`n=== CLINICA MEDICA ==="

  # Find commit that added CM D01 flashcards (before cleanup)
  $flashCommit = "b64af02"

  $cmMap = @(
    [ordered]@{ d=1;  slug="cardiologia";       prefix="CM_D01" },
    [ordered]@{ d=2;  slug="pneumologia";        prefix="CM_D02" },
    [ordered]@{ d=3;  slug="gastroenterologia";  prefix="CM_D03" },
    [ordered]@{ d=4;  slug="nefrologia";         prefix="CM_D04" },
    [ordered]@{ d=5;  slug="endocrinologia";     prefix="CM_D05" },
    [ordered]@{ d=6;  slug="hematologia";        prefix="CM_D06" },
    [ordered]@{ d=7;  slug="reumatologia";       prefix="CM_D07" },
    [ordered]@{ d=8;  slug="infectologia";       prefix="CM_D08" },
    [ordered]@{ d=9;  slug="neurologia";         prefix="CM_D09" }
  )

  foreach ($m in $cmMap) {
    $base = "quizzes/med/clinica_medica/$($m.slug)/$($m.prefix)"
    $q1 = GitShow "HEAD" "${base}_quiz_001_pt.json"
    $q2 = GitShow "HEAD" "${base}_quiz_002_pt.json"
    if (-not $q1 -and -not $q2) { continue }

    Write-Host "  $($m.slug)"
    SyncQuiz "clinica_medica" $m.slug 1 $q1 ${Function:ConvertQuizQuestoes}
    SyncQuiz "clinica_medica" $m.slug 2 $q2 ${Function:ConvertQuizQuestoes}

    $flash = GitShow "HEAD" "flashcards/med/clinica_medica/$($m.slug)/flashcards_pt.json"
    if (-not $flash) { $flash = GitShow $flashCommit "flashcards/med/clinica_medica/$($m.slug)/$($m.prefix)_flashcards_pt.json" }
    SyncFlash "clinica_medica" $m.slug $flash ${Function:ConvertFlashCards}
  }
}

# ─── MEDICINA PREVENTIVA ──────────────────────────────────────────────────────

function SyncPREV {
  Write-Host "`n=== MEDICINA PREVENTIVA ==="

  $prevMap = @(
    [ordered]@{ d=1;  slug="epidemiologia_geral";      prefix="PREV_D01" },
    [ordered]@{ d=2;  slug="vigilancia_epidemiologica"; prefix="PREV_D02" },
    [ordered]@{ d=3;  slug="imunizacao_pni";            prefix="PREV_D03" },
    [ordered]@{ d=4;  slug="bioestatistica";            prefix="PREV_D04" },
    [ordered]@{ d=5;  slug="saude_familia_aps";         prefix="PREV_D05" },
    [ordered]@{ d=6;  slug="politica_nacional_sus";     prefix="PREV_D06" },
    [ordered]@{ d=7;  slug="saude_ambiental_ocupacional"; prefix="PREV_D07" },
    [ordered]@{ d=8;  slug="dcnt_promocao_saude";       prefix="PREV_D08" },
    [ordered]@{ d=9;  slug="bioetica_etica_medica";     prefix="PREV_D09" }
  )

  foreach ($m in $prevMap) {
    $base = "quizzes/med/medicina_preventiva/$($m.slug)/$($m.prefix)"
    $q1 = GitShow "HEAD" "${base}_quiz_001_pt.json"
    $q2 = GitShow "HEAD" "${base}_quiz_002_pt.json"
    if (-not $q1 -and -not $q2) { continue }

    Write-Host "  $($m.slug)"
    SyncQuiz "medicina_preventiva" $m.slug 1 $q1 ${Function:ConvertQuizQuestoes}
    SyncQuiz "medicina_preventiva" $m.slug 2 $q2 ${Function:ConvertQuizQuestoes}

    $flash = GitShow "HEAD" "flashcards/med/medicina_preventiva/$($m.slug)/flashcards_pt.json"
    if (-not $flash) { $flash = GitShow "HEAD" "flashcards/med/medicina_preventiva/$($m.slug)/$($m.prefix)_flashcards_pt.json" }
    SyncFlash "medicina_preventiva" $m.slug $flash ${Function:ConvertFlashCards}
  }
}

# ─── PEDIATRIA ────────────────────────────────────────────────────────────────

function SyncPED {
  Write-Host "`n=== PEDIATRIA ==="

  $pedMap = @(
    [ordered]@{ slug="neonatologia";         prefix="PED_D01" },
    [ordered]@{ slug="puericultura";         prefix="PED_D02" },
    [ordered]@{ slug="pneumologia_ped";      prefix="PED_D03" },
    [ordered]@{ slug="gastro_ped";           prefix="PED_D04" },
    [ordered]@{ slug="infectologia_ped";     prefix="PED_D05" },
    [ordered]@{ slug="cardio_ped";           prefix="PED_D06" },
    [ordered]@{ slug="endocrinologia_ped";   prefix="PED_D07" },
    [ordered]@{ slug="hematologia_onco_ped"; prefix="PED_D08" },
    [ordered]@{ slug="emergencias_ped";      prefix="PED_D09" }
  )

  foreach ($m in $pedMap) {
    $base = "quizzes/med/pediatria/$($m.slug)"
    $q1 = GitShow "HEAD" "$base/quiz_001_pt.json"
    $q2 = GitShow "HEAD" "$base/quiz_002_pt.json"
    if (-not $q1 -and -not $q2) { continue }

    Write-Host "  $($m.slug)"
    SyncQuiz "pediatria" $m.slug 1 $q1 ${Function:ConvertQuizGO}
    SyncQuiz "pediatria" $m.slug 2 $q2 ${Function:ConvertQuizGO}

    $flash = GitShow "HEAD" "flashcards/med/pediatria/$($m.slug)/flashcards_pt.json"
    SyncFlash "pediatria" $m.slug $flash ${Function:ConvertFlashCards}
  }
}

# ─── MAIN ─────────────────────────────────────────────────────────────────────

$start = Get-Date
$dryLabel = if ($Dry) { '[DRY RUN] ' } else { '' }
Write-Host "sync_content.ps1 -- $dryLabel$(Get-Date -Format 'yyyy-MM-dd HH:mm')"

switch ($Area.ToLower()) {
  "cg"   { SyncCG }
  "go"   { SyncGO }
  "cm"   { SyncCM }
  "prev" { SyncPREV }
  "ped"  { SyncPED }
  "all"  { SyncCG; SyncGO; SyncCM; SyncPREV; SyncPED }
  default { Write-Host "Area invalida. Use: cg, go, cm, prev, all" }
}

$elapsed = ((Get-Date) - $start).TotalSeconds
Write-Host ("Concluido em " + [math]::Round($elapsed,1) + "s")
