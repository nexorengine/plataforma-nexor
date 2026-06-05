import json
import os
import random

# Arquivos a corrigir
ARQUIVOS = [
    r"C:\ARAGORN\aragorn_quiz\static\quizzes\med\cirurgia_geral\quiz_001_pt.json",
    r"C:\ARAGORN\aragorn_quiz\static\quizzes\med\cirurgia_geral\quiz_002_pt.json",
    r"C:\ARAGORN\aragorn_quiz\static\quizzes\med\cirurgia_geral\quiz_d2_001_pt.json",
    r"C:\ARAGORN\aragorn_quiz\static\quizzes\med\cirurgia_geral\quiz_d2_002_pt.json",
]

def shuffle_questao(q):
    options = q.get("options", [])
    correct_idx = q.get("correct", 1) - 1  # 0-based

    if not options or correct_idx < 0 or correct_idx >= len(options):
        return q

    # Extrai texto correto
    correct_text = options[correct_idx]

    # Embaralha
    shuffled = options[:]
    random.shuffle(shuffled)

    # Recalcula posição da correta
    new_correct_idx = shuffled.index(correct_text)

    # Remapeia letras A/B/C/D
    letras = ["A", "B", "C", "D"]
    new_options = []
    for i, opt in enumerate(shuffled):
        # Remove prefixo antigo (ex: "A. texto") e coloca novo
        texto = opt
        if len(opt) > 2 and opt[1] == ".":
            texto = opt[2:].strip()
        new_options.append(f"{letras[i]}. {texto}")

    q["options"] = new_options
    q["correct"] = new_correct_idx + 1  # 1-based
    return q

def processar_arquivo(path):
    print(f"\nProcessando: {path}")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    questoes = data.get("questions", [])
    distribuicao_antes = {}
    distribuicao_depois = {}

    for q in questoes:
        letra_antes = ["A","B","C","D"][q.get("correct",1)-1]
        distribuicao_antes[letra_antes] = distribuicao_antes.get(letra_antes, 0) + 1

    # Aplica shuffle
    random.seed(42)  # seed para reprodutibilidade
    data["questions"] = [shuffle_questao(q) for q in questoes]

    for q in data["questions"]:
        letra_depois = ["A","B","C","D"][q.get("correct",1)-1]
        distribuicao_depois[letra_depois] = distribuicao_depois.get(letra_depois, 0) + 1

    print(f"  Distribuição ANTES: {dict(sorted(distribuicao_antes.items()))}")
    print(f"  Distribuição DEPOIS: {dict(sorted(distribuicao_depois.items()))}")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  Salvo OK.")

def main():
    print("=" * 60)
    print("NEXOR MED — Patch: Shuffle de Respostas")
    print("=" * 60)

    for path in ARQUIVOS:
        if os.path.exists(path):
            processar_arquivo(path)
        else:
            print(f"\nARQUIVO NÃO ENCONTRADO: {path}")

    print("\nCONCLUÍDO.")

if __name__ == "__main__":
    main()
