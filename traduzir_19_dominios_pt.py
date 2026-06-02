"""
NEXOR -- TRADUTOR 19 DOMINIOS CFE -- EN PARA PT v1
Traduz quiz_001_en.json para quiz_001_pt.json
nos 19 dominios CFE recem gerados.
Blocos de 10 questoes por chamada -- sem truncamento.

USO:
    python traduzir_19_dominios_pt.py
"""

import json
import anthropic
from pathlib import Path
from datetime import datetime

QUIZZES_DIR = r"static\quizzes\cfe"
MODEL       = "claude-sonnet-4-5"
MAX_TOKENS  = 8192
TIMESTAMP   = datetime.now().strftime("%Y%m%d_%H%M")

DOMINIOS = [
    "ethics_fraud_examiners",
    "evidence_principles",
    "expert_witness",
    "financial_institution_fraud",
    "fraud_risk_management",
    "fraudulent_disbursements",
    "identity_theft_cyberfraud",
    "individual_rights",
    "international_fraud",
    "inventory_fraud",
    "investigation_planning",
    "legal_issues_investigations",
    "non_criminal_actions",
    "occupational_fraud",
    "procurement_contract_fraud",
    "report_writing",
    "securities_fraud",
    "sources_information",
    "tracing_assets"
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

def translate_block(client, questions, lang_name):
    prompt = f"""Translate these CFE exam questions from English to {lang_name}.

STRICT RULES:
1. Translate ONLY: text, options, justification_correct, justification_wrong
2. DO NOT modify: num, tag, correct, difficulty
3. Keep prefixes exactly: "A. ", "B. ", "C. ", "D. "
4. Keep ALL legal terms in English:
   FCPA, SOX, RICO, BSA, SAR, CTR, NACHA, SEC, ACFE,
   CFE, GAAP, IFRS, COSO, SAS, ISA, MLAT, FBAR, FATCA,
   FinCEN, FATF, DPA, NPA, EEA, DTSA, BEC, AML, KYC
5. Return ONLY valid JSON array, no markdown, no explanation

Input:
{json.dumps(questions, ensure_ascii=False, indent=2)}"""

    result = call_api(client, prompt)
    for i, q in enumerate(result):
        if i < len(questions):
            q["num"]        = questions[i]["num"]
            q["tag"]        = questions[i]["tag"]
            q["correct"]    = questions[i]["correct"]
            q["difficulty"] = questions[i]["difficulty"]
    return result

def translate_domain(client, domain_id):
    en_path = Path(QUIZZES_DIR) / domain_id / "quiz_001_en.json"
    pt_path = Path(QUIZZES_DIR) / domain_id / "quiz_001_pt.json"

    if not en_path.exists():
        print(f"  FALTA EN: {domain_id}")
        return False

    data_en = load_json(str(en_path))
    questions = data_en["questions"]
    total = len(questions)

    print(f"\n  {domain_id} ({total}q)")
    print(f"  {'─'*50}")

    translated = []
    blocks = list(range(0, total, 10))

    for i, start in enumerate(blocks):
        bloco = questions[start:start+10]
        end = min(start+10, total)
        print(f"  Bloco {i+1}/{len(blocks)} · Q{start+1}-Q{end}... ", end="", flush=True)
        try:
            result = translate_block(client, bloco, "Portugues (Brasil)")
            translated.extend(result)
            print(f"OK ({len(result)}q)")
        except Exception as e:
            print(f"ERRO: {e}")
            translated.extend(bloco)  # fallback: usa EN

    for i, q in enumerate(translated):
        q["num"] = i + 1

    quiz_pt = dict(data_en)
    quiz_pt["lang"] = "pt"
    quiz_pt["questions"] = translated
    save_json(str(pt_path), quiz_pt)
    print(f"  PT: {len(translated)}q salvo ✅")
    return True

def main():
    print("=" * 70)
    print("  NEXOR -- TRADUTOR 19 DOMINIOS CFE -- EN PARA PT v1")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"  Blocos de 10q · Sem truncamento")
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
    print(f"  CONCLUIDO: {ok}/{len(DOMINIOS)} dominios traduzidos")
    if falhou:
        print(f"  FALHARAM: {', '.join(falhou)}")
    print("  Rode: python verificar_duplicatas.py")
    print("=" * 70)

if __name__ == "__main__":
    main()
