#!/usr/bin/env python3
from pathlib import Path
import json

QUIZ_DIR = Path("static/quizzes")

quizzes_pt = sorted(QUIZ_DIR.rglob("quiz_*_pt.json"))

print("=" * 65)
print("  STATUS DE TRADUCOES")
print("=" * 65)

sem_en = []
sem_es = []

for path_pt in quizzes_pt:
    data = json.loads(path_pt.read_text(encoding="utf-8"))
    cert = data.get("cert_id","?")
    domain = data.get("domain_id","?")
    qnum = data.get("quiz_num","?")
    label = f"{cert}/{domain}/quiz_{qnum:03d}"
    
    path_en = Path(str(path_pt).replace("_pt.json","_en.json"))
    path_es = Path(str(path_pt).replace("_pt.json","_es.json"))
    
    if not path_en.exists():
        sem_en.append(label)
    if not path_es.exists():
        sem_es.append(label)

print(f"\nFaltam EN ({len(sem_en)}):")
for l in sem_en:
    print(f"  - {l}")

print(f"\nFaltam ES ({len(sem_es)}):")
for l in sem_es:
    print(f"  - {l}")

print(f"\nTotal PT: {len(quizzes_pt)}")
print(f"Completos (PT+EN+ES): {len(quizzes_pt)-len(sem_en)}")
