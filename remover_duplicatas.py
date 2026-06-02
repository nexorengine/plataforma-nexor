"""
NEXOR — REMOVEDOR DE DUPLICATAS v1
Lê o relatório do verificar_duplicatas.py e remove questões duplicadas
dos arquivos JSON, renumerando e registrando slots vazios para reposição.

USO:
    python remover_duplicatas.py

SAÍDA:
    - Arquivos JSON corrigidos (in-place com backup)
    - slots_vazios_YYYYMMDD_HHMM.txt (relatório de reposição)
    - remocao_log_YYYYMMDD_HHMM.txt  (log auditável de cada remoção)
"""

import os
import json
import shutil
import re
from datetime import datetime
from collections import defaultdict
from glob import glob

# ─────────────────────────────────────────────────────────────
# CONFIGURAÇÃO
# ─────────────────────────────────────────────────────────────
QUIZZES_DIR   = "static/quizzes"
REPORT_GLOB   = "duplicatas_report_*.txt"   # pega o mais recente
BACKUP_SUFFIX = ".bak"
TIMESTAMP     = datetime.now().strftime("%Y%m%d_%H%M")

SLOTS_FILE = f"slots_vazios_{TIMESTAMP}.txt"
LOG_FILE   = f"remocao_log_{TIMESTAMP}.txt"

# ─────────────────────────────────────────────────────────────
# UTILITÁRIOS
# ─────────────────────────────────────────────────────────────

def find_latest_report():
    reports = sorted(glob(REPORT_GLOB))
    if not reports:
        raise FileNotFoundError(
            "Nenhum relatório duplicatas_report_*.txt encontrado.\n"
            "Rode verificar_duplicatas.py primeiro."
        )
    return reports[-1]


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def backup(path):
    bak = path + BACKUP_SUFFIX
    if not os.path.exists(bak):          # não sobrescreve backup anterior
        shutil.copy2(path, bak)


def quiz_path(cert_id, domain_id, quiz_num, lang):
    fname = f"quiz_{quiz_num:03d}_{lang}.json"
    return os.path.join(QUIZZES_DIR, cert_id, domain_id, fname)


# ─────────────────────────────────────────────────────────────
# PARSER DO RELATÓRIO
# ─────────────────────────────────────────────────────────────

def parse_report(report_path):
    """
    Retorna dois dicts:
        intra[filepath] = set de índices (0-based) a remover
        inter[filepath] = set de índices (0-based) a remover
    """
    intra = defaultdict(set)   # {filepath: {q_idx, ...}}
    inter = defaultdict(set)

    with open(report_path, encoding="utf-8") as f:
        content = f.read()

    # ── SECÇÃO 2: INTRA-QUIZ ─────────────────────────────────
    # [INTRA-DUP] static\quizzes\cert\domain\quiz_NNN_lang.json
    #             Q16 e Q21 — texto IDENTICO: '...'
    intra_pat = re.compile(
        r"\[INTRA-DUP\]\s+(static[\\/]quizzes[\\/][^\n]+\.json)\s+"
        r"Q(\d+)\s+e\s+Q(\d+)\s+",
        re.MULTILINE
    )
    for m in intra_pat.finditer(content):
        raw_path = m.group(1).replace("\\", os.sep).replace("/", os.sep)
        q_keep   = int(m.group(2))   # primeira — mantém
        q_remove = int(m.group(3))   # segunda  — remove
        intra[raw_path].add(q_remove - 1)   # converter para 0-based

    # ── SECÇÃO 3: INTER-QUIZ ─────────────────────────────────
    # [INTER-DUP] cert/domain [lang]
    #             quiz_NNN QXX  X  quiz_MMM QYY
    inter_pat = re.compile(
        r"\[INTER-DUP\]\s+(\S+)/(\S+)\s+\[(\w+)\]\s+"
        r"quiz_(\d+)\s+Q(\d+)\s+X\s+quiz_(\d+)\s+Q(\d+)",
        re.MULTILINE
    )
    for m in inter_pat.finditer(content):
        cert_id   = m.group(1)
        domain_id = m.group(2)
        lang      = m.group(3)
        q1_quiz   = int(m.group(4));  q1_num = int(m.group(5))
        q2_quiz   = int(m.group(6));  q2_num = int(m.group(7))

        # Regra: remove do quiz de número MAIOR (preserva o mais antigo)
        # Se mesmo quiz → já tratado pelo intra (não duplica)
        if q1_quiz == q2_quiz:
            continue

        if q1_quiz < q2_quiz:
            remove_quiz, remove_qnum = q2_quiz, q2_num
        else:
            remove_quiz, remove_qnum = q1_quiz, q1_num

        fpath = quiz_path(cert_id, domain_id, remove_quiz, lang)
        fpath = fpath.replace("/", os.sep).replace("\\", os.sep)
        inter[fpath].add(remove_qnum - 1)   # 0-based

    return intra, inter


# ─────────────────────────────────────────────────────────────
# PROCESSAMENTO
# ─────────────────────────────────────────────────────────────

def remove_questions(filepath, indices_to_remove, log_lines, slots_lines):
    """
    Remove as questões nos índices (0-based) indicados,
    renumera as restantes e salva o arquivo.
    """
    if not os.path.exists(filepath):
        log_lines.append(f"  [AVISO] Arquivo não encontrado: {filepath}")
        return 0

    data = load_json(filepath)
    questions = data.get("questions", [])
    total_before = len(questions)

    # Garante que os índices estão dentro do range
    valid_indices = {i for i in indices_to_remove if 0 <= i < total_before}
    if not valid_indices:
        log_lines.append(f"  [SKIP] {filepath} — índices fora do range")
        return 0

    backup(filepath)

    # Remove e renumera
    new_questions = []
    removed_nums  = []
    for i, q in enumerate(questions):
        if i in valid_indices:
            removed_nums.append(q.get("num", i + 1))
        else:
            new_questions.append(q)

    # Renumera sequencialmente
    for idx, q in enumerate(new_questions):
        q["num"] = idx + 1

    slots_removed = len(valid_indices)
    data["questions"] = new_questions
    save_json(filepath, data)

    # Log auditável
    log_lines.append(f"  [OK] {filepath}")
    log_lines.append(f"       Removidas: Q{sorted(removed_nums)} | Antes: {total_before} | Depois: {len(new_questions)}")

    # Registro de slots vazios
    cert_domain = os.sep.join(filepath.split(os.sep)[-3:-1])   # cert/domain
    fname       = os.path.basename(filepath)
    slots_lines.append(f"{cert_domain}/{fname}  →  {slots_removed} slot(s) a repor")

    return slots_removed


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print(f"  NEXOR — REMOVEDOR DE DUPLICATAS v1")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)

    # 1. Localiza relatório
    report = find_latest_report()
    print(f"\n  Relatório: {report}")

    # 2. Parse
    intra, inter = parse_report(report)

    # Consolida: une intra + inter por filepath
    all_removals = defaultdict(set)
    for fp, idxs in intra.items():
        all_removals[fp] |= idxs
    for fp, idxs in inter.items():
        all_removals[fp] |= idxs

    if not all_removals:
        print("\n  Nenhuma remoção necessária. Sistema limpo.")
        return

    print(f"\n  Arquivos a corrigir: {len(all_removals)}")
    print("-" * 70)

    log_lines   = [f"NEXOR — REMOVEDOR DE DUPLICATAS — {TIMESTAMP}", ""]
    slots_lines = [
        f"NEXOR — SLOTS VAZIOS PARA REPOSIÇÃO — {TIMESTAMP}",
        f"Relatório base: {report}",
        "",
        "ARQUIVO                                              SLOTS",
        "-" * 70,
    ]

    total_removed = 0
    files_modified = 0

    for filepath, indices in sorted(all_removals.items()):
        n = remove_questions(filepath, indices, log_lines, slots_lines)
        if n > 0:
            total_removed  += n
            files_modified += 1
            print(f"  ✓ {os.path.basename(filepath):45s}  -{n}q")

    # Salva logs
    slots_lines += [
        "",
        "-" * 70,
        f"TOTAL DE SLOTS VAZIOS: {total_removed}",
        f"(cada slot = 1 questão a gerar via API para fechar os 50 por quiz)",
    ]

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))

    with open(SLOTS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(slots_lines))

    # Resumo final
    print("\n" + "=" * 70)
    print(f"  CONCLUÍDO")
    print(f"  Arquivos modificados : {files_modified}")
    print(f"  Questões removidas   : {total_removed}")
    print(f"  Slots para reposição : {total_removed}")
    print(f"  Log de remoção       : {LOG_FILE}")
    print(f"  Relatório de slots   : {SLOTS_FILE}")
    print("=" * 70)
    print()
    print("  PRÓXIMO PASSO:")
    print("  1. python verificar_duplicatas.py   ← confirmar zero problemas")
    print("  2. Enviar slots_vazios ao ARAGORN   ← gerar questões de reposição")
    print("=" * 70)


if __name__ == "__main__":
    main()
