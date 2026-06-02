"""
limpar_projeto.py — NEXOR Project Cleanup
Move arquivos obsoletos para arquivo_morto sem deletar nada.
Gera relatório completo do que foi movido.

Uso:
    python limpar_projeto.py           # dry-run (mostra o que seria movido)
    python limpar_projeto.py --executar  # executa a limpeza
"""

import os
import re
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# ── CONFIG ────────────────────────────────────────────────────────────────────
PROJECT_DIR  = Path(r"C:\ARAGORN\aragorn_quiz")
DEPLOYS_DIR  = Path(r"C:\ARAGORN")
ARCHIVE_DIR  = Path(r"C:\ARAGORN\arquivo_morto") / datetime.now().strftime("%Y%m%d_%H%M%S")

# ── REGRAS DE LIMPEZA ─────────────────────────────────────────────────────────

# Padrões de arquivos na RAIZ do projeto para arquivar
ROOT_PATTERNS = [
    # Logs de operação
    r"remocao_log_\d+_\d+\.txt",
    r"reposicao_log_\d+_\d+\.txt",
    r"reposicionamento_log_\d+_\d+\.txt",
    r"regeneracao_truncadas_\d+_\d+\.txt",
    r"slots_vazios_\d+_\d+\.txt",
    r"scan_nexor_\d+_\d+\.txt",
    r"mapeamento_cfe_2026_\d+_\d+\.txt",
    # Backups de server.py
    r"server\.py\.backup\d*",
    r"server\.py\.bak.*",
    r"server\.py\.bak_.*",
    r"server\.py\.backup.*",
    r"server\.py\.bak_fix.*",
    # Arquivos temporários de controle de geração
    r"topicos_usados_.*\.json",
    # Backups de flashcards (pasta separada, não a raiz)
]

# Arquivos exatos para arquivar
ROOT_EXACT = [
    "fractal_flashcard_log.txt",
    "audit_flashcards_report.txt",
]

# Pastas para arquivar completamente
FOLDERS_TO_ARCHIVE = [
    "__pycache__",
]

# ZIPs de deploy na pasta C:\ARAGORN\
DEPLOY_ZIPS = [
    r"nexor_.*\.zip",
    r"nexor_clean.*",
    r"nexor_test.*",
]

# ── HELPERS ──────────────────────────────────────────────────────────────────

def match_any(name, patterns):
    for p in patterns:
        if re.fullmatch(p, name, re.IGNORECASE):
            return True
    return False

def archive(src: Path, base: Path, dry_run: bool, log: list):
    rel = src.relative_to(base)
    dest = ARCHIVE_DIR / rel
    if dry_run:
        log.append(f"  [DRY] {rel}")
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))
        log.append(f"  ✓ {rel}")

# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--executar", action="store_true", help="Executa a limpeza (padrão: dry-run)")
    args = parser.parse_args()
    dry_run = not args.executar

    if dry_run:
        print("=" * 64)
        print("  MODO DRY-RUN — nenhum arquivo será movido")
        print("  Use --executar para aplicar a limpeza")
        print("=" * 64)
    else:
        print("=" * 64)
        print(f"  EXECUTANDO LIMPEZA")
        print(f"  Arquivo morto: {ARCHIVE_DIR}")
        print("=" * 64)
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    log = []
    total = 0

    # 1. Arquivos na raiz do projeto
    print("\n[1] Logs e backups na raiz do projeto:")
    for item in sorted(PROJECT_DIR.iterdir()):
        if item.is_file():
            if match_any(item.name, ROOT_PATTERNS) or item.name in ROOT_EXACT:
                archive(item, PROJECT_DIR.parent, dry_run, log)
                total += 1

    # 2. Pastas para arquivar
    print("\n[2] Pastas temporárias:")
    for folder_name in FOLDERS_TO_ARCHIVE:
        folder = PROJECT_DIR / folder_name
        if folder.exists():
            if dry_run:
                count = sum(1 for _ in folder.rglob("*") if _.is_file())
                log.append(f"  [DRY] {folder_name}/ ({count} arquivos)")
            else:
                dest = ARCHIVE_DIR / folder_name
                shutil.move(str(folder), str(dest))
                log.append(f"  ✓ {folder_name}/")
            total += 1

    # 3. Pasta backup_flashcards_pre_fractal (backup já desnecessário após fractal)
    backup_fcd = PROJECT_DIR / "backup_flashcards_pre_fractal"
    if backup_fcd.exists():
        print("\n[3] Backup flashcards pré-fractal:")
        count = sum(1 for _ in backup_fcd.rglob("*") if _.is_file())
        if dry_run:
            log.append(f"  [DRY] backup_flashcards_pre_fractal/ ({count} arquivos)")
        else:
            dest = ARCHIVE_DIR / "backup_flashcards_pre_fractal"
            shutil.move(str(backup_fcd), str(dest))
            log.append(f"  ✓ backup_flashcards_pre_fractal/ ({count} arquivos)")
        total += 1

    # 4. ZIPs de deploy em C:\ARAGORN\
    print("\n[4] ZIPs de deploy em C:\\ARAGORN\\:")
    for item in sorted(DEPLOYS_DIR.iterdir()):
        if item.is_file() and item.suffix == ".zip":
            if match_any(item.name, DEPLOY_ZIPS):
                if dry_run:
                    log.append(f"  [DRY] {item.name}")
                else:
                    try:
                        dest = ARCHIVE_DIR / item.name
                        shutil.move(str(item), str(dest))
                        log.append(f"  ✓ {item.name}")
                    except Exception:
                        log.append(f"  ⚠ SKIP {item.name} (em uso — delete manualmente)")
                total += 1
        # pasta nexor_clean e nexor_test_static
        if item.is_dir() and re.match(r"nexor_(clean|test)", item.name):
            if dry_run:
                log.append(f"  [DRY] {item.name}/")
            else:
                try:
                    dest = ARCHIVE_DIR / item.name
                    shutil.move(str(item), str(dest))
                    log.append(f"  ✓ {item.name}/")
                except Exception:
                    log.append(f"  ⚠ SKIP {item.name}/ (em uso — delete manualmente)")
            total += 1

    # Relatório
    for line in log:
        print(line)

    print("\n" + "=" * 64)
    if dry_run:
        print(f"  {total} itens seriam movidos para arquivo_morto")
        print(f"  Execute com --executar para aplicar")
    else:
        print(f"  {total} itens movidos para:")
        print(f"  {ARCHIVE_DIR}")
    print("=" * 64)

if __name__ == "__main__":
    main()
