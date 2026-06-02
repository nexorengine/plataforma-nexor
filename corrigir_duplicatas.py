#!/usr/bin/env python3
"""
NEXOR - CORRETOR DE DUPLICATAS
Detecta questoes duplicadas e regenera substitutas via API.
Mantem o padrao de 50 questoes por quiz.
Execute em: C:\\NEXOR\\nexor_quiz\\
"""

import os, json, re, time
from pathlib import Path
from collections import defaultdict
import anthropic

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
client = anthropic.Anthropic(api_key=API_KEY)
QUIZ_DIR = Path("static/quizzes")

# Catalogo simplificado para contexto de geracao
CONTEXTS = {
    "cfe": {"name": "CFE / ACFE", "domains": {
        "fraud_investigation": "CFE Fraud Examiners Manual 2024 - Fraud Investigation. Topics: planning investigations, interviewing, obtaining evidence, surveillance, investigation reports, legal considerations, digital evidence, chain of custody.",
        "law_cfe": "CFE Fraud Examiners Manual 2024 - Law. Topics: criminal law, civil law, employment law, whistleblower protections, expert witness, SOX, FCPA, Brazil Lei 12.846/2013, LGPD, wire fraud, bank fraud.",
        "law": "CFE Fraud Examiners Manual 2024 - Law. Topics: criminal law, civil law, employment law, whistleblower protections, expert witness, SOX, FCPA.",
        "prevention_deterrence": "CFE Fraud Examiners Manual 2024 - Fraud Prevention and Deterrence. Topics: fraud risk management, COSO framework, corporate governance, ethics programs, fraud risk assessment, internal controls.",
    }},
    "cobit": {"name": "COBIT 2019", "domains": {
        "cobit_framework": "COBIT 2019 ISACA - Framework e principios: 6 principios de governanca, componentes do sistema de governanca, dominios e objetivos de governanca e gestao.",
    }},
    "iso27001_li": {"name": "ISO 27001 Lead Implementer", "domains": {
        "fundamentals_isms": "ISO 27001:2022 Lead Implementer PECB - Fundamentos: conceitos CIA, familia ISO 27000, HLS, PDCA, caso de negocio para SI.",
    }},
    "iso27005": {"name": "ISO 27005 Risk Manager", "domains": {
        "risk_context": "ISO 27005:2022 Risk Manager PECB - Fundamentos: estrutura da ISO 27005, integracao com ISO 27001, conceitos fundamentais de risco, partes interessadas, comunicacao de risco.",
    }},
}

def normaliza(texto):
    return ' '.join(str(texto).lower().strip().split())

def make_prompt_substituta(cert_name, domain_context, quiz_num, questao_num, lang):
    if lang == "pt":
        return f"""Voce e um examinador senior de certificacao profissional para {cert_name}.
Dominio: {domain_context}

Gere EXATAMENTE 1 questao de multipla escolha UNICA E ORIGINAL para o Quiz #{quiz_num}, questao numero {questao_num}.
A questao deve abordar um aspecto DIFERENTE das questoes anteriores do mesmo quiz.

Regras: nivel senior, exatamente 4 alternativas, justificativas tecnicas com referencias normativas. TUDO em PORTUGUES BRASILEIRO.

Retorne APENAS JSON valido, sem markdown:
{{"questions":[{{"num":{questao_num},"text":"QUESTAO","tag":"SUBTOPICO","options":["A. op1","B. op2","C. op3","D. op4"],"correct":0,"justification_correct":"justificativa correta.","justification_wrong":"justificativa erro."}}]}}

correct = indice 0-3."""

    elif lang == "es":
        return f"""Usted es un examinador senior de certificacion profesional para {cert_name}.
Dominio: {domain_context}

Genere EXACTAMENTE 1 pregunta de opcion multiple UNICA Y ORIGINAL para el Quiz #{quiz_num}, pregunta numero {questao_num}.
La pregunta debe abordar un aspecto DIFERENTE de las preguntas anteriores del mismo quiz.

Reglas: nivel senior, exactamente 4 alternativas, justificaciones tecnicas con referencias normativas. TODO en ESPANOL TECNICO.

Retorne SOLO JSON valido, sin markdown:
{{"questions":[{{"num":{questao_num},"text":"PREGUNTA","tag":"SUBTEMA","options":["A. op1","B. op2","C. op3","D. op4"],"correct":0,"justification_correct":"justificacion correcta.","justification_wrong":"justificacion incorrecta."}}]}}

correct = indice 0-3."""

    else:
        return f"""You are a senior certification examiner for {cert_name}.
Domain: {domain_context}

Generate EXACTLY 1 UNIQUE AND ORIGINAL multiple choice question for Quiz #{quiz_num}, question number {questao_num}.
The question must address a DIFFERENT aspect from previous questions in the same quiz.

Rules: senior level, exactly 4 options, technical justifications with normative references. ALL in ENGLISH.

Return ONLY valid JSON, no markdown:
{{"questions":[{{"num":{questao_num},"text":"QUESTION","tag":"SUBTOPIC","options":["A. op1","B. op2","C. op3","D. op4"],"correct":0,"justification_correct":"correct justification.","justification_wrong":"wrong justification."}}]}}

correct = index 0-3."""

def extract_question(raw):
    txt = re.sub(r'```json\s*', '', raw.strip())
    txt = re.sub(r'```\s*', '', txt).strip()
    try:
        data = json.loads(txt)
        if "questions" in data and data["questions"]:
            return data["questions"][0]
    except:
        pass
    decoder = json.JSONDecoder()
    for i in range(len(txt)):
        if txt[i] == '{':
            try:
                obj, _ = decoder.raw_decode(txt, i)
                if "text" in obj:
                    return obj
            except:
                continue
    return None

def corrigir_quiz(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    questions = data.get("questions", [])
    cert_id = data.get("cert_id", "")
    domain_id = data.get("domain_id", "")
    quiz_num = data.get("quiz_num", 1)
    lang = data.get("lang", "pt")

    # Detecta duplicatas
    textos_vistos = {}
    duplicatas = []
    for i, q in enumerate(questions):
        texto = normaliza(q.get("text", ""))
        if texto in textos_vistos:
            duplicatas.append(i)
            print(f"    Duplicata: Q#{q.get('num')} duplica Q#{questions[textos_vistos[texto]].get('num')}")
        else:
            textos_vistos[texto] = i

    if not duplicatas:
        return 0

    # Busca contexto
    cert_info = CONTEXTS.get(cert_id, {})
    cert_name = cert_info.get("name", cert_id)
    domain_context = cert_info.get("domains", {}).get(domain_id, f"{cert_name} - {domain_id}")

    # Regenera cada duplicata
    corrigidas = 0
    for idx in duplicatas:
        q_num = questions[idx].get("num", idx + 1)
        print(f"    Regenerando Q#{q_num} em {lang.upper()}...")

        prompt = make_prompt_substituta(cert_name, domain_context, quiz_num, q_num, lang)
        try:
            msg = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = "".join(b.text for b in msg.content if hasattr(b, "text"))
            nova_q = extract_question(raw)
            if nova_q:
                nova_q["num"] = q_num
                questions[idx] = nova_q
                corrigidas += 1
                print(f"    OK - Q#{q_num} substituida")
            else:
                print(f"    ERRO - nao foi possivel parsear a resposta")
        except Exception as e:
            print(f"    ERRO - {e}")
        time.sleep(0.5)

    if corrigidas > 0:
        data["questions"] = questions
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    return corrigidas

def main():
    print("=" * 60)
    print("  NEXOR - CORRETOR DE DUPLICATAS")
    print("=" * 60)

    # Lista de arquivos com duplicatas conhecidas
    alvos = [
        "cfe/fraud_investigation/quiz_001_en.json",
        "cfe/law/quiz_001_en.json",
        "cfe/law_cfe/quiz_001_en.json",
        "cfe/prevention_deterrence/quiz_001_en.json",
        "cobit/cobit_framework/quiz_001_es.json",
        "iso27001_li/fundamentals_isms/quiz_001_en.json",
        "iso27005/risk_context/quiz_001_pt.json",
        "iso27001_li/fundamentals_isms/quiz_003_es.json",
    ]

    total_corrigidas = 0
    for alvo in alvos:
        path = QUIZ_DIR / alvo
        if not path.exists():
            print(f"\nNAO ENCONTRADO: {alvo}")
            continue
        print(f"\nProcessando: {alvo}")
        n = corrigir_quiz(path)
        total_corrigidas += n

    print("\n" + "=" * 60)
    print(f"  CORRECAO CONCLUIDA!")
    print(f"  Total de questoes substituidas: {total_corrigidas}")
    print("=" * 60)

if __name__ == "__main__":
    main()
