import json

def mostrar_questoes(path, label, n=10):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    
    questoes = data.get("questions", [])
    linhas = []
    linhas.append("=" * 70)
    linhas.append(f"{label}")
    linhas.append("=" * 70)
    
    for q in questoes[:n]:
        linhas.append(f"\nQ{q.get('num','?'):02d} [{q.get('camada','?')}] [{q.get('difficulty','?')}] — {q.get('tag','')}")
        linhas.append(f"{q.get('text','')}")
        linhas.append("")
        for opt in q.get("options", []):
            marker = " ◀ CORRETA" if q.get("options","").index(opt)+1 == q.get("correct") else ""
            try:
                idx = q["options"].index(opt) + 1
                marker = " ◀ CORRETA" if idx == q.get("correct") else ""
            except:
                marker = ""
            linhas.append(f"  {opt}{marker}")
        linhas.append("")
        linhas.append(f"✔ {q.get('justification_correct','')}")
        linhas.append(f"✘ {q.get('justification_wrong','')}")
        linhas.append("-" * 70)
    
    return "\n".join(linhas)

D1_PATH = r"C:\ARAGORN\aragorn_quiz\static\quizzes\med\cirurgia_geral\quiz_001_pt.json"
D2_PATH = r"C:\ARAGORN\aragorn_quiz\static\quizzes\med\cirurgia_geral\quiz_d2_001_pt.json"
OUT     = r"C:\ARAGORN\aragorn_quiz\scripts_med\amostra_d1_d2.txt"

output = ""
output += mostrar_questoes(D1_PATH, "D1 · ABDOME AGUDO — primeiras 10 questões")
output += "\n\n"
output += mostrar_questoes(D2_PATH, "D2 · HEPATOBILIAR E PÂNCREAS — primeiras 10 questões")

with open(OUT, "w", encoding="utf-8") as f:
    f.write(output)

print(f"Salvo em: {OUT}")
