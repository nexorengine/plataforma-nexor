"""
NEXOR -- CORRETOR QUESTOES BRASILEIRAS CFE v1
Substitui 22 questoes com conteudo brasileiro (Lei 12.846, LGPD)
por questoes corretas com escopo americano/internacional.
Atualiza PT e ES automaticamente.

USO:
    python corrigir_brasil_cfe.py
"""

import json
import os
import anthropic
from pathlib import Path
from datetime import datetime
import shutil

QUIZZES_DIR = r"static\quizzes\cfe"
MODEL       = "claude-sonnet-4-5"
MAX_TOKENS  = 8192
TIMESTAMP   = datetime.now().strftime("%Y%m%d_%H%M")

# Mapa exato de questoes a substituir
OUT_OF_SCOPE_MAP = {
    "law_cfe/quiz_001_en.json": [2,5,7,10,12,15,17,20,22,24,27,29,30,32,35,37,42,45,48],
    "financial_transactions/quiz_004_en.json": [20,22],
    "law/quiz_001_en.json": [22],
}

ESCOPO_CFE_LAW = """CFE (ACFE) — Law Domain.
SCOPE: US federal law applicable to fraud examination ONLY.
Legal references: FCPA, SOX, RICO, BSA, AML, CFAA, Dodd-Frank,
wire fraud (18 USC 1343), money laundering (18 USC 1956),
False Claims Act, PCAOB, SEC, DOJ, Federal Sentencing Guidelines,
OECD Anti-Bribery Convention (as international framework),
UK Bribery Act (as comparison only).

STRICTLY PROHIBITED:
- Brazilian law (Lei 12.846/2013, Lei de Improbidade, Codigo Penal Brasileiro)
- LGPD (Lei Geral de Protecao de Dados)
- Any Brazil-specific regulatory body (CGU, TCU, MPF)
- Questions that test knowledge of Brazilian law as primary topic"""

ESCOPO_CFE_FINANCIAL = """CFE (ACFE) — Financial Transactions and Fraud Schemes.
SCOPE: Fraud schemes in financial transactions — US and international context.
Topics: asset misappropriation, corruption schemes, money laundering,
financial statement fraud, occupational fraud detection.

STRICTLY PROHIBITED:
- Brazilian law as primary topic
- LGPD as primary topic
- Brazil-specific regulations"""

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

def generate_replacement(client, domain_id, old_question, num):
    escopo = ESCOPO_CFE_LAW if "law" in domain_id else ESCOPO_CFE_FINANCIAL
    old_tag = old_question.get("tag", "unknown")

    # Tópicos substitutos por tag original
    topic_map = {
        "brazil lei 12.846": "FCPA third party liability and agent due diligence",
        "lgpd": "Dodd-Frank whistleblower protections and SEC bounty awards",
        "collusion": "RICO predicate acts and pattern of racketeering",
        "transnational": "OECD Anti-Bribery Convention and cross-border enforcement",
        "sox compliance vs. lgpd": "SOX Section 302 CEO CFO certification requirements",
        "wire fraud & cross-border": "18 USC 1343 wire fraud elements and jurisdiction",
        "fcpa_payment": "FCPA facilitating payments exception definition and limits",
    }

    # Seleciona topico substituto
    replacement_topic = "FCPA anti-bribery provisions elements and application"
    for key, topic in topic_map.items():
        if key.lower() in old_tag.lower():
            replacement_topic = topic
            break

    prompt = f"""You are an expert CFE (Certified Fraud Examiner) exam question writer.

{escopo}

The following question was flagged as OUT_OF_SCOPE (contains Brazilian law content) and must be replaced:
Original tag: {old_tag}
Original text: {old_question.get('text','')[:150]}

Generate exactly 1 replacement question about: {replacement_topic}

MÉTODO NEXOR DE FORMULAÇÃO:
- Scenario-based stem with clear lead-in
- 4 homogeneous options (similar length)
- Correct answer NOT the longest option
- All distractors plausible for someone unfamiliar with the topic
- No absolutes (always, never, all, none)
- justification_correct: explains the legal PRINCIPLE citing specific US law
- justification_wrong: explains why each distractor is incorrect

Return ONLY a valid JSON array with one object, no markdown:
[{{
  "num": {num},
  "text": "Full scenario question text",
  "tag": "us_law_topic_snake_case",
  "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "correct": 0,
  "justification_correct": "Detailed explanation citing specific US law provision",
  "justification_wrong": "Why each incorrect option is wrong"
}}]"""

    try:
        result = call_api(client, prompt)
        if isinstance(result, list) and result:
            result[0]["num"] = num
            return result[0]
        return None
    except Exception as e:
        print(f"\n    Erro API: {e}")
        return None

def translate_question(client, question, lang_name):
    prompt = f"""Translate this CFE exam question from English to {lang_name}.

RULES:
1. Translate ONLY: "text", "options", "justification_correct", "justification_wrong"
2. DO NOT modify: "num", "tag", "correct"
3. Keep prefixes: "A. ", "B. ", "C. ", "D. "
4. Keep US law names in English: FCPA, SOX, RICO, BSA, AML, CFAA, SEC, DOJ
5. Return ONLY a JSON array with one object, no markdown

Input:
{json.dumps([question], ensure_ascii=False, indent=2)}"""

    try:
        result = call_api(client, prompt)
        if isinstance(result, list) and result:
            result[0]["num"] = question["num"]
            result[0]["tag"] = question["tag"]
            result[0]["correct"] = question["correct"]
            return result[0]
        return question
    except Exception as e:
        print(f"\n    Erro traducao: {e}")
        return question

def process_file(client, file_key, out_nums):
    parts      = file_key.split("/")
    domain_id  = parts[0]
    quiz_fname = parts[1]

    en_path = Path(QUIZZES_DIR) / domain_id / quiz_fname
    if not en_path.exists():
        print(f"  ARQUIVO NAO ENCONTRADO: {en_path}")
        return

    backup(str(en_path))
    en_data   = load_json(str(en_path))
    questions = en_data["questions"]
    q_map     = {q["num"]: q for q in questions}
    new_questions = []

    for num in sorted(out_nums):
        old_q = q_map.get(num)
        if not old_q:
            print(f"    Q{num}: nao encontrada")
            continue

        print(f"  Q{num} [{old_q.get('tag','')[:35]}] → substituindo... ", end="", flush=True)
        new_q = generate_replacement(client, domain_id, old_q, num)

        if new_q:
            q_map[num] = new_q
            new_questions.append(new_q)
            print(f"OK [{new_q.get('tag','')[:35]}]")
        else:
            print("FALHOU — mantendo original")

    # Reconstroi e renumera
    all_questions = [q_map[n] for n in sorted(q_map.keys())]
    for i, q in enumerate(all_questions):
        q["num"] = i + 1

    en_data["questions"] = all_questions
    save_json(str(en_path), en_data)
    print(f"  EN salvo: {len(all_questions)}q")

    if not new_questions:
        return

    # Atualiza PT e ES
    for lang_code, lang_name in LANG_CONFIG.items():
        lang_fname = quiz_fname.replace("_en.json", f"_{lang_code}.json")
        lang_path  = Path(QUIZZES_DIR) / domain_id / lang_fname

        if not lang_path.exists():
            print(f"  {lang_code.upper()}: nao encontrado")
            continue

        backup(str(lang_path))
        lang_data      = load_json(str(lang_path))
        lang_map       = {q["num"]: q for q in lang_data["questions"]}

        for new_q in new_questions:
            num = new_q["num"]
            print(f"  Traduzindo Q{num} → {lang_code.upper()}... ", end="", flush=True)
            translated   = translate_question(client, new_q, lang_name)
            lang_map[num] = translated
            print("OK")

        all_lang = [lang_map[n] for n in sorted(lang_map.keys())]
        for i, q in enumerate(all_lang):
            q["num"] = i + 1

        lang_data["questions"] = all_lang
        save_json(str(lang_path), lang_data)
        print(f"  {lang_code.upper()} salvo: {len(all_lang)}q")

def main():
    print("=" * 70)
    print("  NEXOR -- CORRETOR QUESTOES BRASILEIRAS CFE v1")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)

    client = anthropic.Anthropic()

    total = sum(len(v) for v in OUT_OF_SCOPE_MAP.values())
    print(f"\n  Arquivos : {len(OUT_OF_SCOPE_MAP)}")
    print(f"  Questoes : {total} a substituir")

    for file_key, nums in OUT_OF_SCOPE_MAP.items():
        print(f"\n{'─'*70}")
        print(f"  {file_key} — {len(nums)} questoes")
        print(f"{'─'*70}")
        process_file(client, file_key, nums)

    print("\n" + "=" * 70)
    print("  CONCLUIDO")
    print("  Rode: python verificar_duplicatas.py")
    print("=" * 70)

if __name__ == "__main__":
    main()
