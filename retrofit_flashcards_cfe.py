# retrofit_flashcards_cfe.py
# Regenera flashcards CFE no padrao FractalFlashcard v1
# Linguas: PT + EN apenas (ES ignorado)
# Encoding: UTF-8 sem BOM
# Uso: python retrofit_flashcards_cfe.py

import os
import json
import time
import anthropic

BASE_DIR = r"C:\ARAGORN\aragorn_quiz\flashcards\cfe"
CLIENT = anthropic.Anthropic()  # usa ANTHROPIC_API_KEY do ambiente

LAYERS = {
    "F1": {"pt": "Definição",  "en": "Definition"},
    "F2": {"pt": "Distinção",  "en": "Distinction"},
    "F3": {"pt": "Aplicação",  "en": "Application"},
    "F4": {"pt": "Síntese",    "en": "Synthesis"},
}

PROMPT_PT = """Você é um especialista em certificação CFE (Certified Fraud Examiner) da ACFE.

Gere exatamente 48 flashcards no padrão FractalFlashcard para o domínio: {domain_name}

REGRAS OBRIGATÓRIAS:
- 12 cards por layer: F1 (Definição), F2 (Distinção), F3 (Aplicação), F4 (Síntese)
- Frente: pergunta direta ou termo, MÁXIMO 15 palavras
- Verso: resposta mínima suficiente, MÁXIMO 25 palavras
- ZERO exemplos ("por exemplo", "exemplo:", "ex.:" são proibidos)
- ZERO narrativa, ZERO contexto extra, ZERO redundância
- Linguagem técnica precisa, nível CFE exam
- F1: definições core do domínio
- F2: diferenças entre conceitos similares ("qual a diferença entre X e Y?")
- F3: aplicação prática ("em qual situação...", "como se classifica...")
- F4: regras críticas, exceções, red flags que o examinador testa

Responda APENAS com JSON válido, sem markdown, sem texto antes ou depois:

{{
  "cards": [
    {{
      "id": 1,
      "layer": "F1",
      "topic": "slug_do_topico",
      "front": "pergunta aqui",
      "back": "resposta aqui"
    }}
  ]
}}"""

PROMPT_EN = """You are a CFE (Certified Fraud Examiner) certification expert from ACFE.

Generate exactly 48 flashcards in FractalFlashcard format for domain: {domain_name}

MANDATORY RULES:
- 12 cards per layer: F1 (Definition), F2 (Distinction), F3 (Application), F4 (Synthesis)
- Front: direct question or term, MAXIMUM 15 words
- Back: minimum sufficient answer, MAXIMUM 25 words
- ZERO examples ("for example", "e.g.", "such as" are forbidden)
- ZERO narrative, ZERO extra context, ZERO redundancy
- Precise technical language, CFE exam level
- F1: core definitions of the domain
- F2: differences between similar concepts ("what is the difference between X and Y?")
- F3: practical application ("in which situation...", "how is X classified...")
- F4: critical rules, exceptions, red flags the examiner tests

Respond ONLY with valid JSON, no markdown, no text before or after:

{{
  "cards": [
    {{
      "id": 1,
      "layer": "F1",
      "topic": "topic_slug",
      "front": "question here",
      "back": "answer here"
    }}
  ]
}}"""


def load_existing(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def call_claude(prompt):
    response = CLIENT.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.content[0].text.strip()
    # remove markdown fences se presentes
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0].strip()
    return json.loads(raw)


def build_json(existing, lang, new_cards):
    lang_key = lang  # "pt" ou "en"
    layer_labels = {k: v[lang_key] for k, v in LAYERS.items()}

    cards_out = []
    for c in new_cards:
        cards_out.append({
            "id": c["id"],
            "layer": c["layer"],
            "topic": c["topic"],
            "front": {lang_key: c["front"]},
            "back":  {lang_key: c["back"]}
        })

    return {
        "cert_id":     existing.get("cert_id", "cfe"),
        "domain_id":   existing.get("domain_id", ""),
        "domain_code": existing.get("domain_code", ""),
        "domain_name": existing.get("domain_name", ""),
        "lang":        lang_key,
        "total":       len(cards_out),
        "schema":      "FractalFlashcard-v1",
        "layers":      layer_labels,
        "cards":       cards_out
    }


def save_json(path, data):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def retrofit_domain(domain_path, domain_name):
    pt_path = os.path.join(domain_path, "flashcards_pt.json")
    en_path = os.path.join(domain_path, "flashcards_en.json")

    for lang, path, prompt_tpl in [
        ("pt", pt_path, PROMPT_PT),
        ("en", en_path, PROMPT_EN),
    ]:
        if not os.path.exists(path):
            print(f"  [{lang.upper()}] arquivo nao encontrado, pulando.")
            continue

        existing = load_existing(path)

        # backup antes de sobrescrever
        bak_path = path + ".bak_retrofit"
        if not os.path.exists(bak_path):
            save_json(bak_path, existing)
            print(f"  [{lang.upper()}] backup salvo.")

        print(f"  [{lang.upper()}] chamando API...")
        prompt = prompt_tpl.format(domain_name=domain_name)

        try:
            result = call_claude(prompt)
            cards = result["cards"]

            if len(cards) != 48:
                print(f"  [{lang.upper()}] AVISO: {len(cards)} cards gerados (esperado 48). Salvando assim mesmo.")

            new_data = build_json(existing, lang, cards)
            save_json(path, new_data)
            print(f"  [{lang.upper()}] {len(cards)} cards salvos. OK")

        except Exception as e:
            print(f"  [{lang.upper()}] ERRO: {e}")

        time.sleep(2)  # rate limit


def main():
    domains = sorted([
        d for d in os.listdir(BASE_DIR)
        if os.path.isdir(os.path.join(BASE_DIR, d))
    ])

    print(f"RETROFIT FLASHCARDS CFE — {len(domains)} dominios")
    print(f"Linguas: PT + EN | ES: ignorado")
    print("=" * 50)

    for i, domain in enumerate(domains, 1):
        domain_path = os.path.join(BASE_DIR, domain)
        domain_name = domain.replace("_", " ").title()
        print(f"\n[{i:02d}/{len(domains)}] {domain}")

        retrofit_domain(domain_path, domain_name)

    print("\n" + "=" * 50)
    print("RETROFIT CONCLUIDO.")


if __name__ == "__main__":
    main()
