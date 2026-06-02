"""
NEXOR -- TRADUTOR FLASHCARDS CFE -- EN PARA ES v1
Traduz flashcards_en.json para flashcards_es.json
para todos os 46 dominios CFE.
Pula dominios que ja tem ES.
Blocos de 10 cards por chamada.

USO:
    python traduzir_flashcards_todos_es.py
"""

import json
import anthropic
from pathlib import Path
from datetime import datetime

FLASHCARD_DIR = r"static\flashcards\cfe"
MODEL         = "claude-sonnet-4-5"
MAX_TOKENS    = 8192

DOMINIOS = [
    "accounting_concepts","auditor_responsibilities","bankruptcy_fraud",
    "cash_receipts_fraud","collecting_evidence","consumer_fraud",
    "corporate_governance","corruption_bribery","covert_operations",
    "criminal_behavior","criminal_prosecutions","data_analysis_tools",
    "data_theft_ip","emerging_fraud","ethics_fraud_examiners",
    "evidence_principles","expert_witness","financial_institution_fraud",
    "financial_statement_fraud","fraud_investigation","fraud_prevention_programs",
    "fraud_risk_assessment","fraud_risk_management","fraudulent_disbursements",
    "government_fraud","healthcare_fraud","identity_theft_cyberfraud",
    "individual_rights","insurance_fraud","international_fraud",
    "interview_techniques","inventory_fraud","investigation_planning",
    "law_cfe","legal_issues_investigations","legal_system_overview",
    "non_criminal_actions","occupational_fraud","payment_fraud",
    "prevention_deterrence","procurement_contract_fraud","report_writing",
    "securities_fraud","sources_information","tax_fraud","tracing_assets"
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

def translate_block(client, cards):
    prompt = f"""Translate these CFE flashcards from English to Espanol neutro latinoamericano.

STRICT RULES:
1. Translate ONLY the text inside "front" and "back" fields
2. DO NOT modify: id, topic
3. Keep ALL legal terms in English:
   FCPA, UK Bribery Act, OECD, CFE, ACFE, SOX, SEC,
   BSA, SAR, CTR, FinCEN, FATF, MLAT, FBAR, FATCA,
   GAAP, IFRS, COSO, RICO, SAS, ISA, DPA, NPA, NACHA
4. Return ONLY valid JSON array, no markdown

Input:
{json.dumps(cards, ensure_ascii=False, indent=2)}

Return format:
[{{
  "id": 1,
  "topic": "same_as_input",
  "front": {{"es": "Translated front text"}},
  "back": {{"es": "Translated back text"}}
}}]"""

    result = call_api(client, prompt)
    for i, card in enumerate(result):
        if i < len(cards):
            card["id"]    = cards[i]["id"]
            card["topic"] = cards[i]["topic"]
    return result

def translate_domain(client, domain_id):
    en_path = Path(FLASHCARD_DIR) / domain_id / "flashcards_en.json"
    es_path = Path(FLASHCARD_DIR) / domain_id / "flashcards_es.json"

    if not en_path.exists():
        print(f"  FALTA EN: {domain_id}")
        return False

    if es_path.exists():
        data = load_json(str(es_path))
        if len(data.get("cards", [])) >= 45:
            print(f"  SKIP {domain_id} (ja tem ES)")
            return True

    data_en = load_json(str(en_path))
    cards_en = data_en["cards"]
    print(f"\n  {domain_id} ({len(cards_en)} cards)")

    translated = []
    blocks = [cards_en[i:i+10] for i in range(0, len(cards_en), 10)]

    for i, block in enumerate(blocks):
        start = i*10+1; end = min(start+9, len(cards_en))
        print(f"  Bloco {i+1}/{len(blocks)} · Card {start}-{end}... ", end="", flush=True)
        try:
            result = translate_block(client, block)
            translated.extend(result)
            print(f"OK ({len(result)})")
        except Exception as e:
            print(f"ERRO: {e} — usando EN")
            translated.extend(block)

    for i, card in enumerate(translated):
        card["id"] = i + 1

    save_json(str(es_path), {
        "cert_id":     data_en["cert_id"],
        "domain_id":   domain_id,
        "domain_code": data_en["domain_code"],
        "domain_name": data_en["domain_name"],
        "lang":        "es",
        "total":       len(translated),
        "cards":       translated
    })
    print(f"  ES: {len(translated)} cards salvos ✅")
    return True

def main():
    print("=" * 70)
    print("  NEXOR -- TRADUTOR FLASHCARDS CFE -- EN PARA ES v1")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"  {len(DOMINIOS)} dominios · Blocos de 10")
    print("=" * 70)

    client = anthropic.Anthropic()
    ok = 0
    falhou = []

    for i, domain_id in enumerate(DOMINIOS):
        print(f"\n  [{i+1}/{len(DOMINIOS)}]", end="")
        if translate_domain(client, domain_id):
            ok += 1
        else:
            falhou.append(domain_id)

    print("\n" + "=" * 70)
    print(f"  CONCLUIDO: {ok}/{len(DOMINIOS)} dominios")
    if falhou:
        print(f"  FALHARAM: {', '.join(falhou)}")
    print(f"  META DO DIA CONCLUIDA!")
    print("=" * 70)

if __name__ == "__main__":
    main()
