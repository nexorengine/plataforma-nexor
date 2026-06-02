"""
NEXOR -- GERADOR quiz_001 CISM security_program v1
Gera 50 questoes EN + traduz PT e ES automaticamente.
Topicos: fundamentos do programa, charter, alinhamento estrategico,
roadmap, estrutura organizacional do programa de SI.
"""

import json
import anthropic
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = r"static\quizzes\cism\security_program"
MODEL      = "claude-sonnet-4-5"
MAX_TOKENS = 8192

TOPICOS = [
    "information_security_program_definition_scope",
    "security_program_charter_components",
    "security_program_strategic_alignment_business",
    "ciso_role_program_leadership",
    "security_program_roadmap_development",
    "program_objectives_and_goals_setting",
    "security_program_governance_structure",
    "board_executive_engagement_security_program",
    "security_program_scope_boundaries",
    "stakeholder_identification_security_program",
    "security_program_mission_and_vision",
    "aligning_security_program_with_enterprise_architecture",
    "security_program_business_case_development",
    "information_security_strategy_development",
    "security_program_maturity_assessment",
    "capability_maturity_model_cmm_security",
    "security_program_gap_analysis",
    "security_program_success_factors",
    "integration_security_program_business_processes",
    "security_program_organizational_structure",
    "centralized_vs_decentralized_security_model",
    "security_steering_committee_role",
    "security_program_reporting_structure",
    "security_program_documentation_requirements",
    "information_security_program_lifecycle",
    "security_program_change_management",
    "security_program_communication_plan",
    "security_program_continuous_improvement_cycle",
    "risk_appetite_influence_on_security_program",
    "security_program_legal_regulatory_alignment",
    "security_program_insurance_considerations",
    "security_program_outsourcing_considerations",
    "security_program_internal_audit_relationship",
    "security_program_external_audit_relationship",
    "security_program_benchmarking_industry_standards",
    "iso27001_framework_security_program",
    "nist_csf_integration_security_program",
    "cobit_alignment_security_program",
    "security_program_performance_indicators_kpi",
    "security_program_dashboard_reporting",
    "security_program_executive_reporting",
    "security_program_budget_planning",
    "security_program_roi_justification",
    "security_program_resource_allocation",
    "security_program_staffing_model",
    "security_program_skills_gap_assessment",
    "security_program_technology_portfolio",
    "security_program_vendor_selection_criteria",
    "security_program_contract_management",
    "security_program_effectiveness_measurement",
]

LANG_CONFIG = {
    "pt": {"lang_name":"Portugues (Brasil)","domain_name":"Programa de Segurança da Informação","cert_name":"Certified Information Security Manager"},
    "es": {"lang_name":"Espanol (neutro latinoamericano)","domain_name":"Programa de Seguridad de la Informacion","cert_name":"Certified Information Security Manager"},
}

def save_json(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def call_api(client, prompt):
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role":"user","content":prompt}]
    )
    raw = response.content[0].text.strip()
    raw = raw.replace("```json","").replace("```","").strip()
    return json.loads(raw)

def generate_block(client, topicos, num_start):
    topicos_str = "\n".join(f"  - {t}" for t in topicos)
    prompt = f"""You are an expert CISM exam question writer.

Generate exactly {len(topicos)} unique exam questions for:
- Certification: CISM (Certified Information Security Manager)
- Domain: Information Security Program (Domain 3)
- Language: English
- Level: Advanced professional certification

TOPICS (one question per topic in this exact order):
{topicos_str}

Start numbering from num={num_start}.

IMPORTANT CONTEXT — This domain covers:
Building, managing, and operating the information security program.
It is DISTINCT from:
- Governance (Domain 1): organizational structures and strategy
- Risk Management (Domain 2): risk identification and treatment
- Incident Management (Domain 4): incident response and recovery

QUALITY REQUIREMENTS:
- Scenario-based or conceptual CISM style questions
- Advanced professional level difficulty
- All 4 options must be plausible and professionally written
- Correct answer must be unambiguous and defensible per CISM Review Manual
- Justifications must be detailed and technically accurate
- Do NOT repeat concepts from Incident Management or Risk Management domains

Return ONLY a valid JSON array, no markdown, no explanation:
[{{"num":{num_start},"text":"...","tag":"topic_snake_case","options":["A. ...","B. ...","C. ...","D. ..."],"correct":0,"justification_correct":"...","justification_wrong":"..."}}]"""

    try:
        return call_api(client, prompt)
    except Exception as e:
        print(f"\n    Erro no bloco: {e}. Tentando individual...")
        results = []
        for i, topico in enumerate(topicos):
            print(f"    Q{num_start+i} ({topico})... ", end="", flush=True)
            try:
                p2 = f"""Generate exactly 1 CISM exam question for domain Information Security Program.
Topic: {topico}
num: {num_start+i}
Language: English
Level: Advanced professional
Return ONLY a JSON array with one object, no markdown."""
                qs = call_api(client, p2)
                if isinstance(qs, list):
                    qs[0]["num"] = num_start + i
                    results.append(qs[0])
                else:
                    qs["num"] = num_start + i
                    results.append(qs)
                print("OK")
            except Exception as e2:
                print(f"FALHOU: {e2}")
        return results

def translate_block(client, questions, lang_name):
    block_json = json.dumps(questions, ensure_ascii=False, indent=2)
    prompt = f"""Translate these CISM exam questions from English to {lang_name}.

RULES:
1. Translate ONLY: "text", "options", "justification_correct", "justification_wrong"
2. DO NOT modify: "num", "tag", "correct"
3. Keep prefixes exactly: "A. ", "B. ", "C. ", "D. "
4. Use standard {lang_name} information security terminology
5. Return ONLY the JSON array, no markdown

Input:
{block_json}"""
    try:
        return call_api(client, prompt)
    except Exception as e:
        print(f"\n    Erro no bloco: {e}. Tentando individual...")
        results = []
        for q in questions:
            try:
                p2 = prompt.replace(block_json, json.dumps([q], ensure_ascii=False, indent=2))
                r = call_api(client, p2)
                results.append(r[0])
            except:
                results.append(q)
        return results

def main():
    print("="*70)
    print("  NEXOR -- GERADOR quiz_001 CISM security_program v1")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("="*70)
    print(f"\n  Topicos: {len(TOPICOS)}")
    print(f"  Meta   : 50 questoes EN + PT + ES")

    client = anthropic.Anthropic()

    # FASE 1: GERAR EN
    print(f"\n{'─'*70}")
    print("  FASE 1: GERACAO EM INGLES")
    print(f"{'─'*70}")

    all_en = []
    block_size = 10
    num_start = 1

    for i in range(0, len(TOPICOS), block_size):
        bloco = TOPICOS[i:i+block_size]
        end = num_start + len(bloco) - 1
        print(f"\n  Bloco Q{num_start}-Q{end} ({len(bloco)}q)... ", end="", flush=True)
        qs = generate_block(client, bloco, num_start)
        for j, q in enumerate(qs):
            q["num"] = num_start + j
        all_en.extend(qs)
        num_start += len(qs)
        print(f"OK ({len(qs)}q)")

    # Renumera sequencialmente
    for i, q in enumerate(all_en):
        q["num"] = i + 1

    quiz_en = {
        "cert_id":     "cism",
        "domain_id":   "security_program",
        "quiz_num":    1,
        "domain_name": "Information Security Program",
        "cert_name":   "Certified Information Security Manager",
        "lang":        "en",
        "questions":   all_en
    }
    out_en = Path(OUTPUT_DIR) / "quiz_001_en.json"
    save_json(str(out_en), quiz_en)
    print(f"\n  Salvo: {out_en} ({len(all_en)}q)")

    # FASE 2: TRADUCOES
    print(f"\n{'─'*70}")
    print("  FASE 2: TRADUCOES PT e ES")
    print(f"{'─'*70}")

    for lang_code, lang_cfg in LANG_CONFIG.items():
        print(f"\n  [{lang_code.upper()}] Traduzindo {len(all_en)} questoes...")
        translated = []

        for i in range(0, len(all_en), 10):
            bloco = all_en[i:i+10]
            print(f"  Q{bloco[0]['num']}-Q{bloco[-1]['num']}... ", end="", flush=True)
            t = translate_block(client, bloco, lang_cfg["lang_name"])
            translated.extend(t)
            print("OK")

        for i, q in enumerate(translated):
            q["num"] = i + 1

        quiz_lang = {
            "cert_id":     "cism",
            "domain_id":   "security_program",
            "quiz_num":    1,
            "domain_name": lang_cfg["domain_name"],
            "cert_name":   lang_cfg["cert_name"],
            "lang":        lang_code,
            "questions":   translated
        }
        out_path = Path(OUTPUT_DIR) / f"quiz_001_{lang_code}.json"
        save_json(str(out_path), quiz_lang)
        print(f"  Salvo: {out_path} ({len(translated)}q)")

    print("\n" + "="*70)
    print("  CONCLUIDO")
    print("  Rode: python verificar_duplicatas.py")
    print("="*70)

if __name__ == "__main__":
    main()
