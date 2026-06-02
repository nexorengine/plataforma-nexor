"""
NEXOR -- COMPLETAR CFE law_cfe quiz_003 004 005 v1
Completa os 3 arquivos EN que ficaram incompletos.
Gera questoes com escopo exclusivamente americano.
Sincroniza PT e ES automaticamente.

USO:
    python completar_law_cfe.py
"""

import json
import os
import anthropic
from pathlib import Path
from datetime import datetime
import shutil

OUTPUT_DIR = r"static\quizzes\cfe\law_cfe"
MODEL      = "claude-sonnet-4-5"
MAX_TOKENS = 8192
TIMESTAMP  = datetime.now().strftime("%Y%m%d_%H%M")

# Estado atual de cada arquivo
ARQUIVOS = {
    "quiz_003": 31,
    "quiz_004": 31,
    "quiz_005": 32,
}

# Pool de topicos exclusivamente americanos para law_cfe
TOPICOS = [
    "FCPA anti-bribery provisions elements jurisdiction covered persons",
    "FCPA accounting provisions books records and internal controls",
    "FCPA third party liability agent due diligence requirements",
    "FCPA affirmative defenses local law and promotional expenses",
    "FCPA facilitating payments exception definition and limits",
    "SOX Section 302 CEO CFO certification criminal liability",
    "SOX Section 404 ICFR management assessment and auditor attestation",
    "SOX Section 806 whistleblower employee anti-retaliation protections",
    "SOX Section 906 criminal penalties for false certifications",
    "SOX Section 201 prohibited non-audit services to audit clients",
    "SOX Section 203 mandatory audit partner rotation five years",
    "SOX Section 206 cooling off period former auditors",
    "RICO statute elements civil and criminal application",
    "RICO predicate acts pattern of racketeering activity definition",
    "Bank Secrecy Act currency transaction reports CTR thresholds",
    "BSA suspicious activity reports SAR filing obligations",
    "AML Know Your Customer KYC Customer Due Diligence CDD requirements",
    "AML Enhanced Due Diligence EDD for high risk customers",
    "Dodd-Frank SEC whistleblower bounty program award calculation",
    "Dodd-Frank anti-retaliation whistleblower employer prohibitions",
    "18 USC 1343 wire fraud elements interstate commerce requirement",
    "18 USC 1341 mail fraud elements use of mails",
    "18 USC 1956 money laundering concealment proceeds of crime",
    "18 USC 1957 engaging monetary transactions criminally derived property",
    "Computer Fraud and Abuse Act CFAA unauthorized access elements",
    "CFAA exceeding authorized access definition and application",
    "Honest Services Fraud 18 USC 1346 bribery and kickbacks",
    "False Claims Act qui tam relator provisions and bounty awards",
    "False Claims Act reverse false claims liability definition",
    "False Claims Act scienter requirement knowledge standard",
    "Federal Sentencing Guidelines fraud offense level calculation",
    "Federal Sentencing Guidelines organizational culpability factors",
    "SEC enforcement disgorgement penalties and clawback provisions",
    "DOJ deferred prosecution agreement conditions and requirements",
    "DOJ non-prosecution agreement distinction from DPA",
    "Corporate criminal liability respondeat superior doctrine",
    "Individual liability willful blindness conscious avoidance doctrine",
    "PCAOB authority over auditors of public companies",
    "Securities fraud 18 USC 1348 elements and penalties",
    "Identity theft 18 USC 1028 elements and aggravated identity theft",
    "Bank fraud 18 USC 1344 elements and application",
    "Healthcare fraud 18 USC 1347 elements and False Claims Act overlap",
    "Travel Act interstate commerce bribery and corruption",
    "Conspiracy 18 USC 371 to commit fraud against United States",
    "Statute of limitations federal fraud offenses tolling",
    "Forfeiture criminal and civil asset forfeiture in fraud cases",
    "Extraterritorial jurisdiction US law applied to foreign conduct",
    "Privilege attorney client privilege in fraud investigations",
    "Fifth Amendment privilege against self-incrimination in fraud",
    "Grand jury proceedings subpoenas in fraud investigations",
]

LANG_CONFIG = {
    "pt": "Portugues (Brasil)",
    "es": "Espanol (neutro latinoamericano)",
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

def get_topicos(n_needed, existing_tags, quiz_num):
    # Seleciona topicos distintos baseado no numero do quiz
    offset = (quiz_num - 3) * 10  # quiz_003=0, quiz_004=10, quiz_005=20
    pool = TOPICOS[offset:] + TOPICOS[:offset]  # rotaciona o pool
    # Filtra ja usados
    available = [t for t in pool if not any(
        t.split()[0].lower() in tag.lower() for tag in existing_tags
    )]
    if len(available) < n_needed:
        available = pool
    return available[:n_needed]

def generate_questions(client, quiz_num, topicos, num_start):
    topicos_str = "\n".join(f"  - {t}" for t in topicos)

    prompt = f"""You are an expert CFE (Certified Fraud Examiner) exam question writer.

Generate exactly {len(topicos)} exam questions for the CFE certification.
Domain: Law (US Federal Law applicable to fraud)
Language: English
Level: Advanced professional CFE exam level

STRICT SCOPE — US FEDERAL LAW AND ACFE STANDARDS ONLY:
- ALL questions must be grounded in US federal law or ACFE Fraud Examiners Manual
- Legal references MUST be: FCPA, SOX, RICO, BSA, AML, CFAA, Dodd-Frank,
  wire fraud (18 USC 1343), mail fraud (18 USC 1341),
  money laundering (18 USC 1956), False Claims Act, PCAOB, SEC, DOJ
- NO Brazilian law, NO LGPD, NO Portuguese law, NO generic country law
- Scenarios must use US business contexts (US companies, US regulators)
- Cite specific USC sections or SOX sections where applicable

TOPICS (one question per topic in this exact order):
{topicos_str}

Start numbering from num={num_start}.

QUALITY REQUIREMENTS:
- Scenario-based with realistic US business contexts
- 4 plausible professional-level options
- Only one unambiguously correct answer per ACFE standards
- Detailed justification citing specific US law provisions
- Wrong answer justification explains why each distractor is incorrect

Return ONLY a valid JSON array, no markdown, no explanation:
[{{
  "num": {num_start},
  "text": "Full scenario question text",
  "tag": "us_law_topic_snake_case",
  "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "correct": 0,
  "justification_correct": "Detailed explanation citing specific US law",
  "justification_wrong": "Why other options are incorrect"
}}]"""

    try:
        qs = call_api(client, prompt)
        for i, q in enumerate(qs):
            q["num"] = num_start + i
        return qs
    except Exception as e:
        print(f"\n    Erro bloco: {e}. Tentando individual...")
        results = []
        for i, topico in enumerate(topicos):
            print(f"    Q{num_start+i}... ", end="", flush=True)
            try:
                p2 = f"""Generate 1 CFE exam question about: {topico}
US federal law only. num={num_start+i}.
Return ONLY a JSON array with one object, no markdown."""
                qs2 = call_api(client, p2)
                if isinstance(qs2, list) and qs2:
                    qs2[0]["num"] = num_start + i
                    results.append(qs2[0])
                    print("OK")
                else:
                    print("SKIP")
            except Exception as e2:
                print(f"FALHOU: {e2}")
        return results

def translate_questions(client, questions, lang_name):
    if not questions:
        return []
    translated = []
    block_size = 5
    for i in range(0, len(questions), block_size):
        bloco = questions[i:i+block_size]
        block_json = json.dumps(bloco, ensure_ascii=False, indent=2)
        prompt = f"""Translate these CFE exam questions from English to {lang_name}.

RULES:
1. Translate ONLY: "text", "options", "justification_correct", "justification_wrong"
2. DO NOT modify: "num", "tag", "correct"
3. Keep prefixes: "A. ", "B. ", "C. ", "D. "
4. Keep US law names in English: FCPA, SOX, RICO, BSA, AML, CFAA, DOJ, SEC, PCAOB
5. Return ONLY the JSON array, no markdown

Input:
{block_json}"""
        try:
            result = call_api(client, prompt)
            translated.extend(result)
            print(".", end="", flush=True)
        except Exception as e:
            print(f"\n    Erro traducao: {e} — mantendo EN")
            translated.extend(bloco)
    return translated

def process_quiz(client, quiz_base, current_en_count):
    n_needed  = 50 - current_en_count
    quiz_num  = int(quiz_base.split("_")[1])  # ex: quiz_003 → 3

    en_path = Path(OUTPUT_DIR) / f"{quiz_base}_en.json"
    if not en_path.exists():
        print(f"  EN nao encontrado: {en_path}")
        return

    # Carrega EN
    backup(str(en_path))
    en_data = load_json(str(en_path))
    en_questions = en_data["questions"]
    existing_tags = set(q.get("tag", "") for q in en_questions)
    num_start = max(q["num"] for q in en_questions) + 1

    print(f"  EN: {current_en_count}q → gerando {n_needed}q (Q{num_start}–Q{num_start+n_needed-1})")

    # Gera em blocos de 10
    new_questions = []
    topicos = get_topicos(n_needed, existing_tags, quiz_num)
    block_size = 10

    for i in range(0, len(topicos), block_size):
        bloco = topicos[i:i+block_size]
        ns = num_start + i
        print(f"  Bloco Q{ns}–Q{ns+len(bloco)-1}... ", end="", flush=True)
        qs = generate_questions(client, quiz_num, bloco, ns)
        for j, q in enumerate(qs):
            q["num"] = ns + j
        new_questions.extend(qs)
        print(f"OK ({len(qs)}q)")

    # Salva EN
    all_en = en_questions + new_questions
    for i, q in enumerate(all_en):
        q["num"] = i + 1
    en_data["questions"] = all_en
    save_json(str(en_path), en_data)
    print(f"  EN salvo: {len(all_en)}q")

    # Sincroniza PT e ES
    for lang_code, lang_name in LANG_CONFIG.items():
        lang_path = Path(OUTPUT_DIR) / f"{quiz_base}_{lang_code}.json"
        if not lang_path.exists():
            print(f"  {lang_code.upper()}: nao encontrado")
            continue

        backup(str(lang_path))
        lang_data = load_json(str(lang_path))
        lang_questions = lang_data["questions"]
        lang_count = len(lang_questions)

        # Identifica questoes faltantes
        translated_nums = set(q["num"] for q in lang_questions)
        missing_en = [q for q in all_en if q["num"] not in translated_nums]

        if not missing_en:
            print(f"  {lang_code.upper()}: ja sincronizado")
            continue

        print(f"  {lang_code.upper()}: traduzindo {len(missing_en)}q ", end="", flush=True)
        translated = translate_questions(client, missing_en, lang_name)
        print()

        all_lang = lang_questions + translated
        for i, q in enumerate(all_lang):
            q["num"] = i + 1
        lang_data["questions"] = all_lang
        save_json(str(lang_path), lang_data)
        print(f"  {lang_code.upper()} salvo: {len(all_lang)}q")

def main():
    print("=" * 70)
    print("  NEXOR -- COMPLETAR CFE law_cfe quiz_003 004 005")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)

    client = anthropic.Anthropic()

    total_needed = sum(50 - v for v in ARQUIVOS.values())
    print(f"\n  Arquivos : {len(ARQUIVOS)}")
    print(f"  A gerar  : {total_needed} questoes EN + traducoes PT/ES")

    for quiz_base, current_count in ARQUIVOS.items():
        n_needed = 50 - current_count
        print(f"\n{'─'*70}")
        print(f"  {quiz_base} ({current_count}/50 — faltam {n_needed})")
        print(f"{'─'*70}")
        process_quiz(client, quiz_base, current_count)

    print("\n" + "=" * 70)
    print("  CONCLUIDO")
    print("  Rode: python verificar_duplicatas.py")
    print("=" * 70)

if __name__ == "__main__":
    main()
