"""
NEXOR -- CORRETOR OUT_OF_SCOPE NAO-CFE v1
Substitui as 12 questoes OUT_OF_SCOPE identificadas
na auditoria v2 para CCISO, CDPSE, CISM e ISO27001_LI.
Atualiza PT e ES automaticamente.

USO:
    python corrigir_outofscope_v2.py
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

# Mapa exato de questoes OUT_OF_SCOPE por arquivo
# Formato: "cert/domain/quiz_NNN_en.json": [nums]
OUT_OF_SCOPE_MAP = {
    "cciso/controls_audit_assurance/quiz_001_en.json": [26, 41, 45],
    "cciso/governance_risk_compliance/quiz_001_en.json": [1, 4, 6],
    "cdpse/privacy_governance_cdpse/quiz_001_en.json": [5],
    "cism/incident_management/quiz_001_en.json": [11],
    "cism/info_risk_management/quiz_002_en.json": [21],
    "cism/info_security_governance/quiz_002_en.json": [4],
    "cism/info_security_governance/quiz_004_en.json": [23],
    "iso27001_li/fundamentals_isms/quiz_004_en.json": [14],
}

# Escopo correto por certificacao para prompt de geracao
ESCOPO_CERT = {
    "cciso": """CCISO (EC-Council) Domain: Information Security Controls, Audit, Policy and Compliance.
SCOPE: Strategic CISO-level security leadership decisions. Controls must have IS security angle.
References to COSO, ISO 27001, COBIT, SOX are acceptable ONLY when connected to information security governance.
Questions must require CISO strategic thinking, NOT generic financial audit or pure accounting content.
Generate a replacement question about information security controls with CISO strategic leadership angle.""",

    "cdpse": """CDPSE (ISACA) Domain: Privacy Governance.
SCOPE: Technical privacy controls, data governance, privacy engineering, global privacy regulations.
GDPR, CCPA, LGPD references acceptable as regulatory context for privacy technical implementation.
Generate a replacement question about privacy governance from a technical privacy engineering perspective.""",

    "cism": """CISM (ISACA) Domain: varies by domain below.
SCOPE: Information security management - governance, risk management, program management, incident management.
Global management framework. Focus on management decisions, not technical implementation details.
Generate a replacement question appropriate for CISM management level.""",

    "iso27001_li": """ISO 27001 Lead Implementer.
SCOPE: ISO/IEC 27001:2022 and ISO 27002:2022 ISMS implementation.
ISO 27005:2022 risk management. International standard.
GDPR references acceptable as compliance driver for ISMS.
Generate a replacement question about ISMS implementation per ISO 27001:2022.""",
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
    escopo = ESCOPO_CERT.get(cert_id, "Professional certification exam.")
    old_tag = old_question.get("tag", "unknown")

    # Ajusta escopo para CISM por dominio
    if cert_id == "cism":
        domain_map = {
            "incident_management": "Incident Management — IR planning, playbooks, tabletop exercises, DR integration",
            "info_risk_management": "Information Risk Management — risk assessment, treatment, ISO 27005",
            "info_security_governance": "Information Security Governance — CISO role, board reporting, strategy alignment",
            "security_program": "Information Security Program — program development, metrics, awareness",
        }
        domain_scope = domain_map.get(domain_id, domain_id)
        escopo = f"CISM (ISACA) Domain: {domain_scope}. SCOPE: Management-level decisions. Global framework."

    prompt = f"""You are an expert certification exam question writer.

CERTIFICATION: {cert_id.upper()}
DOMAIN: {domain_id}

{escopo}

The following question was flagged as OUT_OF_SCOPE and must be replaced:
Tag: {old_tag}
Original text: {old_question.get('text', '')[:200]}

Generate exactly 1 replacement question that:
- Is clearly IN SCOPE for {cert_id.upper()} {domain_id}
- Covers a similar or related topic to tag: {old_tag}
- Is at advanced professional certification level
- Has 4 plausible options with one unambiguous correct answer
- Includes detailed justification

Return ONLY a valid JSON array with one object, no markdown:
[{{
  "num": {num},
  "text": "Full question text",
  "tag": "topic_snake_case",
  "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "correct": 0,
  "justification_correct": "Detailed explanation",
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
4. Keep technical terms in English when standard
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

def process_file(client, file_key, out_of_scope_nums):
    parts     = file_key.split("/")
    cert_id   = parts[0]
    domain_id = parts[1]
    quiz_fname = parts[2]

    en_path = Path(QUIZZES_DIR) / cert_id / domain_id / quiz_fname
    if not en_path.exists():
        print(f"  ARQUIVO NAO ENCONTRADO: {en_path}")
        return

    backup(str(en_path))
    en_data = load_json(str(en_path))
    questions = en_data["questions"]

    # Mapa por num para acesso rapido
    q_map = {q["num"]: q for q in questions}
    new_questions = []

    for num in sorted(out_of_scope_nums):
        old_q = q_map.get(num)
        if not old_q:
            print(f"    Q{num}: nao encontrada no arquivo")
            continue

        print(f"  Q{num} [{old_q.get('tag','')}] → gerando substituta... ", end="", flush=True)
        new_q = generate_replacement(client, cert_id, domain_id, old_q, num)

        if new_q:
            q_map[num] = new_q
            new_questions.append(new_q)
            print(f"OK [{new_q.get('tag','')}]")
        else:
            print("FALHOU — mantendo original")

    # Reconstroi lista ordenada
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
        lang_data = load_json(str(lang_path))
        lang_questions = lang_data["questions"]
        lang_map = {q["num"]: q for q in lang_questions}

        for new_q in new_questions:
            num = new_q["num"]
            print(f"  Traduzindo Q{num} para {lang_code.upper()}... ", end="", flush=True)
            translated = translate_question(client, new_q, lang_name)
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
    print("  NEXOR -- CORRETOR OUT_OF_SCOPE NAO-CFE v1")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)

    client = anthropic.Anthropic()

    total_files = len(OUT_OF_SCOPE_MAP)
    total_q     = sum(len(v) for v in OUT_OF_SCOPE_MAP.values())
    print(f"\n  Arquivos : {total_files}")
    print(f"  Questoes : {total_q} OUT_OF_SCOPE a substituir")

    for file_key, nums in OUT_OF_SCOPE_MAP.items():
        print(f"\n{'─'*70}")
        print(f"  {file_key}")
        print(f"  Questoes OUT_OF_SCOPE: {sorted(nums)}")
        print(f"{'─'*70}")
        process_file(client, file_key, nums)

    print("\n" + "=" * 70)
    print("  CONCLUIDO")
    print("  Rode: python verificar_duplicatas.py")
    print("  Rode: python auditar_escopo_v2.py (confirmar)")
    print("=" * 70)

if __name__ == "__main__":
    main()
