#!/usr/bin/env python3
import json
from pathlib import Path

QUIZ_DIR = Path("static/quizzes")

print("=" * 70)
print("  NEXOR — INVENTÁRIO COMPLETO DO ACERVO")
print("=" * 70)

stats = {}
sem_en = []
sem_es = []

for path_pt in sorted(QUIZ_DIR.rglob("quiz_*_pt.json")):
    data = json.loads(path_pt.read_text(encoding="utf-8"))
    cert = data.get("cert_id","?")
    domain = data.get("domain_id","?")
    n = len(data.get("questions",[]))
    qnum = data.get("quiz_num","?")

    key = f"{cert}/{domain}"
    if key not in stats:
        stats[key] = {"quizzes":0,"questoes":0,"completos":0}
    stats[key]["quizzes"] += 1
    stats[key]["questoes"] += n
    if n >= 50: stats[key]["completos"] += 1

    path_en = Path(str(path_pt).replace("_pt.json","_en.json"))
    path_es = Path(str(path_pt).replace("_pt.json","_es.json"))
    label = f"{cert}/{domain}/quiz_{qnum:03d}"
    if not path_en.exists(): sem_en.append((label, n))
    if not path_es.exists(): sem_es.append((label, n))

print(f"\n{'─'*70}")
print(f"  ACERVO POR CERTIFICAÇÃO E DOMÍNIO")
print(f"{'─'*70}")
total_q = 0
for key, s in sorted(stats.items()):
    status = "✅" if s["completos"] == s["quizzes"] else "⚠️ "
    print(f"  {status} {key}")
    print(f"     Quizzes: {s['quizzes']} | Questões PT: {s['questoes']} | Completos: {s['completos']}/{s['quizzes']}")
    total_q += s["questoes"]

print(f"\n{'─'*70}")
print(f"  TOTAL GERAL: {total_q} questões em {sum(s['quizzes'] for s in stats.values())} quizzes PT")
print(f"{'─'*70}")

if sem_en:
    print(f"\n⚠️  FALTAM TRADUÇÃO EN ({len(sem_en)} quizzes):")
    for label, n in sem_en:
        print(f"     {label} ({n}q)")

if sem_es:
    print(f"\n⚠️  FALTAM TRADUÇÃO ES ({len(sem_es)} quizzes):")
    for label, n in sem_es:
        print(f"     {label} ({n}q)")

if not sem_en and not sem_es:
    print(f"\n✅  Todas as traduções EN e ES estão em dia!")

print(f"\n{'='*70}")
