"""
NEXOR -- RETOMADA CFE v1
Completa os 8 arquivos CFE que ficaram incompletos por falta de creditos.
Gera apenas as questoes faltantes em cada arquivo.
Atualiza PT e ES automaticamente.

USO:
    python retomar_cfe.py
"""

import json
import os
import anthropic
from pathlib import Path
from datetime import datetime
import shutil

OUTPUT_DIR = r"static\quizzes\cfe"
MODEL      = "claude-sonnet-4-5"
MAX_TOKENS = 8192
TIMESTAMP  = datetime.now().strftime("%Y%m%d_%H%M")

# Arquivos incompletos e quantidade atual de questoes
INCOMPLETOS = {
    "financial_transactions/quiz_004_en.json": 38,
    "financial_transactions/quiz_006_en.json": 48,
    "law/quiz_001_en.json":                    35,
    "law_cfe/quiz_003_en.json":                31,
    "law_cfe/quiz_004_en.json":                31,
    "law_cfe/quiz_005_en.json":                32,
    "law_cfe/quiz_006_en.json":                32,
    "prevention_deterrence/quiz_006_en.json":  43,
}

# Topicos por dominio -- exclusivamente americanos para CFE
TOPICOS = {
    "law_cfe": [
        "FCPA anti-bribery provisions elements and jurisdiction",
        "FCPA accounting provisions books records internal controls",
        "FCPA third party liability and due diligence requirements",
        "FCPA affirmative defenses local law and promotional expenses",
        "SOX Section 302 CEO CFO certification criminal liability",
        "SOX Section 404 ICFR assessment and auditor attestation",
        "SOX Section 806 whistleblower anti-retaliation protections",
        "SOX Section 1107 retaliation against whistleblowers criminal",
        "RICO statute elements civil and criminal application",
        "RICO predicate acts pattern of racketeering activity",
        "Bank Secrecy Act currency transaction reports CTR thresholds",
        "BSA suspicious activity reports SAR filing obligations",
        "AML Know Your Customer KYC Customer Due Diligence CDD",
        "Dodd-Frank SEC whistleblower bounty program awards",
        "Dodd-Frank anti-retaliation whistleblower protections",
        "18 USC 1343 wire fraud elements interstate commerce",
        "18 USC 1341 mail fraud elements use of mails",
        "18 USC 1956 money laundering concealment proceeds",
        "18 USC 1957 monetary transactions criminally derived property",
        "Computer Fraud and Abuse Act unauthorized access elements",
        "Honest Services Fraud 18 USC 1346 bribery kickbacks",
        "False Claims Act qui tam relator provisions awards",
        "False Claims Act reverse false claims liability",
        "Federal Sentencing Guidelines fraud offense calculation",
        "SEC enforcement disgorgement penalties clawback provisions",
        "DOJ deferred prosecution agreement conditions requirements",
        "Corporate criminal liability respondeat superior doctrine",
        "Individual liability willful blindness conscious avoidance",
        "PCAOB authority auditor independence public companies",
        "Securities fraud 18 USC 1348 elements penalties",
    ],
    "law": [
        "FCPA anti-bribery provisions and jurisdiction",
        "SOX whistleblower and certification requirements",
        "RICO civil and criminal application to fraud",
        "BSA AML reporting obligations financial institutions",
        "Wire fraud mail fraud federal statutes elements",
        "Money laundering federal statutes 18 USC 1956",
        "False Claims Act whistleblower qui tam provisions",
        "Federal Sentencing Guidelines fraud offenses",
        "CFAA computer fraud unauthorized access",
        "Dodd-Frank whistleblower SEC bounty program",
        "Honest Services Fraud deprivation of intangible rights",
        "Corporate criminal liability respondeat superior",
        "SEC enforcement disgorgement civil penalties",
        "DOJ non-prosecution deferred prosecution agreements",
        "PCAOB auditor oversight public company requirements",
        "Identity theft 18 USC 1028 elements penalties",
        "Bank fraud 18 USC 1344 elements",
        "Healthcare fraud 18 USC 1347 elements",
        "Travel Act interstate bribery corruption",
        "Conspiracy 18 USC 371 to commit fraud",
    ],
    "financial_transactions": [
        "Check kiting float manipulation detection red flags",
        "Skimming schemes cash larceny before recording",
        "Register disbursement schemes false voids refunds",
        "Billing schemes shell company fictitious vendor",
        "Pay and return schemes vendor overpayment",
        "Payroll fraud ghost employee detection controls",
        "Expense reimbursement fraud mischaracterized expenses",
        "Financial statement fraud revenue recognition timing",
        "Inventory fraud theft misappropriation methods",
        "Money laundering placement layering integration",
        "Ponzi scheme characteristics investor fraud",
        "Embezzlement lapping accounts receivable",
        "Accounts payable fraud duplicate payment schemes",
        "Asset misappropriation non-cash theft methods",
        "Cash on hand theft petty cash manipulation",
        "Journal entry fraud concealment manipulation",
        "Related party transactions disclosure fraud",
        "Loan fraud application misrepresentation",
        "Mortgage fraud property valuation schemes",
        "Securities fraud pump and dump manipulation",
    ],
    "prevention_deterrence": [
        "Internal controls preventive detective corrective types",
        "Segregation of duties incompatible functions identification",
        "Anti-fraud program elements ACFE fraud prevention",
        "Whistleblower hotline anonymous reporting best practices",
        "Pre-employment background screening fraud prevention",
        "Fraud risk assessment methodology ACFE standards",
        "Audit committee oversight fraud governance",
        "Code of conduct ethics program tone at top",
        "Data analytics continuous monitoring fraud detection",
        "Fraud awareness training program design effectiveness",
        "Vendor due diligence anti-corruption controls",
        "Physical security controls asset protection",
        "IT access controls user provisioning segregation",
        "Surprise audits unannounced procedures deterrence",
        "Job rotation mandatory vacation fraud prevention",
        "Document retention policy fraud investigation",
        "Fraud investigation referral law enforcement criteria",
        "Civil recovery remedies fraud victims options",
        "Insurance fidelity bonds crime coverage fraud",
        "Proactive fraud detection data mining techniques",
    ],
}

LANG_CONFIG = {
    "pt": {"lang_name": "Portugues (Brasil)"},
    "es": {"lang_name": "Espanol (neutro latinoamericano)"},
}

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def backup(path):
    bak = path + f".bak_{TIMESTAMP}"
    if not os.path.exists(bak):
        shutil.copy2(path, bak)

def call_api(client, prompt):
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def get_topicos(domain_id, n_needed, existing_tags):
    pool = TOPICOS.get(domain_id, TOPICOS["law_cfe"])
    # Filtra topicos ja usados
    available = [t for t in pool if not any(
        t.split()[0].lower() in tag.lower() for tag in existing_tags
    )]
    if len(available) < n_needed:
        available = pool  # fallback ao pool completo
    return available[:n_needed]

def generate_questions(client, domain_id, topicos, num_start):
    topicos_str = "\n".join(f"  - {t}" for t in topicos)

    prompt = f"""You are an expert CFE (Certified Fraud Examiner) exam question writer.

Generate exactly {len(topicos)} exam questions for the CFE certification.
Domain: {domain_id.replace('_', ' ').title()}
Language: English
Level: Advanced professional CFE exam level

STRICT SCOPE — US LAW AND ACFE STANDARDS ONLY:
- ALL questions must reference US federal law or ACFE Fraud Examiners Manual
- Legal references: FCPA, SOX, RICO, BSA, AML, CFAA, Dodd-Frank,
  wire fraud (18 USC 1343), mail fraud (18 USC 1341),
  money laundering (18 USC 1956), False Claims Act, PCAOB, SEC
- NO Brazilian law, NO LGPD, NO Portuguese law, NO generic country law
- Scenarios must use US business contexts

TOPICS (one question per topic in order):
{topicos_str}

Start numbering from num={num_start}.

Return ONLY a valid JSON array, no markdown:
[{{
  "num": {num_start},
  "text": "Full scenario-based question text",
  "tag": "us_topic_snake_case",
  "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "correct": 0,
  "justification_correct": "Detailed explanation citing specific US law or ACFE standard",
  "justification_wrong": "Why other options are incorrect"
}}]"""

    try:
        return call_api(client, prompt)
    except Exception as e:
        print(f"\n    Erro no bloco: {e}. Tentando individual...")
        results = []
        for i, topico in enumerate(topicos):
            print(f"    Q{num_start+i}... ", end="", flush=True)
            try:
                p2 = f"""Generate 1 CFE exam question about: {topico}
Domain: {domain_id}. US law only. num={num_start+i}.
Return ONLY a JSON array with one object, no markdown."""
                qs = call_api(client, p2)
                if isinstance(qs, list):
                    qs[0]["num"] = num_start + i
                    results.append(qs[0])
                    print("OK")
                else:
                    print("FORMATO ERRADO")
            except Exception as e2:
                print(f"FALHOU: {e2}")
        return results

def translate_block(client, questions, lang_name):
    if not questions:
        return []
    block_json = json.dumps(questions, ensure_ascii=False, indent=2)
    prompt = f"""Translate these CFE exam questions from English to {lang_name}.

RULES:
1. Translate ONLY: "text", "options", "justification_correct", "justification_wrong"
2. DO NOT modify: "num", "tag", "correct"
3. Keep prefixes: "A. ", "B. ", "C. ", "D. "
4. Keep US law names in English: FCPA, SOX, RICO, BSA, AML, CFAA, etc.
5. Return ONLY the JSON array, no markdown

Input:
{block_json}"""
    try:
        return call_api(client, prompt)
    except Exception as e:
        print(f"\n    Erro traducao: {e}")
        return questions

def process_file(client, file_key, current_count):
    parts       = file_key.split("/")
    domain_id   = parts[0]
    quiz_fname  = parts[1]
    n_needed    = 50 - current_count

    en_path = Path(OUTPUT_DIR) / domain_id / quiz_fname
    if not en_path.exists():
        print(f"  ARQUIVO NAO ENCONTRADO: {en_path}")
        return

    backup(str(en_path))
    data = load_json(str(en_path))
    questions = data["questions"]
    existing_tags = set(q.get("tag", "") for q in questions)
    num_start = max(q["num"] for q in questions) + 1

    print(f"  Atual: {current_count}q | A gerar: {n_needed}q | num_start: {num_start}")

    # Gera em blocos de 10
    new_questions = []
    topicos = get_topicos(domain_id, n_needed, existing_tags)
    block_size = 10

    for i in range(0, len(topicos), block_size):
        bloco = topicos[i:i+block_size]
        ns = num_start + i
        print(f"  Bloco Q{ns}-Q{ns+len(bloco)-1}... ", end="", flush=True)
        qs = generate_questions(client, domain_id, bloco, ns)
        for j, q in enumerate(qs):
            q["num"] = ns + j
        new_questions.extend(qs)
        print(f"OK ({len(qs)}q)")

    # Monta e renumera
    all_questions = questions + new_questions
    for i, q in enumerate(all_questions):
        q["num"] = i + 1

    data["questions"] = all_questions
    save_json(str(en_path), data)
    print(f"  EN salvo: {len(all_questions)}q")

    # Atualiza PT e ES
    for lang_code, lang_cfg in LANG_CONFIG.items():
        lang_fname = quiz_fname.replace("_en.json", f"_{lang_code}.json")
        lang_path  = Path(OUTPUT_DIR) / domain_id / lang_fname
        if not lang_path.exists():
            print(f"  {lang_code.upper()}: nao encontrado, pulando")
            continue

        backup(str(lang_path))
        lang_data = load_json(str(lang_path))
        lang_questions = lang_data["questions"]

        print(f"  Traduzindo {len(new_questions)}q para {lang_code.upper()}... ", end="", flush=True)
        translated_new = []
        for i in range(0, len(new_questions), 10):
            bloco = new_questions[i:i+10]
            t = translate_block(client, bloco, lang_cfg["lang_name"])
            translated_new.extend(t)
        print("OK")

        all_lang = lang_questions + translated_new
        for i, q in enumerate(all_lang):
            q["num"] = i + 1

        lang_data["questions"] = all_lang
        save_json(str(lang_path), lang_data)
        print(f"  {lang_code.upper()} salvo: {len(all_lang)}q")

def main():
    print("=" * 70)
    print("  NEXOR -- RETOMADA CFE v1")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)

    client = anthropic.Anthropic()

    total_needed = sum(50 - v for v in INCOMPLETOS.values())
    print(f"\n  Arquivos incompletos : {len(INCOMPLETOS)}")
    print(f"  Questoes a completar : {total_needed}")

    for file_key, current_count in INCOMPLETOS.items():
        n_needed = 50 - current_count
        print(f"\n{'─'*70}")
        print(f"  {file_key} ({current_count}/50 — faltam {n_needed})")
        print(f"{'─'*70}")
        process_file(client, file_key, current_count)

    print("\n" + "=" * 70)
    print("  CONCLUIDO")
    print("  Rode: python verificar_duplicatas.py")
    print("  Rode: python auditar_escopo_v2.py")
    print("=" * 70)

if __name__ == "__main__":
    main()
