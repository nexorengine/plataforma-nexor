import json
from pathlib import Path

def rebalancear(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    qs = data["questions"]
    
    # contar estado atual
    by_diff = {"EASY": [], "STANDARD": [], "HARD": []}
    for q in qs:
        by_diff[q["difficulty"]].append(q)
    
    target = {"EASY": 10, "STANDARD": 30, "HARD": 10}
    
    for diff, target_n in target.items():
        atual = len(by_diff[diff])
        if atual == target_n:
            continue
        elif atual > target_n:
            # excesso: mover para STANDARD
            excesso = atual - target_n
            for q in by_diff[diff][target_n:]:
                q["difficulty"] = "STANDARD"
        else:
            # falta: pegar de STANDARD
            falta = target_n - atual
            std = [q for q in qs if q["difficulty"] == "STANDARD"]
            if diff == "EASY":
                candidatos = std[:falta]
            else:  # HARD
                candidatos = std[-falta:]
            for q in candidatos:
                q["difficulty"] = diff
    
    # verificar resultado
    dist = {"EASY": 0, "STANDARD": 0, "HARD": 0}
    for q in qs:
        dist[q["difficulty"]] += 1
    
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return dist

quizzes = [
    Path(r"quizzes\med\pediatria\puericultura\quiz_001_pt.json"),
    Path(r"quizzes\med\pediatria\puericultura\quiz_002_pt.json"),
    Path(r"quizzes\med\pediatria\neonatologia\quiz_001_pt.json"),
    Path(r"quizzes\med\pediatria\neonatologia\quiz_002_pt.json"),
    Path(r"quizzes\med\pediatria\pneumologia_ped\quiz_001_pt.json"),
    Path(r"quizzes\med\pediatria\pneumologia_ped\quiz_002_pt.json"),
]

for p in quizzes:
    dist = rebalancear(p)
    status = "OK" if dist == {"EASY":10,"STANDARD":30,"HARD":10} else "ERRO"
    print(f"[{status}] {p.parent.name}/{p.name} — E={dist['EASY']} S={dist['STANDARD']} H={dist['HARD']}")

print("CONCLUIDO")
