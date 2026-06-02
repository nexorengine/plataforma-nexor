"""
NEXOR -- LIMPEZA DEFINITIVA LEGACY CFE v1
Transforma os dominios legacy em padrão novo:

  fraud_investigation:
    Mantém quiz_001, 005, 006 (50q) → renumera 001, 002, 003
    Deleta quiz_002, 003, 004 (incompletos)

  prevention_deterrence:
    Mantém quiz_003, 005, 006 (50q) → renumera 001, 002, 003
    Deleta quiz_001, 002, 004, 007 (incompletos)

  financial_transactions:
    Deleta todos (conteúdo já reposicionado nos novos domínios)

  law:
    Move quiz_001 para law_cfe como quiz_011

USO:
    python limpar_legacy_definitivo.py
"""

import json
import os
import shutil
from pathlib import Path
from datetime import datetime

QUIZZES_DIR = r"static\quizzes\cfe"
TIMESTAMP   = datetime.now().strftime("%Y%m%d_%H%M")

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def backup_dir(domain_id):
    """Faz backup do diretorio inteiro antes de modificar."""
    src = Path(QUIZZES_DIR) / domain_id
    bak = Path(QUIZZES_DIR) / f"{domain_id}_bak_{TIMESTAMP}"
    if src.exists():
        shutil.copytree(str(src), str(bak))
        print(f"  Backup: {bak}")

def delete_quiz(domain_id, quiz_num):
    """Deleta os 3 arquivos de um quiz (en, pt, es)."""
    base = Path(QUIZZES_DIR) / domain_id
    deleted = 0
    for lang in ["en", "pt", "es"]:
        f = base / f"quiz_{quiz_num:03d}_{lang}.json"
        if f.exists():
            os.remove(str(f))
            deleted += 1
    return deleted

def rename_quiz(domain_id, old_num, new_num):
    """Renomeia quiz e atualiza quiz_num interno."""
    base = Path(QUIZZES_DIR) / domain_id
    for lang in ["en", "pt", "es"]:
        old_f = base / f"quiz_{old_num:03d}_{lang}.json"
        new_f = base / f"quiz_{new_num:03d}_{lang}.json"
        if old_f.exists():
            data = load_json(str(old_f))
            data["quiz_num"] = new_num
            save_json(str(new_f), data)
            os.remove(str(old_f))
            print(f"  {lang.upper()}: quiz_{old_num:03d} → quiz_{new_num:03d} ({len(data['questions'])}q)")

def move_quiz(src_domain, src_num, dst_domain, dst_num):
    """Move quiz de um dominio para outro."""
    src_base = Path(QUIZZES_DIR) / src_domain
    dst_base = Path(QUIZZES_DIR) / dst_domain
    dst_base.mkdir(parents=True, exist_ok=True)

    for lang in ["en", "pt", "es"]:
        src_f = src_base / f"quiz_{src_num:03d}_{lang}.json"
        dst_f = dst_base / f"quiz_{dst_num:03d}_{lang}.json"
        if src_f.exists():
            data = load_json(str(src_f))
            data["domain_id"] = dst_domain
            data["quiz_num"]  = dst_num
            save_json(str(dst_f), data)
            os.remove(str(src_f))
            print(f"  {lang.upper()}: {src_domain}/quiz_{src_num:03d} → {dst_domain}/quiz_{dst_num:03d} ({len(data['questions'])}q)")

def delete_all_quizzes(domain_id):
    """Deleta todos os quizzes de um dominio (mantém a pasta)."""
    base = Path(QUIZZES_DIR) / domain_id
    if not base.exists():
        return 0
    deleted = 0
    for f in base.iterdir():
        if f.suffix == ".json" and "bak" not in f.name:
            os.remove(str(f))
            deleted += 1
    return deleted

def main():
    print("=" * 70)
    print("  NEXOR -- LIMPEZA DEFINITIVA LEGACY CFE v1")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)

    # ─── 1. FRAUD_INVESTIGATION ───────────────────────────────────────────────
    print(f"\n{'─'*70}")
    print("  FRAUD_INVESTIGATION")
    print(f"{'─'*70}")
    backup_dir("fraud_investigation")

    # Deleta incompletos
    for num in [2, 3, 4]:
        n = delete_quiz("fraud_investigation", num)
        if n: print(f"  Deletado: quiz_{num:03d} ({n} arquivos)")

    # Renumera completos
    # quiz_005 → quiz_002
    rename_quiz("fraud_investigation", 5, 2)
    # quiz_006 → quiz_003
    rename_quiz("fraud_investigation", 6, 3)
    print("  fraud_investigation: quiz_001, quiz_002, quiz_003 (3×50q)")

    # ─── 2. PREVENTION_DETERRENCE ─────────────────────────────────────────────
    print(f"\n{'─'*70}")
    print("  PREVENTION_DETERRENCE")
    print(f"{'─'*70}")
    backup_dir("prevention_deterrence")

    # Deleta incompletos
    for num in [1, 2, 4, 7]:
        n = delete_quiz("prevention_deterrence", num)
        if n: print(f"  Deletado: quiz_{num:03d} ({n} arquivos)")

    # Renumera completos
    # quiz_003 → quiz_001
    rename_quiz("prevention_deterrence", 3, 1)
    # quiz_005 → quiz_002
    rename_quiz("prevention_deterrence", 5, 2)
    # quiz_006 → quiz_003
    rename_quiz("prevention_deterrence", 6, 3)
    print("  prevention_deterrence: quiz_001, quiz_002, quiz_003 (3×50q)")

    # ─── 3. FINANCIAL_TRANSACTIONS ────────────────────────────────────────────
    print(f"\n{'─'*70}")
    print("  FINANCIAL_TRANSACTIONS")
    print(f"{'─'*70}")
    backup_dir("financial_transactions")

    n = delete_all_quizzes("financial_transactions")
    print(f"  Deletados: {n} arquivos (conteudo ja reposicionado nos novos dominios)")

    # ─── 4. LAW → LAW_CFE ─────────────────────────────────────────────────────
    print(f"\n{'─'*70}")
    print("  LAW → LAW_CFE")
    print(f"{'─'*70}")
    backup_dir("law")

    # Descobre proximo numero disponivel em law_cfe
    law_cfe_base = Path(QUIZZES_DIR) / "law_cfe"
    existing = sorted(law_cfe_base.glob("quiz_*_en.json"))
    nums = []
    for f in existing:
        try:
            nums.append(int(f.name.split("_")[1]))
        except:
            pass
    next_num = max(nums) + 1 if nums else 11
    print(f"  Movendo law/quiz_001 → law_cfe/quiz_{next_num:03d}")
    move_quiz("law", 1, "law_cfe", next_num)

    # ─── VERIFICACAO FINAL ────────────────────────────────────────────────────
    print(f"\n{'─'*70}")
    print("  VERIFICACAO FINAL")
    print(f"{'─'*70}")

    for domain_id in ["fraud_investigation", "prevention_deterrence", "financial_transactions", "law_cfe"]:
        base = Path(QUIZZES_DIR) / domain_id
        if not base.exists():
            continue
        files = sorted([f for f in base.iterdir() if f.suffix == ".json" and "bak" not in f.name and "_en" in f.name])
        total_q = 0
        for f in files:
            data = load_json(str(f))
            total_q += len(data["questions"])
        print(f"  {domain_id}: {len(files)} quizzes EN · {total_q}q")

    print("\n" + "=" * 70)
    print("  CONCLUIDO")
    print("  Rode: python verificar_duplicatas.py")
    print("=" * 70)

if __name__ == "__main__":
    main()
