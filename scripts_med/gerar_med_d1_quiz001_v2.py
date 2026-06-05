import anthropic
import json
import os
from datetime import datetime

# ── CONFIG ──────────────────────────────────────────────────────────────────
PRODUTO       = "med"
CERT_ID       = "med"
DOMAIN_ID     = "cirurgia_geral"
SUBDOMINIO    = "abdome_agudo"
DOMAIN_NAME   = "D1 · Abdome Agudo"
CERT_NAME     = "Residência Médica — Cirurgia Geral"
QUIZ_NUM      = 1
LANG          = "pt"
OUTPUT_PATH   = r"C:\ARAGORN\aragorn_quiz\static\quizzes\med\cirurgia_geral\quiz_001_pt.json"
LOG_PATH      = r"C:\ARAGORN\aragorn_quiz\scripts_med\log_d1_quiz001.txt"
MODEL         = "claude-haiku-4-5-20251001"

# Distribuição: 20% EASY (10q) + 60% STANDARD (30q) + 20% HARD (10q) = 50
# Dividido em blocos por camada FractalQuiz + dificuldade

BLOCOS = [
    {"camada": "F1", "descricao": "Definição e terminologia clínica",       "difficulty": "EASY",     "n": 10, "tokens": 4000},
    {"camada": "F2", "descricao": "Diagnóstico diferencial e distinções",   "difficulty": "STANDARD", "n": 10, "tokens": 4000},
    {"camada": "F3", "descricao": "Cenários clínicos e condutas",           "difficulty": "STANDARD", "n": 10, "tokens": 4000},
    {"camada": "F3", "descricao": "Cenários clínicos e condutas avançadas", "difficulty": "STANDARD", "n": 10, "tokens": 4000},
    {"camada": "F4", "descricao": "Integração e julgamento clínico",        "difficulty": "HARD",     "n": 5,  "tokens": 3000},
    {"camada": "F4", "descricao": "Integração e julgamento clínico",        "difficulty": "HARD",     "n": 5,  "tokens": 3000},
]

TOPICOS = [
    "Apendicite aguda",
    "Colecistite aguda",
    "Obstrução intestinal",
    "Perfuração de víscera oca",
    "Diverticulite aguda",
    "Peritonite",
    "Abdome agudo inflamatório vs obstrutivo vs perfurativo vs vascular"
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
- Todos os distrátores devem ser plausíveis para quem não domina completamente o tópico
- Sem absolutos (sempre, nunca, todos), sem clang association, sem "todas as anteriores"

NÍVEL COGNITIVO:
- EASY: Bloom Nível 1-2 (definição/compreensão direta)
- STANDARD: Bloom Nível 3 (aplicação em cenário clínico)
- HARD: Bloom Nível 4-5 (análise/avaliação com múltiplas variáveis)

JUSTIFICATIVAS:
- justification_correct: explica o PRINCÍPIO clínico/fisiopatológico (máx 30 palavras)
- justification_wrong: explica especificamente por que cada distrator está errado (máx 20 palavras cada)
"""

SYSTEM_PROMPT = f"""Você é um gerador expert de questões de múltipla escolha para provas de residência médica no Brasil.
Referência principal: Sabiston — Tratado de Cirurgia (2019).
Nível da prova: ACM/SC — prova unificada generalista.

{METODO_NEXOR}

Responda SOMENTE com JSON válido, sem markdown, sem backticks."""

def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    linha = f"[{timestamp}] {msg}"
    print(linha)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(linha + "\n")

def gerar_bloco(client, bloco, topicos, q_start, max_tokens):
    camada     = bloco["camada"]
    descricao  = bloco["descricao"]
    difficulty = bloco["difficulty"]
    n          = bloco["n"]

    prompt = f"""Gere exatamente {n} questões de múltipla escolha nível {difficulty} ({camada} — {descricao}) sobre Abdome Agudo em Cirurgia Geral.

Tópicos a cobrir (distribua entre as {n} questões): {', '.join(topicos)}

Retorne SOMENTE este JSON:
{{
  "questoes": [
    {{
      "num": {q_start},
      "text": "enunciado com cenário clínico",
      "tag": "snake_case_subtopico",
      "camada": "{camada}",
      "options": ["A. texto", "B. texto", "C. texto", "D. texto"],
      "correct": 1,
      "difficulty": "{difficulty}",
      "justification_correct": "princípio clínico em até 30 palavras",
      "justification_wrong": "A: motivo; B: motivo; C: motivo (omitir a correta)"
    }}
  ]
}}

REGRAS:
- correct: número 1-4 (posição da alternativa correta)
- options: sempre ["A. ...", "B. ...", "C. ...", "D. ..."]
- Comprimento das opções homogêneo (±20%)
- Correta NÃO pode ser a mais longa
- Sem absolutos, sem clang, sem "todas as anteriores"
- IDs sequenciais começando em num={q_start}"""

    MAX_TENTATIVAS = 3
    tokens = max_tokens
    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=tokens,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = response.content[0].text.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()
            data = json.loads(raw)
            return data["questoes"]
        except json.JSONDecodeError as e:
            log(f"  Tentativa {tentativa} falhou (truncado): {e}")
            if tentativa == MAX_TENTATIVAS:
                raise
            tokens = int(tokens * 1.4)
            log(f"  Retentando com {tokens} tokens...")

def main():
    log("=" * 60)
    log(f"NEXOR MED — Quiz {QUIZ_NUM:03d} — {DOMAIN_NAME} — PT")
    log(f"Padrão: 20% EASY + 60% STANDARD + 20% HARD")
    log("=" * 60)

    client = anthropic.Anthropic()
    todas_questoes = []
    q_start = 1

    for i, bloco in enumerate(BLOCOS):
        label = f"{bloco['camada']}/{bloco['difficulty']} ({bloco['n']}q)"
        log(f"Gerando bloco {i+1}/{len(BLOCOS)}: {label}...")
        try:
            questoes = gerar_bloco(client, bloco, TOPICOS, q_start, bloco["tokens"])
            todas_questoes.extend(questoes)
            q_start += bloco["n"]
            log(f"  OK: {len(questoes)} questões geradas")
        except Exception as e:
            log(f"  ERRO: {e}")
            raise

    # ── AUDITORIA ──────────────────────────────────────────────────────────
    log(f"\nAUDITORIA:")
    log(f"  Total: {len(todas_questoes)} questões")

    easy     = sum(1 for q in todas_questoes if q.get("difficulty") == "EASY")
    standard = sum(1 for q in todas_questoes if q.get("difficulty") == "STANDARD")
    hard     = sum(1 for q in todas_questoes if q.get("difficulty") == "HARD")
    log(f"  EASY: {easy} | STANDARD: {standard} | HARD: {hard}")

    alertas = 0
    for q in todas_questoes:
        if len(q.get("options", [])) != 4:
            log(f"  ALERTA opções: Q{q.get('num')}")
            alertas += 1
        if q.get("correct") not in [1, 2, 3, 4]:
            log(f"  ALERTA correct inválido: Q{q.get('num')}")
            alertas += 1
        if not q.get("justification_correct"):
            log(f"  ALERTA sem justification_correct: Q{q.get('num')}")
            alertas += 1
    if alertas == 0:
        log("  Todas as questões dentro do padrão NEXOR.")

    # ── SALVAR ─────────────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "cert_id":     CERT_ID,
            "domain_id":   DOMAIN_ID,
            "subdominio":  SUBDOMINIO,
            "quiz_num":    QUIZ_NUM,
            "domain_name": DOMAIN_NAME,
            "cert_name":   CERT_NAME,
            "lang":        LANG,
            "total":       len(todas_questoes),
            "questions":   todas_questoes
        }, f, ensure_ascii=False, indent=2)

    log(f"\nSalvo em: {OUTPUT_PATH}")
    log("CONCLUÍDO.")

if __name__ == "__main__":
    main()
