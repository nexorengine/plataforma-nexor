"""
verificar_duplicatas.py  v2
Verifica duplicidade real de questoes e alternativas em todos os quizzes do NEXOR.
Usa hash do texto COMPLETO para evitar falsos positivos por inicio similar.

Uso:
    cd C:\\NEXOR\\nexor_quiz
    python verificar_duplicatas.py
"""

import json, re, hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict

QUIZ_DIR = Path("static/quizzes")
REPORT   = f"duplicatas_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"

linhas = []
def L(t=""): linhas.append(t)
def S(): L("=" * 70)
def H(t): S(); L(f"  {t}"); S()

total_quizzes     = 0
total_questoes    = 0
erros_alt         = 0
erros_intra       = 0
erros_inter       = 0
erros_gab         = 0
erros_just        = 0

# hash do texto completo (nao truncado)
def htext(t):
    return hashlib.md5(t.strip().lower().encode()).hexdigest()

# normaliza alternativa removendo prefixo "A. " "B. " etc
def norm_alt(s):
    return re.sub(r'^[A-Da-d]\.\s*', '', s).strip().lower()

S()
L(f"  NEXOR — VERIFICADOR DE DUPLICATAS v2")
L(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
S(); L()

arquivos = sorted(QUIZ_DIR.rglob("quiz_*.json"))
L(f"  Arquivos encontrados: {len(arquivos)}"); L()

# ── Carrega todos os dados ────────────────────────────────────────────────────
quizzes = []
for arq in arquivos:
    try:
        data = json.loads(arq.read_text(encoding="utf-8"))
        data["_arq"] = arq
        quizzes.append(data)
        total_quizzes += 1
        total_questoes += len(data.get("questions", []))
    except Exception as e:
        L(f"  [ERRO JSON] {arq}: {e}")

# ── 1. ALTERNATIVAS DUPLICADAS ────────────────────────────────────────────────
H("1. ALTERNATIVAS DUPLICADAS DENTRO DE UMA QUESTAO")
achou = False
for data in quizzes:
    arq  = data["_arq"]
    qnum = data.get("quiz_num", "?")
    for q in data.get("questions", []):
        num  = q.get("num", "?")
        opts = q.get("options", [])
        vistos = {}
        for i, op in enumerate(opts):
            chave = norm_alt(op)
            if chave in vistos:
                erros_alt += 1
                achou = True
                L(f"  [ALT-DUP] {arq}")
                L(f"            Q{num} — alternativas {vistos[chave]+1} e {i+1} identicas:")
                L(f"            '{opts[vistos[chave]]}' == '{op}'"); L()
            else:
                vistos[chave] = i
if not achou:
    L("  Nenhuma alternativa duplicada encontrada."); L()

# ── 2. QUESTOES DUPLICADAS DENTRO DO MESMO QUIZ (hash completo) ───────────────
H("2. QUESTOES DUPLICADAS DENTRO DO MESMO QUIZ (texto completo)")
achou = False
for data in quizzes:
    arq = data["_arq"]
    vistos = {}
    for q in data.get("questions", []):
        num   = q.get("num", "?")
        texto = q.get("text", "")
        h     = htext(texto)
        if h in vistos:
            erros_intra += 1
            achou = True
            L(f"  [INTRA-DUP] {arq}")
            L(f"              Q{vistos[h]} e Q{num} — texto IDENTICO:")
            L(f"              '{texto[:120]}'"); L()
        else:
            vistos[h] = num
if not achou:
    L("  Nenhuma questao identica dentro de um mesmo quiz."); L()

# ── 3. QUESTOES DUPLICADAS ENTRE QUIZZES (mesmo cert/domain/lang) ─────────────
H("3. QUESTOES IDENTICAS ENTRE QUIZZES DO MESMO DOMINIO E IDIOMA")
achou = False
# indice: (cert_id, domain_id, lang) -> {hash -> (quiz_num, num_q, arq)}
indice = defaultdict(dict)
for data in quizzes:
    cert   = data.get("cert_id", "?")
    domain = data.get("domain_id", "?")
    lang   = data.get("lang", "?")
    qnum   = data.get("quiz_num", "?")
    arq    = data["_arq"]
    chave_grupo = (cert, domain, lang)
    for q in data.get("questions", []):
        num   = q.get("num", "?")
        texto = q.get("text", "")
        h     = htext(texto)
        if h in indice[chave_grupo]:
            orig_qnum, orig_num, orig_arq = indice[chave_grupo][h]
            erros_inter += 1
            achou = True
            L(f"  [INTER-DUP] {cert}/{domain} [{lang}]")
            L(f"              quiz_{orig_qnum:03d} Q{orig_num}  X  quiz_{qnum:03d} Q{num}")
            L(f"              '{texto[:120]}'"); L()
        else:
            indice[chave_grupo][h] = (qnum, num, arq)
if not achou:
    L("  Nenhuma questao identica entre quizzes do mesmo dominio/idioma."); L()

# ── 4. GABARITO INVALIDO ──────────────────────────────────────────────────────
H("4. GABARITO INVALIDO (correct fora do intervalo valido)")
achou = False
for data in quizzes:
    arq  = data["_arq"]
    for q in data.get("questions", []):
        num     = q.get("num", "?")
        correct = q.get("correct")
        opts    = q.get("options", [])
        if not isinstance(correct, int) or correct < 0 or correct >= len(opts):
            erros_gab += 1
            achou = True
            L(f"  [GAB-INV] {arq} — Q{num}: correct={correct}, {len(opts)} alternativas"); L()
if not achou:
    L("  Todos os gabaritos estao validos."); L()

# ── 5. QUESTOES SEM JUSTIFICATIVA ─────────────────────────────────────────────
H("5. QUESTOES SEM JUSTIFICATIVA")
achou = False
for data in quizzes:
    arq = data["_arq"]
    for q in data.get("questions", []):
        num = q.get("num", "?")
        jc  = q.get("justification_correct", "").strip()
        jw  = q.get("justification_wrong", "").strip()
        if not jc or not jw:
            erros_just += 1
            achou = True
            L(f"  [SEM-JUST] {arq} — Q{num}")
            if not jc: L(f"             justification_correct ausente")
            if not jw: L(f"             justification_wrong ausente")
            L()
if not achou:
    L("  Todas as questoes possuem justificativas."); L()

# ── RESUMO ────────────────────────────────────────────────────────────────────
H("RESUMO FINAL")
L(f"  Quizzes analisados  : {total_quizzes}")
L(f"  Questoes analisadas : {total_questoes}"); L()
L(f"  [1] Alternativas duplicadas      : {erros_alt}")
L(f"  [2] Questoes identicas intra-quiz: {erros_intra}")
L(f"  [3] Questoes identicas inter-quiz: {erros_inter}")
L(f"  [4] Gabaritos invalidos          : {erros_gab}")
L(f"  [5] Sem justificativa            : {erros_just}"); L()

total = erros_alt + erros_intra + erros_inter + erros_gab + erros_just
if total == 0:
    L("  STATUS: TUDO OK — nenhum problema encontrado!")
else:
    L(f"  STATUS: {total} problema(s) real(is) encontrado(s).")
L()
S(); L(f"  Relatorio: {REPORT}"); S()

Path(REPORT).write_text("\n".join(linhas), encoding="utf-8")
print("\n".join(linhas))
