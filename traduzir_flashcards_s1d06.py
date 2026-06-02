"""
NEXOR -- TRADUTOR FLASHCARDS S1D06 -- PT e ES v1
Traduz flashcards_en.json para PT e ES.
Blocos de 10 por chamada -- sem truncamento.

USO:
    python traduzir_flashcards_s1d06.py
"""

import json
import anthropic
from pathlib import Path
from datetime import datetime

FLASHCARDS_DIR = r"static\flashcards\cfe\corruption_bribery"
MODEL          = "claude-sonnet-4-5"
MAX_TOKENS     = 8192

LANGS = [
    ("pt", "Portugues (Brasil)"),
    ("es", "Espanol neutro latinoamericano"),
]

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def call_api(client, prompt):
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def translate_block(client, cards, lang_code, lang_name):
    prompt = f"""Translate these CFE flashcards from English to {lang_name}.

STRICT RULES:
1. Translate ONLY the text inside "front" and "back" fields
2. DO NOT modify: id, topic
3. Keep ALL legal terms in English:
   FCPA, UK Bribery Act, OECD, CFE, ACFE, SOX, SEC,
   BSA, SAR, CTR, FinCEN, FATF, MLAT, DPA, NPA
4. Return ONLY valid JSON array, no markdown

Input:
{json.dumps(cards, ensure_ascii=False, indent=2)}

Return format:
[{{
  "id": 1,
  "topic": "same_as_input",
  "front": {{
    "{lang_code}": "Translated front text"
  }},
  "back": {{
    "{lang_code}": "Translated back text"
  }}
}}]"""

    result = call_api(client, prompt)
    for i, card in enumerate(result):
        if i < len(cards):
            card["id"]    = cards[i]["id"]
            card["topic"] = cards[i]["topic"]
    return result

def translate_lang(client, cards_en, lang_code, lang_name):
    print(f"\n  Traduzindo para {lang_code.upper()} ({lang_name})")
    translated = []
    blocks = [cards_en[i:i+10] for i in range(0, len(cards_en), 10)]

    for i, block in enumerate(blocks):
        start = i * 10 + 1
        end = min(start + 9, len(cards_en))
        print(f"  Bloco {i+1}/5 · Card {start}-{end}... ", end="", flush=True)
        try:
            result = translate_block(client, block, lang_code, lang_name)
            translated.extend(result)
            print(f"OK ({len(result)} cards)")
        except Exception as e:
            print(f"ERRO: {e} — usando EN como fallback")
            translated.extend(block)

    for i, card in enumerate(translated):
        card["id"] = i + 1

    return translated

def main():
    print("=" * 70)
    print("  NEXOR -- TRADUTOR FLASHCARDS S1D06 -- PT e ES v1")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"  Blocos de 10 · Sem truncamento")
    print("=" * 70)

    client = anthropic.Anthropic()

    # Carrega EN
    en_path = Path(FLASHCARDS_DIR) / "flashcards_en.json"
    data_en = load_json(str(en_path))
    cards_en = data_en["cards"]
    print(f"\n  EN carregado: {len(cards_en)} flashcards")

    # Traduz PT e ES
    for lang_code, lang_name in LANGS:
        translated = translate_lang(client, cards_en, lang_code, lang_name)

        out_path = Path(FLASHCARDS_DIR) / f"flashcards_{lang_code}.json"
        save_json(str(out_path), {
            "cert_id":     "cfe",
            "domain_id":   "corruption_bribery",
            "domain_code": "S1D06",
            "domain_name": data_en["domain_name"],
            "lang":        lang_code,
            "total":       len(translated),
            "cards":       translated
        })
        print(f"  {lang_code.upper()}: {len(translated)} flashcards salvos ✅")

    print("\n" + "=" * 70)
    print("  CONCLUIDO — Flashcards S1D06 trilíngues prontos")
    print("  EN + PT + ES · 50 cards cada")
    print("=" * 70)

if __name__ == "__main__":
    main()
