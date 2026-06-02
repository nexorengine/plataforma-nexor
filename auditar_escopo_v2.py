"""
NEXOR -- AUDITOR DE ESCOPO v2
Criterios calibrados por certificacao.
Distingue entre referencia legitima (exemplo) e tema central errado.
Audita apenas arquivos _en.json.

USO:
    python auditar_escopo_v2.py
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
REPORT_FILE = f"auditoria_escopo_v2_{TIMESTAMP}.txt"

# Criterios calibrados por certificacao
# referenced_ok: pode aparecer como EXEMPLO ou CONTEXTO
# central_forbidden: NAO pode ser o TEMA CENTRAL da questao
ESCOPO_V2 = {
    "cfe": {
        "name": "Certified Fraud Examiner (ACFE)",
        "description": "ACFE CFE exam covers fraud theory, financial crimes, fraud investigation, fraud prevention. Primary legal framework is US law (FCPA, SOX, RICO, BSA/AML, CFAA, Dodd-Frank). Universal fraud principles apply globally.",
        "referenced_ok": ["SOX", "FCPA", "RICO", "BSA", "AML", "CFAA", "Dodd-Frank", "GDPR as example", "money laundering", "bribery", "corruption"],
        "central_forbidden": ["Brazilian law", "Lei Anticorrupcao 12.846", "LGPD", "Brazilian Penal Code", "MPF", "TCU", "CGU", "COAF Brazil specific", "Lei de Improbidade", "Portuguese law", "Argentine law"],
        "level_note": "Professional level questions appropriate. Scenario-based fraud cases acceptable regardless of country if law cited is correct."
    },
    "cissp": {
        "name": "Certified Information Systems Security Professional (ISC2)",
        "description": "ISC2 CBK 8 domains. Global scope. References to GDPR, HIPAA, SOX, PCI-DSS acceptable as EXAMPLES of regulatory requirements. Questions should not be exclusively about one country law.",
        "referenced_ok": ["GDPR as example", "HIPAA as example", "SOX as example", "PCI-DSS", "NIST", "ISO 27001", "FIPS", "common law principles"],
        "central_forbidden": ["Brazilian law as primary topic", "LGPD as sole focus", "country-specific law as the only answer"],
        "level_note": "Advanced professional level. Technical depth expected."
    },
    "cism": {
        "name": "Certified Information Security Manager (ISACA)",
        "description": "ISACA CISM 4 domains. Global management framework. References to specific regulations (GDPR, SOX, HIPAA) acceptable as governance examples. Focus should be on management decisions not law compliance details.",
        "referenced_ok": ["GDPR as governance example", "SOX as compliance example", "NIST CSF", "ISO 27001", "COBIT", "regulatory compliance concept"],
        "central_forbidden": ["Brazilian law as topic", "LGPD as primary focus", "country-specific regulatory details as exam content"],
        "level_note": "Management and governance focus. Not technical implementation details."
    },
    "cisa": {
        "name": "Certified Information Systems Auditor (ISACA)",
        "description": "ISACA CISA 5 domains. Global audit framework. References to SOX, GDPR, COBIT, ITIL acceptable as audit context examples.",
        "referenced_ok": ["SOX as audit example", "GDPR as compliance example", "COBIT", "ITIL", "ISO 27001", "IIA standards", "PCAOB as example"],
        "central_forbidden": ["Brazilian law as primary topic", "country-specific audit law as sole focus"],
        "level_note": "IS audit focus. IT governance and controls."
    },
    "cciso": {
        "name": "Certified Chief Information Security Officer (EC-Council)",
        "description": "EC-Council CCISO 5 domains. Strategic security leadership. References to SOX, HIPAA, GDPR, PCI-DSS acceptable as compliance governance examples. COSO, IIA, ISAE acceptable as audit framework references. Focus should be on CISO strategic decisions.",
        "referenced_ok": ["SOX as compliance example", "HIPAA as compliance example", "GDPR as privacy governance", "COSO as control framework", "IIA standards", "ISAE", "PCI-DSS", "NIST", "ISO 27001"],
        "central_forbidden": ["Brazilian law as topic", "LGPD as primary focus", "questions that are purely about financial audit with no IS angle"],
        "level_note": "Strategic CISO level. Questions should have IS security leadership angle even when referencing other frameworks."
    },
    "crisc": {
        "name": "Certified in Risk and Information Systems Control (ISACA)",
        "description": "ISACA CRISC 4 domains. IT risk management. References to COBIT, ISO 27005, NIST RMF, regulatory frameworks acceptable as context.",
        "referenced_ok": ["COBIT", "ISO 27005", "NIST RMF", "GDPR as risk example", "SOX as risk context", "Basel as financial risk example"],
        "central_forbidden": ["Brazilian law as primary topic", "country-specific risk regulation as sole focus"],
        "level_note": "IT risk management focus."
    },
    "cobit": {
        "name": "COBIT 2019 Foundation (ISACA)",
        "description": "ISACA COBIT 2019 governance framework. Pure framework content. Design factors, focus areas, governance objectives. No country-specific law expected.",
        "referenced_ok": ["ISO 27001 as example", "ITIL as example", "NIST as example", "regulatory compliance as design factor"],
        "central_forbidden": ["country-specific law as primary topic", "Brazilian law", "LGPD", "SOX details beyond governance concept"],
        "level_note": "Foundation level. Framework concepts only."
    },
    "itil4": {
        "name": "ITIL 4 Foundation (Axelos)",
        "description": "ITIL 4 Foundation. Service management framework. SVS, 4 dimensions, 34 practices, guiding principles. DevOps, Agile, Lean references are LEGITIMATE in ITIL 4 as it explicitly integrates these. Foundation level scope applies.",
        "referenced_ok": ["DevOps", "Agile", "Lean", "SRE", "service value chain", "practices", "guiding principles", "SVS"],
        "central_forbidden": ["country-specific law", "Brazilian law", "financial audit standards as primary topic", "practitioner-level detail beyond Foundation concepts"],
        "level_note": "CRITICAL: DevOps, Agile, Lean ARE in scope for ITIL 4. Flag only if content is clearly beyond Foundation level or about country-specific law. Truncated questions should be flagged separately."
    },
    "iso27001_li": {
        "name": "ISO 27001 Lead Implementer",
        "description": "ISO/IEC 27001:2022 and ISO 27002:2022 implementation. GDPR references are LEGITIMATE as privacy is addressed in ISO 27001 Annex A controls. SOX references acceptable as compliance context. Focus on ISMS implementation.",
        "referenced_ok": ["GDPR as privacy control example", "SOX as compliance requirement example", "ISO 27005", "ISO 27002", "NIST CSF", "COBIT", "regulatory compliance as ISMS driver"],
        "central_forbidden": ["Brazilian law as primary topic", "LGPD as sole focus replacing ISO content", "non-ISO framework as the only answer"],
        "level_note": "Lead Implementer level. GDPR and other regulations are LEGITIMATE references in ISO 27001 context."
    },
    "iso27001_la": {
        "name": "ISO 27001 Lead Auditor",
        "description": "ISO/IEC 27001:2022 audit. ISO 19011 audit guidelines. Certification audit process. GDPR acceptable as compliance context in audits.",
        "referenced_ok": ["GDPR as audit finding context", "ISO 19011", "ISO 17021", "regulatory compliance in audit scope"],
        "central_forbidden": ["Brazilian law as primary topic", "country-specific audit law replacing ISO audit standards"],
        "level_note": "Lead Auditor level. ISO audit standards focus."
    },
    "iso27701_li": {
        "name": "ISO 27701 Lead Implementer",
        "description": "ISO/IEC 27701:2019 PIMS. Privacy extension to ISO 27001. GDPR references are HIGHLY LEGITIMATE as ISO 27701 was designed with GDPR alignment. LGPD references acceptable as privacy law example.",
        "referenced_ok": ["GDPR extensively", "LGPD as privacy law example", "CCPA as privacy law example", "ISO 27001", "privacy by design", "data subject rights"],
        "central_forbidden": ["content unrelated to privacy management", "security-only content with no privacy angle"],
        "level_note": "GDPR and privacy law references are core content for ISO 27701."
    },
    "iso22301_li": {
        "name": "ISO 22301 Lead Implementer",
        "description": "ISO 22301:2019 BCMS. Business continuity management. International standard. No country-specific law expected.",
        "referenced_ok": ["ISO 31000", "ISO 27001 relationship", "regulatory BCP requirements as examples"],
        "central_forbidden": ["Brazilian law as primary topic", "country-specific BCP regulation as sole focus"],
        "level_note": "International standard focus."
    },
    "iso27005": {
        "name": "ISO 27005 Risk Manager",
        "description": "ISO/IEC 27005:2022 information security risk management. International standard.",
        "referenced_ok": ["ISO 31000", "NIST RMF as comparison", "regulatory risk requirements as context"],
        "central_forbidden": ["Brazilian law as primary topic", "country-specific risk regulation"],
        "level_note": "International standard focus."
    },
    "cippe": {
        "name": "Certified Information Privacy Professional Europe (IAPP)",
        "description": "IAPP CIPP/E. European privacy law. GDPR is THE primary framework. ePrivacy Directive. EU data protection. LGPD and other non-EU laws should NOT be primary topic.",
        "referenced_ok": ["GDPR extensively", "ePrivacy Directive", "EU Charter", "adequacy decisions", "SCCs", "BCRs", "EDPB guidelines"],
        "central_forbidden": ["LGPD as primary topic", "CCPA as primary topic", "Brazilian law", "non-EU privacy law as central focus"],
        "level_note": "European privacy law exclusively. Non-EU references only acceptable as comparison examples."
    },
    "cipm": {
        "name": "Certified Information Privacy Manager (IAPP)",
        "description": "IAPP CIPM. Privacy program management. Global scope. GDPR, CCPA, LGPD all acceptable as examples of privacy laws in a global program context.",
        "referenced_ok": ["GDPR as example", "CCPA as example", "LGPD as example", "privacy by design", "privacy program governance", "data mapping"],
        "central_forbidden": ["content unrelated to privacy program management"],
        "level_note": "Global privacy program management. Multiple jurisdictions acceptable as examples."
    },
    "cdpse": {
        "name": "Certified Data Privacy Solutions Engineer (ISACA)",
        "description": "ISACA CDPSE. Technical privacy controls and data governance. GDPR, CCPA, LGPD acceptable as regulatory context. Focus on technical privacy implementation.",
        "referenced_ok": ["GDPR as technical requirement", "CCPA as privacy regulation", "LGPD as data protection law", "privacy by design technical", "data governance"],
        "central_forbidden": ["non-privacy technical content", "security-only content with no privacy angle"],
        "level_note": "Technical privacy engineering focus. Multiple privacy laws acceptable."
    },
    "grcp": {
        "name": "Governance Risk Compliance Professional (OCEG)",
        "description": "OCEG GRC capability model. Integrated GRC. SOX, GDPR, ISO 31000, COSO references are LEGITIMATE as GRC covers all major frameworks.",
        "referenced_ok": ["SOX as GRC example", "GDPR as compliance example", "COSO", "ISO 31000", "OCEG GRC model", "integrated GRC"],
        "central_forbidden": ["Brazilian law as primary topic", "country-specific GRC regulation as sole focus"],
        "level_note": "Integrated GRC focus. Major global frameworks all acceptable."
    },
}

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def analyze_block_v2(client, cert_id, questions_block):
    scope = ESCOPO_V2.get(cert_id, {})

    questions_summary = []
    for q in questions_block:
        questions_summary.append({
            "num": q.get("num"),
            "tag": q.get("tag"),
            "text": q.get("text", "")[:300],
            "correct_option": q.get("options", [""])[q.get("correct", 0)][:150] if q.get("options") else "",
            "justification": q.get("justification_correct", "")[:200]
        })

    prompt = f"""You are a senior certification exam quality auditor with deep knowledge of professional certifications.

CERTIFICATION: {scope.get('name', cert_id)}
DESCRIPTION: {scope.get('description', '')}

ACCEPTABLE REFERENCES (these are IN SCOPE even if from other jurisdictions):
{json.dumps(scope.get('referenced_ok', []), ensure_ascii=False)}

TRULY FORBIDDEN (these make a question OUT OF SCOPE):
{json.dumps(scope.get('central_forbidden', []), ensure_ascii=False)}

LEVEL NOTE: {scope.get('level_note', '')}

CRITICAL DISTINCTION:
- A question that MENTIONS GDPR/SOX/HIPAA as an EXAMPLE = IN_SCOPE
- A question where the CENTRAL TOPIC is a forbidden jurisdiction/law = OUT_OF_SCOPE
- A question with TRUNCATED TEXT (ends mid-sentence) = flag as TRUNCATED
- A question at wrong difficulty level = flag as WRONG_LEVEL
- Only flag OUT_OF_SCOPE if you are HIGHLY CONFIDENT the content is wrong for this cert

Questions to evaluate:
{json.dumps(questions_summary, ensure_ascii=False, indent=2)}

Return ONLY a JSON array:
[{{
  "num": 1,
  "status": "IN_SCOPE",
  "issue_type": null,
  "reason": null
}}]

Status values:
- IN_SCOPE: correct content for this certification
- OUT_OF_SCOPE: central topic is clearly wrong for this certification  
- TRUNCATED: question text ends mid-sentence or is clearly incomplete
- WRONG_LEVEL: content is correct domain but wrong difficulty level

Be conservative. When in doubt, mark IN_SCOPE. Only flag real problems."""

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
        return [{"num": q.get("num"), "status": "ERROR", "issue_type": "api_error", "reason": str(e)} for q in questions_block]

def audit_quiz_v2(client, cert_id, domain_id, quiz_file, report_lines):
    try:
        data = load_json(quiz_file)
    except Exception as e:
        report_lines.append(f"  ERRO ao ler {quiz_file}: {e}")
        return 0, 0, 0, 0

    questions = data.get("questions", [])
    lang = data.get("lang", "?")
    if lang != "en":
        return 0, 0, 0, 0

    all_results = {}
    block_size = 10
    for i in range(0, len(questions), block_size):
        block = questions[i:i+block_size]
        results = analyze_block_v2(client, cert_id, block)
        for r in results:
            all_results[r.get("num")] = r

    out_of_scope = []
    truncated    = []
    wrong_level  = []

    for q in questions:
        num = q.get("num")
        r = all_results.get(num, {"status": "UNKNOWN"})
        status = r.get("status", "UNKNOWN")

        if status == "OUT_OF_SCOPE":
            out_of_scope.append((q, r))
        elif status == "TRUNCATED":
            truncated.append((q, r))
        elif status == "WRONG_LEVEL":
            wrong_level.append((q, r))

    total_problems = len(out_of_scope) + len(truncated) + len(wrong_level)
    fname = os.path.basename(quiz_file)

    if total_problems > 0:
        report_lines.append(f"\n  [{cert_id}/{domain_id}/{fname}]")
        report_lines.append(f"  OUT_OF_SCOPE:{len(out_of_scope)} | TRUNCATED:{len(truncated)} | WRONG_LEVEL:{len(wrong_level)}")

        for q, r in out_of_scope:
            report_lines.append(f"    [OUT_OF_SCOPE] Q{q.get('num')} tag:{q.get('tag')}")
            report_lines.append(f"      {r.get('reason','')}")
            report_lines.append(f"      Texto: {q.get('text','')[:100]}...")

        for q, r in truncated:
            report_lines.append(f"    [TRUNCATED] Q{q.get('num')} tag:{q.get('tag')}")
            report_lines.append(f"      Texto: {q.get('text','')[:100]}...")

        for q, r in wrong_level:
            report_lines.append(f"    [WRONG_LEVEL] Q{q.get('num')} tag:{q.get('tag')}")
            report_lines.append(f"      {r.get('reason','')}")

    return len(questions), len(out_of_scope), len(truncated), len(wrong_level)

def main():
    print("=" * 70)
    print("  NEXOR -- AUDITOR DE ESCOPO v2 (criterios calibrados)")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)

    client = anthropic.Anthropic()

    report_lines = [
        f"NEXOR -- AUDITORIA DE ESCOPO v2 -- {TIMESTAMP}",
        "Criterios calibrados -- distingue referencia legitima de tema errado",
        "=" * 70,
        ""
    ]

    totals = {
        "quizzes": 0, "questions": 0,
        "out_of_scope": 0, "truncated": 0, "wrong_level": 0
    }
    cert_summary = {}

    base = Path(QUIZZES_DIR)
    for cert_dir in sorted(base.iterdir()):
        if not cert_dir.is_dir():
            continue
        cert_id = cert_dir.name

        if cert_id not in ESCOPO_V2:
            print(f"\n  [{cert_id}] — sem perfil, pulando")
            continue

        print(f"\n  [{cert_id.upper()}]")
        cert_totals = {"out": 0, "trunc": 0, "level": 0}

        for domain_dir in sorted(cert_dir.iterdir()):
            if not domain_dir.is_dir():
                continue
            domain_id = domain_dir.name

            for quiz_file in sorted(domain_dir.glob("quiz_*_en.json")):
                fname = quiz_file.name
                print(f"    {domain_id}/{fname} ... ", end="", flush=True)

                nq, nout, ntrunc, nlevel = audit_quiz_v2(
                    client, cert_id, domain_id, str(quiz_file), report_lines
                )

                totals["quizzes"]     += 1
                totals["questions"]   += nq
                totals["out_of_scope"] += nout
                totals["truncated"]   += ntrunc
                totals["wrong_level"] += nlevel
                cert_totals["out"]    += nout
                cert_totals["trunc"]  += ntrunc
                cert_totals["level"]  += nlevel

                total = nout + ntrunc + nlevel
                if total == 0:
                    print(f"OK ({nq}q)")
                else:
                    parts = []
                    if nout:   parts.append(f"{nout} OUT_OF_SCOPE")
                    if ntrunc: parts.append(f"{ntrunc} TRUNCATED")
                    if nlevel: parts.append(f"{nlevel} WRONG_LEVEL")
                    print(f"⚠️  {' | '.join(parts)} em {nq}q")

        total_cert = cert_totals["out"] + cert_totals["trunc"] + cert_totals["level"]
        if total_cert > 0:
            cert_summary[cert_id] = cert_totals

    # Resumo
    report_lines += [
        "",
        "=" * 70,
        "RESUMO EXECUTIVO",
        "=" * 70,
        f"Quizzes auditados : {totals['quizzes']}",
        f"Questoes          : {totals['questions']}",
        f"OUT_OF_SCOPE      : {totals['out_of_scope']}",
        f"TRUNCATED         : {totals['truncated']}",
        f"WRONG_LEVEL       : {totals['wrong_level']}",
        f"TOTAL PROBLEMAS   : {totals['out_of_scope'] + totals['truncated'] + totals['wrong_level']}",
        "",
        "POR CERTIFICACAO:",
    ]
    for cert, ct in cert_summary.items():
        report_lines.append(
            f"  {cert}: OUT={ct['out']} TRUNCATED={ct['trunc']} LEVEL={ct['level']}"
        )

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print("\n" + "=" * 70)
    print(f"  CONCLUIDO")
    print(f"  OUT_OF_SCOPE : {totals['out_of_scope']}")
    print(f"  TRUNCATED    : {totals['truncated']}")
    print(f"  WRONG_LEVEL  : {totals['wrong_level']}")
    print(f"  Relatorio    : {REPORT_FILE}")
    print("=" * 70)

if __name__ == "__main__":
    main()
