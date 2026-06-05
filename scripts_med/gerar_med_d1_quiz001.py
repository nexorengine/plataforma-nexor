import anthropic
import json
import os
from datetime import datetime

# ── CONFIG ──────────────────────────────────────────────────────────────────
DOMINIO = "cirurgia_geral"
SUBDOMINIO = "abdome_agudo"
PRODUTO = "med"
QUIZ_NUM = "001"
OUTPUT_PATH = r"C:\ARAGORN\aragorn_quiz\static\quizzes\med\cirurgia_geral\quiz_001_pt.json"
LOG_PATH = r"C:\ARAGORN\aragorn_quiz\scripts_med\log_d1_quiz001.txt"
MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 4000

BLOCOS = {
    "F1": {"descricao": "Definição e terminologia clínica", "n": 13},
    "F2": {"descricao": "Diagnóstico diferencial e distinções", "n": 12},
    "F3": {"descricao": "Cenários clínicos e condutas", "n": 13},
    "F4": {"descricao": "Integração e julgamento clínico", "n": 12},
}

TOPICOS = [
    "Apendicite aguda",
    "Colecistite aguda",
    "Obstrução intestinal",
    "Perfuração de víscera oca",
    "Diverticulite aguda",
    "Peritonite",
    "Abdome agudo inflamatório vs obstrutivo vs perfurativo vs vascular"
]

SYSTEM_PROMPT = """Você é um gerador de questões de múltipla escolha para residência médica no Brasil.
Referência: Sabiston — Tratado de Cirurgia (2019).

REGRAS:
1. Cada questão tem enunciado clínico + 4 alternativas (A, B, C, D)
2. Apenas 1 alternativa correta
3. Comentário da resposta correta: máx 2 linhas / 30 palavras
4. Nível de dificuldade compatível com prova ACM/SC
5. Responda SOMENTE com JSON válido, sem markdown, sem backticks
6. Nunca repita temas entre questões do mesmo bloco"""

def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    linha = f"[{timestamp}] {msg}"
    print(linha)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(linha + "\n")

def gerar_bloco(client, camada, descricao, n_questoes, topicos, q_start):
    prompt = f"""Gere exatamente {n_questoes} questões de múltipla escolha nível {camada} ({descricao}) sobre Abdome Agudo em Cirurgia Geral.

Tópicos a cobrir (distribua): {', '.join(topicos)}

Retorne SOMENTE este JSON:
{{
  "questoes": [
    {{
      "id": "Q{str(q_start).zfill(3)}",
      "camada": "{camada}",
      "subtopico": "nome do subtópico",
      "enunciado": "texto da questão",
      "alternativas": {{
        "A": "texto",
        "B": "texto",
        "C": "texto",
        "D": "texto"
      }},
      "resposta": "A",
      "comentario": "explicação em até 2 linhas"
    }}
  ]
}}

IDs sequenciais começando em Q{str(q_start).zfill(3)}
Enunciado: cenário clínico realista, objetivo
Comentário: máx 30 palavras"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
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

def main():
    log("=" * 60)
    log(f"NEXOR MED — Quiz {QUIZ_NUM} — D1 Abdome Agudo — PT")
    log("=" * 60)

    client = anthropic.Anthropic()
    todas_questoes = []
    q_start = 1

    for camada, info in BLOCOS.items():
        log(f"Gerando bloco {camada} ({info['n']} questões)...")
        try:
            questoes = gerar_bloco(client, camada, info["descricao"],
                                   info["n"], TOPICOS, q_start)
            todas_questoes.extend(questoes)
            q_start += info["n"]
            log(f"  {camada}: {len(questoes)} questões OK")
        except Exception as e:
            log(f"  ERRO no bloco {camada}: {e}")
            raise

    # auditoria
    log(f"\nAUDITORIA:")
    log(f"  Total de questões: {len(todas_questoes)}")
    alertas = 0
    for q in todas_questoes:
        if len(q.get("alternativas", {})) != 4:
            log(f"  ALERTA alternativas: {q['id']}")
            alertas += 1
        if q.get("resposta") not in ["A", "B", "C", "D"]:
            log(f"  ALERTA resposta inválida: {q['id']}")
            alertas += 1
    if alertas == 0:
        log("  Todas as questões dentro do padrão.")

    # salvar
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "dominio": DOMINIO,
            "subdominio": SUBDOMINIO,
            "produto": PRODUTO,
            "quiz": QUIZ_NUM,
            "idioma": "pt",
            "total": len(todas_questoes),
            "questoes": todas_questoes
        }, f, ensure_ascii=False, indent=2)

    log(f"\nSalvo em: {OUTPUT_PATH}")
    log("CONCLUÍDO.")

if __name__ == "__main__":
    main()
