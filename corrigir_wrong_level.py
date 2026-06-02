"""
NEXOR -- CORRETOR WRONG_LEVEL v1
Substitui 25 questoes identificadas como WRONG_LEVEL:
- CISM: questoes muito tecnicas para nivel gerencial
- ITIL4: questoes que referenciam Managing Professional (alem do Foundation)

USO:
    python corrigir_wrong_level.py
"""

import json
import os
import anthropic
from pathlib import Path
from datetime import datetime
import shutil

QUIZZES_DIR = r"static\quizzes"
MODEL       = "claude-sonnet-4-5"
MAX_TOKENS  = 8192
TIMESTAMP   = datetime.now().strftime("%Y%m%d_%H%M")

# Mapa exato de questoes WRONG_LEVEL por arquivo
WRONG_LEVEL_MAP = {
    "cism/incident_management/quiz_001_en.json": [24, 25],
    "cism/incident_management/quiz_002_en.json": [2, 3, 4, 6, 11, 16, 41, 43, 44, 45],
    "cism/info_risk_management/quiz_001_en.json": [41],
    "cism/info_risk_management/quiz_002_en.json": [16, 19],
    "cism/info_security_governance/quiz_003_en.json": [13, 34, 37],
    "cism/info_security_governance/quiz_004_en.json": [21, 31],
    "itil4/itil_stakeholders/quiz_001_en.json": [1, 3, 5],
    "itil4/itil_svs/quiz_001_en.json": [42],
    "itil4/itil_value_streams/quiz_001_en.json": [3],
}

# Instrucoes de nivel por certificacao
NIVEL_INSTRUCOES = {
    "cism": """CISM (ISACA) — MANAGEMENT LEVEL ONLY.

CRITICAL: CISM questions must be at MANAGEMENT/GOVERNANCE level, NOT technical implementation.

CORRECT CISM FOCUS:
  ✅ Strategic decisions a CISO makes
  ✅ Risk management from business perspective
  ✅ Governance frameworks and board reporting
  ✅ Policy and program decisions
  ✅ Vendor and third-party risk management decisions
  ✅ Incident response from management perspective (declaring incidents, escalation, communication)
  ✅ Business impact and recovery priorities

WRONG LEVEL for CISM:
  ❌ Technical attack mechanics (how DoS/DDoS works technically)
  ❌ Forensic procedures (bit-stream imaging, RAM acquisition, ARP cache)
  ❌ SIEM tuning and correlation rules
  ❌ Malware technical classification
  ❌ Network traffic analysis techniques
  ❌ NTP configuration and time sync
  ❌ Application whitelisting configuration
  ❌ Specific backup media technical details

Generate a replacement question at MANAGEMENT level on a related topic.""",

    "itil4": """ITIL 4 FOUNDATION LEVEL ONLY.

CRITICAL: Questions must be at ITIL 4 Foundation level ONLY.
Do NOT reference or require knowledge of:
  ❌ ITIL 4 Managing Professional (MP) modules
  ❌ ITIL 4 Strategic Leader (SL) modules
  ❌ CDS (Create, Deliver and Support)
  ❌ DSV (Drive Stakeholder Value)
  ❌ HVIT (High Velocity IT)
  ❌ DPI (Direct, Plan and Improve)

CORRECT Foundation scope:
  ✅ ITIL 4 SVS (Service Value System) concepts
  ✅ 4 Dimensions of Service Management
  ✅ Guiding Principles (7 principles)
  ✅ Service Value Chain activities
  ✅ 34 Practices at Foundation level
  ✅ Key ITIL 4 definitions and concepts

Generate a replacement question at ITIL 4 Foundation level only.""",
}

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

def get_cert_id(file_key):
    return file_key.split("/")[0]

def get_domain_id(file_key):
    return file_key.split("/")[1]

def generate_replacement(client, cert_id, domain_id, old_question, num):
    nivel = NIVEL_INSTRUCOES.get(cert_id, "Professional certification level.")
    old_tag = old_question.get("tag", "unknown")
    old_text = old_question.get("text", "")[:200]

    # Escopo especifico por dominio CISM
    domain_context = ""
    if cert_id == "cism":
        domain_map = {
            "incident_management": "Incident Management — IR planning, escalation decisions, communication, DR triggers, business recovery priorities",
            "info_risk_management": "Information Risk Management — risk assessment decisions, risk treatment options, risk appetite, risk reporting to management",
            "info_security_governance": "Information Security Governance — CISO strategy, board reporting, policy framework, organizational security structure",
            "security_program": "Information Security Program — program governance, metrics, awareness program decisions, vendor management",
        }
        domain_context = f"\nDomain context: {domain_map.get(domain_id, domain_id)}"

    prompt = f"""You are an expert certification exam question writer.

CERTIFICATION: {cert_id.upper()}
DOMAIN: {domain_id}{domain_context}

{nivel}

The following question was flagged as WRONG_LEVEL and must be replaced:
Original tag: {old_tag}
Original text: {old_text}

Generate exactly 1 replacement question that:
- Is at the CORRECT level for {cert_id.upper()} {domain_id}
- Covers a similar management/governance topic (not the same technical content)
- Is scenario-based and realistic
- Has 4 plausible options with one unambiguous correct answer
- Includes detailed justification at the appropriate level

Return ONLY a valid JSON array with one object, no markdown:
[{{
  "num": {num},
  "text": "Full question text",
  "tag": "topic_snake_case",
  "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "correct": 0,
  "justification_correct": "Detailed management-level explanation",
  "justification_wrong": "Why other options are incorrect"
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
    prompt = f"""Translate this exam question from English to {lang_name}.

RULES:
1. Translate ONLY: "text", "options", "justification_correct", "justification_wrong"
2. DO NOT modify: "num", "tag", "correct"
3. Keep prefixes: "A. ", "B. ", "C. ", "D. "
4. Keep technical terms standard in {lang_name}
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

def process_file(client, file_key, wrong_level_nums):
    parts      = file_key.split("/")
    cert_id    = parts[0]
    domain_id  = parts[1]
    quiz_fname = parts[2]

    en_path = Path(QUIZZES_DIR) / cert_id / domain_id / quiz_fname
    if not en_path.exists():
        print(f"  ARQUIVO NAO ENCONTRADO: {en_path}")
        return

    backup(str(en_path))
    en_data   = load_json(str(en_path))
    questions = en_data["questions"]
    q_map     = {q["num"]: q for q in questions}
    new_questions = []

    for num in sorted(wrong_level_nums):
        old_q = q_map.get(num)
        if not old_q:
            print(f"    Q{num}: nao encontrada")
            continue

        print(f"  Q{num} [{old_q.get('tag','')[:30]}] → gerando... ", end="", flush=True)
        new_q = generate_replacement(client, cert_id, domain_id, old_q, num)

        if new_q:
            q_map[num] = new_q
            new_questions.append(new_q)
            print(f"OK [{new_q.get('tag','')[:30]}]")
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
        lang_path  = Path(QUIZZES_DIR) / cert_id / domain_id / lang_fname

        if not lang_path.exists():
            print(f"  {lang_code.upper()}: nao encontrado, pulando")
            continue

        backup(str(lang_path))
        lang_data      = load_json(str(lang_path))
        lang_questions = lang_data["questions"]
        lang_map       = {q["num"]: q for q in lang_questions}

        for new_q in new_questions:
            num = new_q["num"]
            print(f"  Traduzindo Q{num} para {lang_code.upper()}... ", end="", flush=True)
            translated      = translate_question(client, new_q, lang_name)
            lang_map[num]   = translated
            print("OK")

        all_lang = [lang_map[n] for n in sorted(lang_map.keys())]
        for i, q in enumerate(all_lang):
            q["num"] = i + 1

        lang_data["questions"] = all_lang
        save_json(str(lang_path), lang_data)
        print(f"  {lang_code.upper()} salvo: {len(all_lang)}q")

def main():
    print("=" * 70)
    print("  NEXOR -- CORRETOR WRONG_LEVEL v1")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)

    client = anthropic.Anthropic()

    total_files = len(WRONG_LEVEL_MAP)
    total_q     = sum(len(v) for v in WRONG_LEVEL_MAP.values())
    print(f"\n  Arquivos : {total_files}")
    print(f"  Questoes : {total_q} WRONG_LEVEL a substituir")
    print(f"  CISM     : 20 questoes (muito tecnicas)")
    print(f"  ITIL4    :  5 questoes (nivel Managing Professional)")

    for file_key, nums in WRONG_LEVEL_MAP.items():
        print(f"\n{'─'*70}")
        print(f"  {file_key}")
        print(f"  WRONG_LEVEL: {sorted(nums)}")
        print(f"{'─'*70}")
        process_file(client, file_key, nums)

    print("\n" + "=" * 70)
    print("  CONCLUIDO")
    print("  Rode: python verificar_duplicatas.py")
    print("=" * 70)

if __name__ == "__main__":
    main()
