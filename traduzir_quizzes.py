import os, json, anthropic
from pathlib import Path

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
client = anthropic.Anthropic(api_key=API_KEY)
QUIZ_DIR = Path("static/quizzes")

def traduzir_questao(q):
    prompt = f"""Traduza o seguinte objeto JSON para português brasileiro.
Traduza APENAS os valores dos campos: text, tag, options, justification_correct, justification_wrong.
NÃO traduza as chaves (num, text, tag, options, correct, justification_correct, justification_wrong).
NÃO altere o valor do campo "correct" (é um número, não traduza).
Mantenha terminologia técnica precisa (CFE, ISO 27001, ACFE, etc).
Retorne APENAS o JSON traduzido, sem markdown, sem texto extra.

JSON original:
{json.dumps(q, ensure_ascii=False)}"""

    msg = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = msg.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def traduzir_quiz(path):
    print(f"  Traduzindo: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    
    # Check if already in Portuguese
    sample = data["questions"][0]["text"] if data["questions"] else ""
    if any(w in sample.lower() for w in ["durante", "qual", "segundo", "quando", "como", "entre", "que"]):
        print(f"  -> Já em português, pulando.")
        return

    translated_questions = []
    total = len(data["questions"])
    for i, q in enumerate(data["questions"]):
        print(f"  -> Questão {i+1}/{total}...", end="\r")
        try:
            tq = traduzir_questao(q)
            translated_questions.append(tq)
        except Exception as e:
            print(f"\n  -> Erro na questão {i+1}: {e}. Mantendo original.")
            translated_questions.append(q)

    data["questions"] = translated_questions
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n  -> Concluído: {total} questões traduzidas.")

def main():
    quizzes = list(QUIZ_DIR.rglob("quiz_*.json"))
    if not quizzes:
        print("Nenhum quiz encontrado em static/quizzes/")
        return
    
    print(f"NEXOR QUIZ — Tradução Automática")
    print(f"Encontrados {len(quizzes)} quiz(zes) para traduzir.\n")
    
    for path in sorted(quizzes):
        traduzir_quiz(path)
    
    print("\nTradução concluída!")

if __name__ == "__main__":
    main()
