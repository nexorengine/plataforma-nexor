"""
NEXOR -- GERADOR quiz_002 CISM incident_management v2
Gera 50 questoes completas do zero.
As 6 questoes ja existentes estao embutidas no script.
Gera EN + traduz PT e ES automaticamente.
"""

import json
import anthropic
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = r"static\quizzes\cism\incident_management"
MODEL      = "claude-sonnet-4-5"
MAX_TOKENS = 8192

# As 6 questoes ja existentes -- embutidas diretamente
Q_EXISTENTES = [
    {"num":1,"text":"When does an incident responder look at an incident response playbook?","tag":"playbook_usage_timing","options":["A. Before an incident occurs, to prepare for a simulated incident","B. During an incident, to understand the steps required to respond to a specific type of incident","C. After an incident, to understand how to improve incident response procedures","D. During an incident, to understand who to escalate the incident to"],"correct":1,"justification_correct":"An incident response playbook contains specific, detailed, technical steps required to respond to a particular type of incident. Incident responders consult the playbook during an active incident to ensure all necessary steps are taken.","justification_wrong":"A is incorrect because simulations use the IRP or scenario documents, not playbooks. C is incorrect because post-incident review improves the IRP, not the playbook itself. D is incorrect because escalation paths are defined in the IRP, not the playbook."},
    {"num":2,"text":"An organization is developing an incident response playbook for ransomware attacks. Which of the following steps should be included in the containment phase?","tag":"ransomware_containment_actions","options":["A. Disconnecting affected systems from the network","B. Restoring data from backups","C. Identifying the vulnerabilities that allowed the attack to occur","D. Notifying law enforcement"],"correct":0,"justification_correct":"Containment aims to limit damage and prevent spread. Disconnecting affected systems stops ransomware from encrypting additional systems and terminates C2 communication.","justification_wrong":"B is recovery phase. C is post-incident root-cause analysis. D is a notification activity, not containment."},
    {"num":3,"text":"An organization has experienced a security breach involving the theft of customer PII. The incident response team has contained the incident. What is the next most appropriate step?","tag":"ir_lifecycle_eradication_after_containment","options":["A. Eradicate the cause of the incident.","B. Conduct a lessons-learned meeting.","C. Notify affected customers and regulators.","D. Restore systems to normal operations."],"correct":0,"justification_correct":"Following containment, eradication removes the root cause from the environment before recovery begins.","justification_wrong":"B is the closure phase after recovery. C typically follows eradication and recovery. D occurs after eradication is complete."},
    {"num":4,"text":"Why is it important to capture and preserve a bit-stream image of a compromised system hard drive during an investigation?","tag":"forensic_imaging_chain_of_custody","options":["A. To ensure that the system can be restored quickly if needed","B. To permit a forensic analysis to be performed without altering the original evidence","C. To compress the data so that it can be transmitted to an external investigator more easily","D. To encrypt the data to protect it from unauthorized access"],"correct":1,"justification_correct":"A bit-stream forensic image preserves original evidence in an unaltered state, allowing investigators to analyze a copy while maintaining chain of custody for legally defensible findings.","justification_wrong":"A is incorrect because forensic images are not used for system restoration. C is incorrect because forensic imaging does not compress data. D is incorrect because the primary purpose is preservation, not encryption."},
    {"num":5,"text":"What is the primary objective of the lessons learned phase of incident response?","tag":"lessons_learned_phase_objective","options":["A. To assign blame to the individuals responsible for the incident","B. To calculate the total financial cost of the incident","C. To identify areas of improvement in the organization's security posture and incident response capabilities","D. To document the incident for law enforcement purposes"],"correct":2,"justification_correct":"The lessons learned phase reviews the incident and response to identify weaknesses in controls, processes, and capabilities, driving continuous improvement to prevent or better respond to future incidents.","justification_wrong":"A is counterproductive and not the purpose. B may occur but is not the primary objective. D is a separate legal and forensic activity."},
    {"num":6,"text":"A security analyst is reviewing network traffic logs and notices high volume traffic from a single internal IP address directed toward an external IP address known to host malicious C2 servers. Which phase of the IR lifecycle is this?","tag":"detection_analysis_phase_c2_traffic","options":["A. Preparation","B. Detection and Analysis","C. Containment, Eradication, and Recovery","D. Post-Incident Activity"],"correct":1,"justification_correct":"Reviewing logs and identifying anomalous traffic patterns indicating potential compromise are core Detection and Analysis phase activities.","justification_wrong":"A is pre-incident capability building. C follows after detection and analysis. D occurs after full resolution."},
]

# 44 topicos novos para os slots restantes
TOPICOS_ALVO = [
    "chain_of_custody_digital_evidence",
    "volatile_data_collection_order_of_volatility",
    "forensic_tools_and_techniques",
    "evidence_admissibility_legal_requirements",
    "memory_forensics_ram_acquisition",
    "phishing_attack_indicators_and_response",
    "insider_threat_detection_indicators",
    "advanced_persistent_threat_apt_characteristics",
    "sql_injection_attack_response",
    "man_in_the_middle_attack_identification",
    "zero_day_vulnerability_response",
    "brute_force_attack_detection_response",
    "social_engineering_incident_handling",
    "network_segmentation_containment_strategy",
    "malware_analysis_static_dynamic",
    "rootkit_detection_and_removal",
    "credential_compromise_response_steps",
    "data_exfiltration_detection_indicators",
    "ransomware_recovery_strategy",
    "supply_chain_attack_response",
    "law_enforcement_notification_criteria",
    "regulatory_notification_requirements_breach",
    "affected_party_notification_best_practices",
    "internal_stakeholder_communication_ir",
    "public_disclosure_timing_strategy",
    "ir_metrics_mean_time_to_detect",
    "ir_metrics_mean_time_to_respond",
    "ir_metrics_mean_time_to_contain",
    "post_incident_report_structure",
    "ir_program_continuous_improvement",
    "computer_crime_laws_cfaa",
    "privacy_regulations_incident_impact",
    "legal_hold_and_litigation_support",
    "regulatory_compliance_during_incident",
    "siem_role_in_incident_detection",
    "edr_endpoint_detection_response_tools",
    "threat_intelligence_platform_usage",
    "network_traffic_analysis_tools",
    "log_management_incident_investigation",
    "ir_team_structure_roles",
    "ir_program_governance_framework",
    "third_party_ir_coordination",
    "cyber_insurance_incident_implications",
    "ir_budget_justification_risk_based",
]

LANG_CONFIG = {
    "pt": {"lang_name":"Portugues (Brasil)","domain_name":"Gestao de Incidentes","cert_name":"Certified Information Security Manager"},
    "es": {"lang_name":"Espanol (neutro latinoamericano)","domain_name":"Gestion de Incidentes","cert_name":"Certified Information Security Manager"},
}

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
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

Generate exactly {len(topicos)} unique exam questions for CISM Incident Management domain in English.
Start numbering from num={num_start}.

TOPICS (one question per topic in this order):
{topicos_str}

REQUIREMENTS:
- Scenario-based or conceptual CISM style
- Advanced professional level
- All 4 options plausible and distinct
- Correct answer unambiguous per CISM Review Manual
- Detailed technical justifications

Return ONLY a valid JSON array, no markdown:
[{{"num":{num_start},"text":"...","tag":"topic_snake_case","options":["A. ...","B. ...","C. ...","D. ..."],"correct":0,"justification_correct":"...","justification_wrong":"..."}}]"""

    try:
        return call_api(client, prompt)
    except Exception as e:
        print(f"\n    Erro no bloco: {e}. Tentando individual...")
        results = []
        for i, topico in enumerate(topicos):
            print(f"    Q{num_start+i} ({topico})... ", end="", flush=True)
            try:
                p2 = prompt.replace(topicos_str, f"  - {topico}").replace(f"exactly {len(topicos)}", "exactly 1").replace(f"num={num_start}", f"num={num_start+i}")
                qs = call_api(client, p2)
                qs[0]["num"] = num_start + i
                results.append(qs[0])
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
4. Use standard {lang_name} infosec terminology
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
    print("  NEXOR -- GERADOR quiz_002 CISM incident_management v2")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("="*70)
    print(f"\n  Questoes existentes (embutidas): {len(Q_EXISTENTES)}")
    print(f"  A gerar: {50 - len(Q_EXISTENTES)} questoes novas")

    client = anthropic.Anthropic()

    # FASE 1: GERAR EN
    print(f"\n{'─'*70}")
    print("  FASE 1: GERACAO EM INGLES")
    print(f"{'─'*70}")

    novas_en = []
    block_size = 11
    num_start = len(Q_EXISTENTES) + 1

    for i in range(0, len(TOPICOS_ALVO), block_size):
        bloco = TOPICOS_ALVO[i:i+block_size]
        end = num_start + len(bloco) - 1
        print(f"\n  Bloco Q{num_start}-Q{end} ({len(bloco)}q)... ", end="", flush=True)
        qs = generate_block(client, bloco, num_start)
        for j, q in enumerate(qs):
            q["num"] = num_start + j
        novas_en.extend(qs)
        num_start += len(qs)
        print(f"OK ({len(qs)}q geradas)")

    all_en = Q_EXISTENTES + novas_en
    for i, q in enumerate(all_en):
        q["num"] = i + 1

    quiz_en = {"cert_id":"cism","domain_id":"incident_management","quiz_num":2,"domain_name":"Incident Management","cert_name":"Certified Information Security Manager","lang":"en","questions":all_en}
    out_en = Path(OUTPUT_DIR) / "quiz_002_en.json"
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

        quiz_lang = {"cert_id":"cism","domain_id":"incident_management","quiz_num":2,"domain_name":lang_cfg["domain_name"],"cert_name":lang_cfg["cert_name"],"lang":lang_code,"questions":translated}
        out_path = Path(OUTPUT_DIR) / f"quiz_002_{lang_code}.json"
        save_json(str(out_path), quiz_lang)
        print(f"  Salvo: {out_path} ({len(translated)}q)")

    print("\n" + "="*70)
    print("  CONCLUIDO")
    print("  Rode: python verificar_duplicatas.py")
    print("="*70)

if __name__ == "__main__":
    main()
