import anthropic
import json
import os
from datetime import datetime

# ── CONFIG ──────────────────────────────────────────────────────────────────
DOMINIO = "cirurgia_geral"
PRODUTO = "med"
OUTPUT_PATH = r"C:\ARAGORN\aragorn_quiz\static\flashcards\med\cirurgia_geral\flashcards_pt.json"
LOG_PATH = r"C:\ARAGORN\aragorn_quiz\scripts_med\log_d1_flashcards.txt"
MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 4000

CAMADAS = {
    "F1": "Definição — O que é? Conceitos precisos, terminologia clínica.",
    "F2": "Distinção — Qual a diferença? Comparações, diagnóstico diferencial.",
    "F3": "Aplicação — Como usar na prática? Cenários clínicos, condutas, red flags.",
    "F4": "Síntese — Como integrar? Julgamento clínico, múltiplos conceitos."
}

TOPICOS_D1 = [
    "Apendicite aguda",
    "Colecistite aguda",
    "Obstrução intestinal",
    "Perfuração de víscera hollow",
    "Diverticulite aguda"
]

SYSTEM_PROMPT = """Você é um gerador de flashcards médicos para preparação de residência médica no Brasil.
Referência principal: Sabiston — Tratado de Cirurgia (2019).

REGRAS ABSOLUTAS:
1. FRENTE: máximo 15 palavras — pergunta direta e específica
2. VERSO: máximo 2 linhas / 25 palavras — resposta técnica objetiva
3. Zero exemplos no verso
4. Zero contexto adicional
5. Zero conectivos desnecessários (portanto, ou seja, em resumo)
6. Terminologia médica precisa
7. Responda SOMENTE com JSON válido, sem markdown, sem backticks"""

def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    linha = f"[{timestamp}] {msg}"
    print(linha)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(linha + "\n")

def gerar_camada(client, camada_codigo, camada_descricao, topicos):
    prompt = f"""Gere exatamente 12 flashcards de nível {camada_codigo} ({camada_descricao}) sobre Abdome Agudo em Cirurgia Geral para prova de residência médica.

Tópicos a cobrir (distribua entre os 12 cards): {', '.join(topicos)}

Retorne SOMENTE este JSON (sem markdown):
{{
  "flashcards": [
    {{
      "id": "{camada_codigo}_001",
      "camada": "{camada_codigo}",
      "frente": "pergunta aqui",
      "verso": "resposta aqui"
    }}
  ]
}}

IDs sequenciais: {camada_codigo}_001 até {camada_codigo}_012
Frente: máx 15 palavras
Verso: máx 25 palavras, 2 linhas"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()

    # limpeza defensiva
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    data = json.loads(raw)
    return data["flashcards"]

def main():
    log("=" * 60)
    log("NEXOR MED — Gerador D1 Abdome Agudo — Flashcards PT")
    log("=" * 60)

    client = anthropic.Anthropic()
    todos_cards = []

    for codigo, descricao in CAMADAS.items():
        log(f"Gerando camada {codigo}...")
        try:
            cards = gerar_camada(client, codigo, descricao, TOPICOS_D1)
            todos_cards.extend(cards)
            log(f"  {codigo}: {len(cards)} cards gerados OK")
        except Exception as e:
            log(f"  ERRO na camada {codigo}: {e}")
            raise

    # auditoria rápida
    log(f"\nAUDITORIA:")
    log(f"  Total de cards: {len(todos_cards)}")
    alertas = 0
    for card in todos_cards:
        frente_palavras = len(card["frente"].split())
        verso_palavras = len(card["verso"].split())
        if frente_palavras > 15:
            log(f"  ALERTA frente longa: {card['id']} ({frente_palavras} palavras)")
            alertas += 1
        if verso_palavras > 25:
            log(f"  ALERTA verso longo: {card['id']} ({verso_palavras} palavras)")
            alertas += 1
    if alertas == 0:
        log("  Todos os cards dentro do padrão calibrado.")

    # salvar
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "dominio": DOMINIO,
            "produto": PRODUTO,
            "idioma": "pt",
            "total": len(todos_cards),
            "flashcards": todos_cards
        }, f, ensure_ascii=False, indent=2)

    log(f"\nSalvo em: {OUTPUT_PATH}")
    log("CONCLUÍDO.")

if __name__ == "__main__":
    main()
