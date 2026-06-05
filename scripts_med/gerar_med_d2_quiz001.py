import anthropic
import json
import os
from datetime import datetime

PRODUTO      = "med"
CERT_ID      = "med"
DOMAIN_ID    = "cirurgia_geral"
SUBDOMINIO   = "hepatobiliar_pancreas"
DOMAIN_NAME  = "D2 · Hepatobiliar e Pâncreas"
CERT_NAME    = "Residência Médica — Cirurgia Geral"
QUIZ_NUM     = 1
LANG         = "pt"
OUTPUT_PATH  = r"C:\ARAGORN\aragorn_quiz\static\quizzes\med\cirurgia_geral\quiz_d2_001_pt.json"
LOG_PATH     = r"C:\ARAGORN\aragorn_quiz\scripts_med\log_d2_quiz001.txt"
MODEL        = "claude-haiku-4-5-20251001"

BLOCOS = [
    {"camada": "F1", "descricao": "Definição e terminologia clínica",       "difficulty": "EASY",     "n": 10, "tokens": 4000},
    {"camada": "F2", "descricao": "Diagnóstico diferencial e distinções",   "difficulty": "STANDARD", "n": 10, "tokens": 4000},
    {"camada": "F3", "descricao": "Cenários clínicos e condutas",           "difficulty": "STANDARD", "n": 10, "tokens": 5600},
    {"camada": "F3", "descricao": "Cenários clínicos e condutas avançadas", "difficulty": "STANDARD", "n": 10, "tokens": 5600},
    {"camada": "F4", "descricao": "Integração e julgamento clínico",        "difficulty": "HARD",     "n": 5,  "tokens": 3000},
    {"camada": "F4", "descricao": "Integração e julgamento clínico",        "difficulty": "HARD",     "n": 5,  "tokens": 3000},
]

TOPICOS = [
    "Colelitíase e coledocolitíase",
    "Colecistite aguda litiásica e alitiásica",
    "Colangite aguda — critérios de Tokyo",
    "Pancreatite aguda — classificação de Atlanta e conduta",
    "Pancreatite crônica",
    "Icterícia obstrutiva — diagnóstico diferencial",
    "Câncer de pâncreas",
    "Câncer de vesícula biliar"
]

METODO_NEXOR = """
MÉTODO NEXOR DE FORMULAÇÃO — APLICAR OBRIGATORIAMENTE:

STEM:
- Apresentar cenário clínico realista antes do lead-in
- Lead-in deve ser uma pergunta completa e focada
- Sem informação irrelevante, sem negativo duplo

OPÇÕES:
- 4 opções de comprimento homogêneo (±20% variação)
- Opção correta NÃO pode ser a mais longa
- Todos os distrátores devem ser plausíveis
- Sem absolutos (sempre, nunca, todos), sem clang, sem "todas as anteriores"

NÍVEL COGNITIVO:
- EASY: Bloom 1-2 (definição/compreensão direta)
- STANDARD: Bloom 3 (aplicação em cenário clínico)
- HARD: Bloom 4-5 (análise/avaliação com múltiplas variáveis)

JUSTIFICATIVAS:
- justification_correct: princípio clínico/fisiopatológico (máx 30 palavras)
- justification_wrong: por que cada distrator está errado (máx 20 palavras cada)
"""

def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    linha = f"[{timestamp}] {msg}"
    print(linha)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(linha + "\n")

def gerar_bloco(client, bloco, topicos, q_start):
    camada     = bloco["camada"]
    descricao  = bloco["descricao"]
    difficulty = bloco["difficulty"]
    n          = bloco["n"]
    tokens     = bloco["tokens"]

    system = f"""Você é um gerador expert de questões de múltipla escolha para provas de residência médica no Brasil.
Referência principal: Sabiston — Tratado de Cirurgia (2019).
Nível da prova: ACM/SC — prova unificada generalista.
{METODO_NEXOR}
Responda SOMENTE com JSON válido, sem markdown, sem backticks."""

    prompt = f"""Gere exatamente {n} questões nível {difficulty} ({camada} — {descricao}) sobre Doenças Hepatobiliares e Pâncreas.

Tópicos: {', '.join(topicos)}

JSON:
{{
  "questoes": [
    {{
      "num": {q_start},
      "text": "enunciado clínico",
      "tag": "snake_case_subtopico",
      "camada": "{camada}",
      "options": ["A. texto", "B. texto", "C. texto", "D. texto"],
      "correct": 1,
      "difficulty": "{difficulty}",
      "justification_correct": "princípio em até 30 palavras",
      "justification_wrong": "A: motivo; B: motivo; C: motivo"
    }}
  ]
}}

IDs começando em num={q_start}. correct=1-4. Opções homogêneas. Correta não é a mais longa."""

    for tentativa in range(1, 4):
        try:
            response = client.messages.create(
                model=MODEL, max_tokens=tokens, system=system,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = response.content[0].text.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            data = json.loads(raw.strip())
            return data["questoes"]
        except json.JSONDecodeError as e:
            log(f"  Tentativa {tentativa} falhou: {e}")
            if tentativa == 3:
                raise
            tokens = int(tokens * 1.4)
            log(f"  Retentando com {tokens} tokens...")

def main():
    log("=" * 60)
    log(f"NEXOR MED — Quiz 001 — {DOMAIN_NAME} — PT")
    log(f"Padrão: 20% EASY + 60% STANDARD + 20% HARD")
    log("=" * 60)

    client = anthropic.Anthropic()
    todas = []
    q_start = 1

    for i, bloco in enumerate(BLOCOS):
        label = f"{bloco['camada']}/{bloco['difficulty']} ({bloco['n']}q)"
        log(f"Gerando bloco {i+1}/{len(BLOCOS)}: {label}...")
        questoes = gerar_bloco(client, bloco, TOPICOS, q_start)
        todas.extend(questoes)
        q_start += bloco["n"]
        log(f"  OK: {len(questoes)} questões")

    log(f"\nAUDITORIA:")
    log(f"  Total: {len(todas)}")
    easy = sum(1 for q in todas if q.get("difficulty") == "EASY")
    std  = sum(1 for q in todas if q.get("difficulty") == "STANDARD")
    hard = sum(1 for q in todas if q.get("difficulty") == "HARD")
    log(f"  EASY: {easy} | STANDARD: {std} | HARD: {hard}")
    alertas = sum(1 for q in todas if len(q.get("options",[])) != 4 or q.get("correct") not in [1,2,3,4])
    log(f"  Alertas: {alertas}" if alertas else "  Todas dentro do padrão NEXOR.")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump({"cert_id": CERT_ID, "domain_id": DOMAIN_ID,
                   "subdominio": SUBDOMINIO, "quiz_num": QUIZ_NUM,
                   "domain_name": DOMAIN_NAME, "cert_name": CERT_NAME,
                   "lang": LANG, "total": len(todas), "questions": todas},
                  f, ensure_ascii=False, indent=2)

    log(f"\nSalvo em: {OUTPUT_PATH}")
    log("CONCLUÍDO.")

if __name__ == "__main__":
    main()
