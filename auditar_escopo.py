"""
NEXOR -- AUDITOR DE ESCOPO v1
Varre todos os quizzes e detecta questoes potencialmente fora de escopo
usando a API Anthropic para analise semantica por certificacao.
Gera relatorio detalhado com questoes suspeitas para revisao manual.

USO:
    python auditar_escopo.py
"""

import json
import os
import anthropic
from pathlib import Path
from datetime import datetime

QUIZZES_DIR = "static/quizzes"
MODEL       = "claude-sonnet-4-5"
MAX_TOKENS  = 4096
TIMESTAMP   = datetime.now().strftime("%Y%m%d_%H%M")
REPORT_FILE = f"auditoria_escopo_{TIMESTAMP}.txt"

# Escopo esperado por certificacao -- usado no prompt de auditoria
ESCOPO = {
    "cfe": {
        "name": "Certified Fraud Examiner (ACFE)",
        "scope": "US law (FCPA, SOX, RICO, BSA/AML, CFAA, Dodd-Frank), ACFE Fraud Examiners Manual, universal fraud theory (Fraud Triangle, Fraud Diamond), forensic accounting, interview techniques, legal elements of fraud. NO Brazilian law, NO LGPD, NO Lei Anticorrupcao 12.846, NO Brazilian regulators.",
        "forbidden": ["brasil", "brazilian law", "lei anticorrupcao", "lgpd", "mpf", "ministerio publico", "tcu", "cgu", "coaf brasil", "lei 12846", "improbidade", "codigo penal brasileiro"]
    },
    "cissp": {
        "name": "Certified Information Systems Security Professional (ISC2)",
        "scope": "ISC2 CBK 8 domains: Security and Risk Management, Asset Security, Security Architecture, Communication and Network Security, Identity and Access Management, Security Assessment, Security Operations, Software Development Security. Global scope, no country-specific law.",
        "forbidden": ["lei brasileira", "lgpd", "anpd", "lei 13709", "codigo penal", "ministerio publico"]
    },
    "cism": {
        "name": "Certified Information Security Manager (ISACA)",
        "scope": "ISACA CISM 4 domains: Information Security Governance, Information Risk Management, Information Security Program, Incident Management. Global framework, no country-specific law.",
        "forbidden": ["lei brasileira", "lgpd", "anpd", "ministerio publico", "tcu"]
    },
    "cisa": {
        "name": "Certified Information Systems Auditor (ISACA)",
        "scope": "ISACA CISA 5 domains: IS Audit Process, Governance, Systems Acquisition, IS Operations, Protection of Information Assets. Global framework.",
        "forbidden": ["lei brasileira", "lgpd", "anpd", "ministerio publico"]
    },
    "cciso": {
        "name": "Certified Chief Information Security Officer (EC-Council)",
        "scope": "EC-Council CCISO 5 domains: Governance, IS Controls, Management Projects Operations, Information Security Core Concepts, Strategic Planning. Global scope.",
        "forbidden": ["lei brasileira", "lgpd", "anpd"]
    },
    "crisc": {
        "name": "Certified in Risk and Information Systems Control (ISACA)",
        "scope": "ISACA CRISC 4 domains: Governance, IT Risk Assessment, Risk Response, Risk Monitoring. Global framework.",
        "forbidden": ["lei brasileira", "lgpd", "anpd"]
    },
    "cobit": {
        "name": "COBIT 2019 Foundation (ISACA)",
        "scope": "ISACA COBIT 2019 governance framework, design factors, focus areas, objectives. Global framework.",
        "forbidden": ["lei brasileira", "lgpd"]
    },
    "itil4": {
        "name": "ITIL 4 Foundation (Axelos)",
        "scope": "ITIL 4 service management framework: SVS, 4 dimensions, practices, guiding principles. Global framework.",
        "forbidden": ["lei brasileira", "lgpd"]
    },
    "iso27001_li": {
        "name": "ISO 27001 Lead Implementer",
        "scope": "ISO/IEC 27001:2022 and ISO/IEC 27002:2022, ISO 27005:2022 risk management, ISMS implementation. International standard.",
        "forbidden": ["lei brasileira", "lgpd especificamente", "anpd"]
    },
    "iso27001_la": {
        "name": "ISO 27001 Lead Auditor",
        "scope": "ISO/IEC 27001:2022 audit, ISO 19011 audit guidelines, certification audit process. International standard.",
        "forbidden": ["lei brasileira", "lgpd especificamente"]
    },
    "iso27701_li": {
        "name": "ISO 27701 Lead Implementer",
        "scope": "ISO/IEC 27701:2019 Privacy Information Management System. International standard. GDPR references acceptable as example.",
        "forbidden": ["lei brasileira especifica", "anpd"]
    },
    "iso22301_li": {
        "name": "ISO 22301 Lead Implementer",
        "scope": "ISO 22301:2019 Business Continuity Management System. International standard.",
        "forbidden": ["lei brasileira"]
    },
    "iso27005": {
        "name": "ISO 27005 Risk Manager",
        "scope": "ISO/IEC 27005:2022 information security risk management. International standard.",
        "forbidden": ["lei brasileira"]
    },
    "cippe": {
        "name": "Certified Information Privacy Professional Europe (IAPP)",
        "scope": "GDPR, European privacy law, ePrivacy Directive, EU data protection framework. European scope only.",
        "forbidden": ["lgpd", "lei brasileira", "anpd", "lei 13709", "brasil"]
    },
    "cipm": {
        "name": "Certified Information Privacy Manager (IAPP)",
        "scope": "Privacy program management, global privacy frameworks, GDPR, CCPA, privacy by design. Global scope.",
        "forbidden": ["lgpd especificamente como lei", "anpd"]
    },
    "cdpse": {
        "name": "Certified Data Privacy Solutions Engineer (ISACA)",
        "scope": "Privacy by design, data governance, technical privacy controls, global privacy regulations. Global scope.",
        "forbidden": ["lgpd como unica referencia", "anpd"]
    },
    "grcp": {
        "name": "Governance Risk Compliance Professional (OCEG)",
        "scope": "OCEG GRC capability model, integrated governance, risk and compliance. Global framework.",
        "forbidden": ["lei brasileira especifica"]
    },
}

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def keyword_check(question, forbidden_keywords):
    """Verificacao rapida por palavras-chave antes de chamar a API."""
    text = (
        question.get("text", "") + " " +
        question.get("justification_correct", "") + " " +
        question.get("justification_wrong", "") + " " +
        " ".join(question.get("options", []))
    ).lower()
    
    hits = []
    for kw in forbidden_keywords:
        if kw.lower() in text:
            hits.append(kw)
    return hits

def analyze_block_api(client, cert_id, questions_block):
    """Analise semantica via API para um bloco de questoes."""
    scope_info = ESCOPO.get(cert_id, {})
    
    questions_summary = []
    for q in questions_block:
        questions_summary.append({
            "num": q.get("num"),
            "tag": q.get("tag"),
            "text": q.get("text", "")[:200],
            "justification_correct": q.get("justification_correct", "")[:150]
        })
    
    prompt = f"""You are an expert certification exam quality auditor.

Review these exam questions for the {scope_info.get('name', cert_id)} certification.

EXPECTED SCOPE: {scope_info.get('scope', 'Global professional certification')}

For each question, determine if it is:
- IN_SCOPE: content correctly matches the certification scope
- OUT_OF_SCOPE: content references wrong jurisdiction, wrong laws, wrong framework
- SUSPICIOUS: content is borderline or potentially incorrect

Questions to review:
{json.dumps(questions_summary, ensure_ascii=False, indent=2)}

Return ONLY a JSON array with your assessment:
[{{"num": 1, "status": "IN_SCOPE", "reason": "brief reason if OUT_OF_SCOPE or SUSPICIOUS"}}]

Be strict. Flag anything that references country-specific law not in scope, wrong regulatory bodies, or incorrect jurisdictions."""

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.content[0].text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        return [{"num": q.get("num"), "status": "ERROR", "reason": str(e)} for q in questions_block]

def audit_quiz(client, cert_id, domain_id, quiz_file, report_lines):
    """Audita um arquivo de quiz."""
    try:
        data = load_json(quiz_file)
    except Exception as e:
        report_lines.append(f"  ERRO ao ler {quiz_file}: {e}")
        return 0, 0

    questions = data.get("questions", [])
    lang = data.get("lang", "?")
    
    # Apenas audita EN para evitar triplicar chamadas API
    if lang != "en":
        return 0, 0

    scope_info = ESCOPO.get(cert_id, {})
    forbidden = scope_info.get("forbidden", [])
    
    flagged = []
    
    # FASE 1: keyword check rapido
    keyword_flagged = []
    for q in questions:
        hits = keyword_check(q, forbidden)
        if hits:
            keyword_flagged.append((q, hits))
    
    # FASE 2: analise API em blocos de 10
    api_results = {}
    block_size = 10
    for i in range(0, len(questions), block_size):
        block = questions[i:i+block_size]
        results = analyze_block_api(client, cert_id, block)
        for r in results:
            api_results[r.get("num")] = r

    # Consolida resultados
    for q in questions:
        num = q.get("num")
        kw_hits = [hits for qq, hits in keyword_flagged if qq.get("num") == num]
        api_result = api_results.get(num, {})
        status = api_result.get("status", "UNKNOWN")
        reason = api_result.get("reason", "")
        
        if status in ("OUT_OF_SCOPE", "SUSPICIOUS") or kw_hits:
            flagged.append({
                "num": num,
                "tag": q.get("tag"),
                "status": status,
                "keyword_hits": kw_hits[0] if kw_hits else [],
                "reason": reason,
                "text": q.get("text", "")[:120]
            })

    # Registra no relatorio
    fname = os.path.basename(quiz_file)
    if flagged:
        report_lines.append(f"\n  [{cert_id}/{domain_id}/{fname}] — {len(flagged)} PROBLEMA(S)")
        for f in flagged:
            report_lines.append(f"    Q{f['num']} [{f['status']}] tag:{f['tag']}")
            if f['keyword_hits']:
                report_lines.append(f"      Keywords: {f['keyword_hits']}")
            if f['reason']:
                report_lines.append(f"      Razao: {f['reason']}")
            report_lines.append(f"      Texto: {f['text']}...")
    
    return len(questions), len(flagged)

def main():
    print("=" * 70)
    print("  NEXOR -- AUDITOR DE ESCOPO v1")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("  Analise semantica por certificacao via API")
    print("=" * 70)

    client = anthropic.Anthropic()
    
    report_lines = [
        f"NEXOR -- AUDITORIA DE ESCOPO -- {TIMESTAMP}",
        "=" * 70,
        "Questoes fora de escopo ou suspeitas por certificacao:",
        ""
    ]

    total_quizzes   = 0
    total_questions = 0
    total_flagged   = 0
    certs_com_problema = []

    # Varre toda a estrutura de quizzes
    base = Path(QUIZZES_DIR)
    for cert_dir in sorted(base.iterdir()):
        if not cert_dir.is_dir():
            continue
        cert_id = cert_dir.name
        
        if cert_id not in ESCOPO:
            print(f"\n  [{cert_id}] — sem perfil de escopo definido, pulando")
            continue

        print(f"\n  [{cert_id.upper()}] {ESCOPO[cert_id]['name']}")
        cert_flagged = 0

        for domain_dir in sorted(cert_dir.iterdir()):
            if not domain_dir.is_dir():
                continue
            domain_id = domain_dir.name

            for quiz_file in sorted(domain_dir.glob("quiz_*_en.json")):
                fname = quiz_file.name
                print(f"    {domain_id}/{fname} ... ", end="", flush=True)
                
                nq, nf = audit_quiz(client, cert_id, domain_id, str(quiz_file), report_lines)
                total_quizzes   += 1
                total_questions += nq
                total_flagged   += nf
                cert_flagged    += nf
                
                status = f"OK ({nq}q)" if nf == 0 else f"⚠️  {nf} PROBLEMA(S) em {nq}q"
                print(status)

        if cert_flagged > 0:
            certs_com_problema.append(f"{cert_id}: {cert_flagged} problema(s)")

    # Resumo final
    report_lines += [
        "",
        "=" * 70,
        "RESUMO",
        "=" * 70,
        f"Quizzes auditados (EN): {total_quizzes}",
        f"Questoes analisadas   : {total_questions}",
        f"Problemas detectados  : {total_flagged}",
        "",
        "Certificacoes com problemas:",
    ]
    for c in certs_com_problema:
        report_lines.append(f"  · {c}")

    if not certs_com_problema:
        report_lines.append("  Nenhuma — catalogo limpo.")

    # Salva relatorio
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print("\n" + "=" * 70)
    print(f"  CONCLUIDO")
    print(f"  Quizzes auditados : {total_quizzes}")
    print(f"  Questoes          : {total_questions}")
    print(f"  Problemas         : {total_flagged}")
    print(f"  Relatorio         : {REPORT_FILE}")
    print("=" * 70)

if __name__ == "__main__":
    main()
