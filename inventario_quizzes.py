"""
inventario_quizzes.py
Conta quizzes completos (50 questoes) em portugues por certificacao e dominio.

Uso:
    cd C:\\NEXOR\\nexor_quiz
    python inventario_quizzes.py
"""

import json
from pathlib import Path
from collections import defaultdict

QUIZ_DIR  = Path("static/quizzes")
COMPLETO  = 50

total_quizzes   = 0
total_completos = 0
total_questoes  = 0

linhas = []
def L(t=""): linhas.append(t)
def S(): L("=" * 60)

S()
L("  NEXOR — INVENTARIO DE QUIZZES COMPLETOS (PT)")
S(); L()

# Agrupa por cert
por_cert = defaultdict(lambda: defaultdict(list))

for arq in sorted(QUIZ_DIR.rglob("quiz_*_pt.json")):
    try:
        data = json.loads(arq.read_text(encoding="utf-8"))
    except:
        continue
    cert   = data.get("cert_id", "?")
    domain = data.get("domain_id", "?")
    qnum   = data.get("quiz_num", "?")
    nq     = len(data.get("questions", []))
    por_cert[cert][domain].append((qnum, nq))
    total_quizzes += 1
    total_questoes += nq
    if nq == COMPLETO:
        total_completos += 1

# Exibe por cert/domain
for cert in sorted(por_cert):
    dominios = por_cert[cert]
    cert_completos = sum(1 for d in dominios.values() for (n,q) in d if q == COMPLETO)
    cert_total     = sum(len(d) for d in dominios.values())
    L(f"  {cert.upper():<20} {cert_completos}/{cert_total} quizzes completos")
    for domain in sorted(dominios):
        quizzes = sorted(dominios[domain])
        for (qnum, nq) in quizzes:
            status = "OK" if nq == COMPLETO else f"INCOMPLETO ({nq}q)"
            L(f"    quiz_{qnum:03d}  {domain:<35} {status}")
    L()

S()
L(f"  Total de quizzes PT analisados : {total_quizzes}")
L(f"  Quizzes completos (50q)        : {total_completos}")
L(f"  Quizzes incompletos            : {total_quizzes - total_completos}")
L(f"  Total de questoes PT           : {total_questoes}")
L(f"  Equivalente trilíngue (x3)     : {total_questoes * 3}")
S()

print("\n".join(linhas))
