"""
NEXOR -- CORRETOR CFE law_cfe v1
Substitui questoes OUT_OF_SCOPE identificadas na auditoria v2.
Regenera apenas as questoes problematicas com escopo americano correto.
Atualiza PT e ES automaticamente.

USO:
    python corrigir_cfe_law.py
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

# Mapa de questoes OUT_OF_SCOPE por arquivo (resultado da auditoria v2)
OUT_OF_SCOPE_MAP = {
    "law_cfe/quiz_001_en.json": [2,5,7,10,12,15,17,20,22,24,27,29,30,32,35,37,42,45,48],
    "law_cfe/quiz_002_en.json": [35,39,40,43,44,47,48,49,50],
    "law_cfe/quiz_003_en.json": [3,5,7,12,15,17,20,22,25,26,29,32,33,35,38,40,43,46,47],
    "law_cfe/quiz_004_en.json": [2,4,7,10,11,14,16,17,21,23,26,29,31,34,37,40,43,46,48],
    "law_cfe/quiz_005_en.json": [2,5,7,10,12,15,16,19,20,23,26,28,29,35,39,41,45,47],
    "law_cfe/quiz_006_en.json": [2,5,6,10,12,15,20,22,24,27,29,31,33,36,37,40,43,45],
    "law/quiz_001_en.json":     [3,7,12,15,18,22,25,26,30,33,37,39,43,46,49],
    "financial_transactions/quiz_004_en.json": [29,30,32,34,36,45],
    "financial_transactions/quiz_006_en.json": [36,38],
    "prevention_deterrence/quiz_006_en.json":  [4,11,14,21,23,36,37],
}

# Topicos exclusivamente americanos para law_cfe
TOPICOS_LAW_CFE = [
    "FCPA anti-bribery provisions — elements and application",
    "FCPA accounting provisions — books records and internal controls",
    "FCPA facilitating payments exception — definition and limits",
    "FCPA affirmative defenses — local law and reasonable expenditures",
    "SOX Section 302 — CEO CFO certification requirements",
    "SOX Section 404 — internal controls over financial reporting",
    "SOX Section 906 — criminal penalties for false certifications",
    "SOX Section 806 — whistleblower protections for employees",
    "RICO statute — elements of civil and criminal RICO claims",
    "RICO predicate acts — definition and application",
    "Bank Secrecy Act — currency transaction reports CTR",
    "Bank Secrecy Act — suspicious activity reports SAR",
    "AML Know Your Customer KYC requirements",
    "Dodd-Frank whistleblower program — SEC bounty provisions",
    "Dodd-Frank whistleblower — anti-retaliation protections",
    "18 USC 1343 — wire fraud elements and penalties",
    "18 USC 1341 — mail fraud elements and application",
    "18 USC 1956 — money laundering elements",
    "18 USC 1957 — engaging in monetary transactions in criminally derived property",
    "Computer Fraud and Abuse Act CFAA — unauthorized access provisions",
    "CFAA — exceeding authorized access definition",
    "Foreign Corrupt Practices Act — jurisdiction and who is covered",
    "FCPA — third party liability and due diligence",
    "Honest Services Fraud 18 USC 1346 — definition and application",
    "Travel Act — interstate commerce and bribery",
    "Federal Sentencing Guidelines — fraud offense levels",
    "False Claims Act — qui tam provisions and whistleblower awards",
    "False Claims Act — reverse false claims liability",
    "Identity theft — 18 USC 1028 elements",
    "Securities fraud — 18 USC 1348 elements",
    "Investment Advisers Act — fraud provisions",
    "Sherman Antitrust Act — application to fraud schemes",
    "Federal Election Campaign Act — prohibited contributions",
    "PCAOB — authority over auditors of public companies",
    "SEC enforcement — disgorgement and penalties",
    "DOJ deferred prosecution agreements — conditions and implications",
    "Corporate liability — respondeat superior doctrine",
    "Individual liability — willful blindness doctrine",
    "Statute of limitations — federal fraud offenses",
    "Extraterritorial jurisdiction — US law applied abroad",
]

TOPICOS_FINANCIAL = [
    "Check kiting schemes — detection and red flags",
    "Skimming schemes — cash larceny vs skimming distinction",
    "Billing schemes — shell company characteristics",
    "Payroll fraud — ghost employee schemes",
    "Expense reimbursement fraud — red flags",
    "Financial statement fraud — revenue recognition manipulation",
    "Asset misappropriation — inventory theft methods",
    "Money laundering — placement layering integration stages",
    "Ponzi scheme characteristics and detection",
    "Embezzlement — lapping scheme mechanics",
]

TOPICOS_PREVENTION = [
    "Internal controls — preventive detective corrective classification",
    "Segregation of duties — incompatible functions",
    "Anti-fraud program — elements per ACFE guidance",
    "Whistleblower hotline — best practices and anonymous reporting",
    "Background checks — pre-employment screening",
    "Fraud risk assessment — methodology and frequency",
    "Corporate governance — board audit committee responsibilities",
    "Code of conduct — elements and tone at the top",
    "Data analytics — continuous monitoring for fraud detection",
    "Fraud awareness training — program design",
]

LANG_CONFIG = {
    "pt": {"lang_name": "Portugues (Brasil)", "domain_names": {
        "law_cfe": "Lei Aplicavel",
        "law": "Lei Aplicavel",
        "financial_transactions": "Transacoes Financeiras e Fraude",
        "prevention_deterrence": "Prevencao e Dissuasao de Fraude",
    }},
    "es": {"lang_name": "Espanol (neutro latinoamericano)", "domain_names": {
        "law_cfe": "Ley Aplicable",
        "law": "Ley Aplicable",
        "financial_transactions": "Transacciones Financieras y Fraude",
        "prevention_deterrence": "Prevencion y Disuasion del Fraude",
    }},
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

def get_topicos_for_domain(domain_id, n_needed):
    if "law" in domain_id:
        pool = TOPICOS_LAW_CFE
    elif "financial" in domain_id:
        pool = TOPICOS_FINANCIAL
    elif "prevention" in domain_id:
        pool = TOPICOS_PREVENTION
    else:
        pool = TOPICOS_LAW_CFE
    # Cicla os topicos se precisar de mais do que o pool
    topicos = []
    for i in range(n_needed):
        topicos.append(pool[i % len(pool)])
    return topicos

def generate_replacement_questions(client, domain_id, n_questions, num_start, existing_tags):
    topicos = get_topicos_for_domain(domain_id, n_questions)
    topicos_str = "\n".join(f"  - {t}" for t in topicos)
    existing_tags_str = "\n".join(f"  - {t}" for t in list(existing_tags)[:30])

    prompt = f"""You are an expert CFE (Certified Fraud Examiner) exam question writer.

Generate exactly {n_questions} replacement exam questions for the CFE certification.
Domain: {domain_id}
Language: English
Level: Advanced professional (CFE exam level)

STRICT SCOPE RULES:
- ALL questions must be based on US federal law and ACFE standards ONLY
- NO Brazilian law, NO LGPD, NO Portuguese language law
- NO generic "country X" scenarios without US law grounding
- Legal references must be: FCPA, SOX, RICO, BSA, AML, CFAA, Dodd-Frank,
  wire fraud (18 USC 1343), mail fraud (18 USC 1341), money laundering (18 USC 1956),
  False Claims Act, PCAOB, SEC regulations, Federal Sentencing Guidelines

TOPICS TO COVER (one question per topic):
{topicos_str}

TAGS ALREADY IN USE (avoid repeating these concepts):
{existing_tags_str}

Start numbering from num={num_start}.

QUALITY REQUIREMENTS:
- Scenario-based questions with realistic US business contexts
- 4 plausible options — only one clearly correct
- Detailed justification citing specific US law provisions
- Advanced CFE exam difficulty

Return ONLY a valid JSON array, no markdown:
[{{
  "num": {num_start},
  "text": "...",
  "tag": "us_law_topic_snake_case",
  "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "correct": 0,
  "justification_correct": "...",
  "justification_wrong": "..."
}}]"""

    try:
        return call_api(client, prompt)
    except Exception as e:
        print(f"\n    Erro no bloco: {e}. Tentando individual...")
        results = []
        for i, topico in enumerate(topicos):
            try:
                p2 = f"""Generate 1 CFE exam question in English about: {topico}
Domain: {domain_id}
US law only. num={num_start+i}
Return ONLY a JSON array with one object."""
                qs = call_api(client, p2)
                if isinstance(qs, list):
                    qs[0]["num"] = num_start + i
                    results.append(qs[0])
            except Exception as e2:
                print(f"      Q{num_start+i} FALHOU: {e2}")
        return results

def translate_questions(client, questions, lang_code, lang_cfg):
    translated = []
    block_size = 10
    for i in range(0, len(questions), block_size):
        bloco = questions[i:i+block_size]
        block_json = json.dumps(bloco, ensure_ascii=False, indent=2)
        prompt = f"""Translate these CFE exam questions from English to {lang_cfg['lang_name']}.

RULES:
1. Translate ONLY: "text", "options", "justification_correct", "justification_wrong"
2. DO NOT modify: "num", "tag", "correct"
3. Keep prefixes: "A. ", "B. ", "C. ", "D. "
4. Keep US law terms in English (FCPA, SOX, RICO, BSA, etc.) — do not translate law names
5. Return ONLY the JSON array, no markdown

Input:
{block_json}"""
        try:
            result = call_api(client, prompt)
            translated.extend(result)
        except Exception as e:
            print(f"\n    Erro traducao bloco: {e}")
            translated.extend(bloco)
    return translated

def process_file(client, domain_path, domain_id, quiz_filename, out_of_scope_nums):
    en_path = Path(OUTPUT_DIR) / domain_path / quiz_filename
    if not en_path.exists():
        print(f"    ARQUIVO NAO ENCONTRADO: {en_path}")
        return

    # Backup
    backup(str(en_path))

    # Carrega EN
    data = load_json(str(en_path))
    questions = data["questions"]
    existing_tags = set(q.get("tag", "") for q in questions)

    # Identifica questoes a substituir (por num)
    to_replace = set(out_of_scope_nums)
    keep = [q for q in questions if q["num"] not in to_replace]
    n_replace = len(to_replace)

    print(f"    Mantendo {len(keep)}q | Substituindo {n_replace}q")

    # Gera questoes de substituicao
    num_start = max(q["num"] for q in questions) + 100  # temporario
    new_questions = generate_replacement_questions(
        client, domain_id, n_replace, num_start, existing_tags
    )

    if len(new_questions) < n_replace:
        print(f"    AVISO: geradas {len(new_questions)} de {n_replace} esperadas")

    # Monta lista final e renumera
    all_questions = keep + new_questions
    for i, q in enumerate(all_questions):
        q["num"] = i + 1

    data["questions"] = all_questions
    save_json(str(en_path), data)
    print(f"    EN salvo: {len(all_questions)}q")

    # Atualiza PT e ES
    for lang_code, lang_cfg in LANG_CONFIG.items():
        lang_path = Path(OUTPUT_DIR) / domain_path / quiz_filename.replace("_en.json", f"_{lang_code}.json")
        if not lang_path.exists():
            print(f"    {lang_code.upper()}: arquivo nao encontrado, pulando")
            continue

        backup(str(lang_path))
        lang_data = load_json(str(lang_path))
        lang_questions = lang_data["questions"]

        # Mantém as questoes nao substituidas traduzidas
        lang_keep = [q for q in lang_questions if q["num"] not in to_replace]

        # Traduz as novas questoes
        print(f"    Traduzindo {len(new_questions)}q para {lang_code.upper()}... ", end="", flush=True)
        translated_new = translate_questions(client, new_questions, lang_code, lang_cfg)
        print("OK")

        # Monta e renumera
        all_lang = lang_keep + translated_new
        for i, q in enumerate(all_lang):
            q["num"] = i + 1

        lang_data["questions"] = all_lang
        save_json(str(lang_path), lang_data)
        print(f"    {lang_code.upper()} salvo: {len(all_lang)}q")

def main():
    print("=" * 70)
    print("  NEXOR -- CORRETOR CFE OUT_OF_SCOPE v1")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)

    client = anthropic.Anthropic()

    total_files = len(OUT_OF_SCOPE_MAP)
    total_questions = sum(len(v) for v in OUT_OF_SCOPE_MAP.values())
    print(f"\n  Arquivos a corrigir : {total_files}")
    print(f"  Questoes a substituir: {total_questions}")

    for file_key, out_nums in OUT_OF_SCOPE_MAP.items():
        parts = file_key.split("/")
        domain_id   = parts[0]
        quiz_fname  = parts[1]
        domain_path = domain_id

        print(f"\n{'─'*70}")
        print(f"  {file_key} — {len(out_nums)} questoes OUT_OF_SCOPE")
        print(f"{'─'*70}")

        # Remove duplicatas do mapa
        out_nums_clean = list(set(out_nums))
        out_nums_clean.sort()

        process_file(client, domain_path, domain_id, quiz_fname, out_nums_clean)

    print("\n" + "=" * 70)
    print("  CONCLUIDO")
    print("  Rode: python verificar_duplicatas.py")
    print("  Rode: python auditar_escopo_v2.py (confirmar correcao)")
    print("=" * 70)

if __name__ == "__main__":
    main()
