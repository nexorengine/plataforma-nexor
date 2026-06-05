import anthropic
import json
import os
from datetime import datetime

DOMINIO      = "cirurgia_geral"
SUBDOMINIO   = "queimaduras"
PRODUTO      = "med"
DOMAIN_NAME  = "D9 · Queimaduras"
OUTPUT_PATH  = r"C:\ARAGORN\aragorn_quiz\static\flashcards\med\cirurgia_geral\flashcards_d9_pt.json"
LOG_PATH     = r"C:\ARAGORN\aragorn_quiz\scripts_med\log_d9_flashcards.txt"
MODEL        = "claude-haiku-4-5-20251001"
MAX_TOKENS   = 4000

CAMADAS = {
    "F1": "Definição — O que é? Conceitos precisos, terminologia clínica.",
    "F2": "Distinção — Qual a diferença? Comparações, diagnóstico diferencial.",
    "F3": "Aplicação — Como usar na prática? Cenários clínicos, condutas, red flags.",
    "F4": "Síntese — Como integrar? Julgamento clínico, múltiplos conceitos."
}

TOPICOS = [
    "Classificação de queimaduras — 1°, 2° superficial, 2° profundo, 3° grau",
    "Regra dos 9 e fórmula de Lund-Browder — cálculo da SCQ",
    "Reposição volêmica — fórmula de Parkland e Galveston",
    "Critérios de internação e transferência para centro de queimados",
    "Lesão inalatória — diagnóstico e manejo das vias aéreas",
    "Queimadura elétrica e química — particularidades",
    "Tratamento cirúrgico — escarotomia, enxertia e curativos",
    "Complicações — infecção, síndrome compartimental, CIVD"
]

SYSTEM_PROMPT = """Você é um gerador de flashcards médicos para preparação de residência médica no Brasil.
Referência principal: Sabiston — Tratado de Cirurgia (2019).

REGRAS ABSOLUTAS:
1. FRENTE: máximo 15 palavras — pergunta direta e específica
2. VERSO: máximo 2 linhas / 25 palavras — resposta técnica objetiva
3. Zero exemplos no verso
4. Zero contexto adicional
5. Zero conectivos desnecessários
6. Terminologia médica precisa
7. Responda SOMENTE com JSON válido, sem markdown, sem backticks"""

def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    linha = f"[{timestamp}] {msg}"
    print(linha)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(linha + "\n")

def gerar_camada(client, camada_codigo, camada_descricao, topicos):
    prompt = f"""Gere exatamente 12 flashcards de nível {camada_codigo} ({camada_descricao}) sobre Queimaduras em Cirurgia Geral para prova de residência médica.

Tópicos a cobrir (distribua entre os 12 cards): {', '.join(topicos)}

Retorne SOMENTE este JSON:
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

    tokens = MAX_TOKENS
    for tentativa in range(1, 4):
        try:
            response = client.messages.create(
                model=MODEL, max_tokens=tokens, system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = response.content[0].text.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"): raw = raw[4:]
            data = json.loads(raw.strip())
            return data["flashcards"]
        except json.JSONDecodeError as e:
            log(f"  Tentativa {tentativa} falhou: {e}")
            if tentativa == 3: raise
            tokens = int(tokens * 1.4)
            log(f"  Retentando com {tokens} tokens...")

def main():
    log("=" * 60)
    log(f"NEXOR MED — Flashcards {DOMAIN_NAME} — PT")
    log("=" * 60)

    client = anthropic.Anthropic()
    todos_cards = []

    for codigo, descricao in CAMADAS.items():
        log(f"Gerando camada {codigo}...")
        cards = gerar_camada(client, codigo, descricao, TOPICOS)
        todos_cards.extend(cards)
        log(f"  {codigo}: {len(cards)} cards OK")

    log(f"\nAUDITORIA:")
    log(f"  Total: {len(todos_cards)} cards")
    alertas = 0
    for card in todos_cards:
        if len(card["frente"].split()) > 15:
            log(f"  ALERTA frente longa: {card['id']}"); alertas += 1
        if len(card["verso"].split()) > 25:
            log(f"  ALERTA verso longo: {card['id']}"); alertas += 1
    if alertas == 0:
        log("  Todos os cards dentro do padrão calibrado.")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump({"dominio": DOMINIO, "subdominio": SUBDOMINIO,
                   "produto": PRODUTO, "domain_name": DOMAIN_NAME,
                   "idioma": "pt", "total": len(todos_cards),
                   "flashcards": todos_cards}, f, ensure_ascii=False, indent=2)

    log(f"\nSalvo em: {OUTPUT_PATH}")
    log("CONCLUÍDO.")

if __name__ == "__main__":
    main()
