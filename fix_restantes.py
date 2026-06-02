#!/usr/bin/env python3
import os, json, re, time
from pathlib import Path
import anthropic

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
client = anthropic.Anthropic(api_key=API_KEY)
QUIZ_DIR = Path("static/quizzes")

def normaliza(texto):
    return ' '.join(str(texto).lower().strip().split())

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

def regenera(path, q_num, cert_name, domain_context, lang, quiz_num):
    print(f"  Regenerando Q#{q_num} em {lang.upper()} em {path.name}...")
    
    if lang == "pt":
        prompt = f"""Voce e um examinador senior para {cert_name}.
Dominio: {domain_context}
Gere EXATAMENTE 1 questao UNICA E ORIGINAL numero {q_num} para Quiz #{quiz_num}.
Aborde aspecto DIFERENTE das questoes anteriores. Nivel senior, 4 alternativas, justificativas normativas. PORTUGUES BRASILEIRO.
Retorne APENAS JSON: {{"questions":[{{"num":{q_num},"text":"Q","tag":"T","options":["A. a","B. b","C. c","D. d"],"correct":0,"justification_correct":"j.","justification_wrong":"j."}}]}}"""
    elif lang == "es":
        prompt = f"""Usted es examinador senior para {cert_name}.
Dominio: {domain_context}
Genere EXACTAMENTE 1 pregunta UNICA Y ORIGINAL numero {q_num} para Quiz #{quiz_num}.
Aborde aspecto DIFERENTE de las anteriores. Nivel senior, 4 alternativas, justificaciones normativas. ESPANOL TECNICO.
Retorne SOLO JSON: {{"questions":[{{"num":{q_num},"text":"P","tag":"T","options":["A. a","B. b","C. c","D. d"],"correct":0,"justification_correct":"j.","justification_wrong":"j."}}]}}"""
    else:
        prompt = f"""You are a senior examiner for {cert_name}.
Domain: {domain_context}
Generate EXACTLY 1 UNIQUE ORIGINAL question number {q_num} for Quiz #{quiz_num}.
Address a DIFFERENT aspect. Senior level, 4 options, normative justifications. ENGLISH.
Return ONLY JSON: {{"questions":[{{"num":{q_num},"text":"Q","tag":"T","options":["A. a","B. b","C. c","D. d"],"correct":0,"justification_correct":"j.","justification_wrong":"j."}}]}}"""

    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = "".join(b.text for b in msg.content if hasattr(b, "text"))
    return extract_question(raw)

def fix_interno(path, cert_name, domain_context):
    """Corrige duplicatas internas num quiz."""
    data = json.loads(path.read_text(encoding="utf-8"))
    questions = data.get("questions", [])
    lang = data.get("lang", "pt")
    quiz_num = data.get("quiz_num", 1)
    
    textos_vistos = {}
    corrigidas = 0
    for i, q in enumerate(questions):
        texto = normaliza(q.get("text", ""))
        if texto in textos_vistos:
            q_num = q.get("num", i+1)
            nova = regenera(path, q_num, cert_name, domain_context, lang, quiz_num)
            if nova:
                nova["num"] = q_num
                questions[i] = nova
                corrigidas += 1
                print(f"  OK - Q#{q_num} substituida")
            else:
                print(f"  ERRO - Q#{q_num} nao regenerada")
        else:
            textos_vistos[texto] = i
    
    if corrigidas > 0:
        data["questions"] = questions
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return corrigidas

def fix_entre_quizzes(path_novo, path_ref, cert_name, domain_context):
    """Corrige questoes de path_novo que existem em path_ref."""
    data_ref = json.loads(path_ref.read_text(encoding="utf-8"))
    data_novo = json.loads(path_novo.read_text(encoding="utf-8"))
    
    textos_ref = {normaliza(q.get("text","")) for q in data_ref.get("questions",[])}
    questions = data_novo.get("questions", [])
    lang = data_novo.get("lang", "pt")
    quiz_num = data_novo.get("quiz_num", 1)
    
    corrigidas = 0
    for i, q in enumerate(questions):
        if normaliza(q.get("text","")) in textos_ref:
            q_num = q.get("num", i+1)
            print(f"  Q#{q_num} duplica questao do quiz anterior")
            nova = regenera(path_novo, q_num, cert_name, domain_context, lang, quiz_num)
            if nova:
                nova["num"] = q_num
                questions[i] = nova
                corrigidas += 1
                print(f"  OK - Q#{q_num} substituida")
    
    if corrigidas > 0:
        data_novo["questions"] = questions
        path_novo.write_text(json.dumps(data_novo, ensure_ascii=False, indent=2), encoding="utf-8")
    return corrigidas

print("=" * 60)
print("  NEXOR - FIX DUPLICATAS RESTANTES")
print("=" * 60)

total = 0

# CASO 1: iso27001_li/fundamentals_isms quiz_003_es duplica quiz_002_es
print("\n[1/2] iso27001_li/fundamentals_isms - quiz_003_es vs quiz_002_es")
p3 = QUIZ_DIR / "iso27001_li/fundamentals_isms/quiz_003_es.json"
p2 = QUIZ_DIR / "iso27001_li/fundamentals_isms/quiz_002_es.json"
if p3.exists() and p2.exists():
    n = fix_entre_quizzes(p3, p2,
        "ISO 27001 Lead Implementer",
        "ISO 27001:2022 Lead Implementer PECB - Fundamentos: conceptos CIA, familia ISO 27000, HLS, PDCA, caso de negocio para SI, alcance del SGSI, partes interesadas, liderazgo, politica de SI.")
    total += n
else:
    print("  Arquivo nao encontrado")

# CASO 2: iso27701_li/pims_fundamentals quiz_001_es duplicata interna
print("\n[2/2] iso27701_li/pims_fundamentals - quiz_001_es duplicata interna")
p = QUIZ_DIR / "iso27701_li/pims_fundamentals/quiz_001_es.json"
if p.exists():
    n = fix_interno(p,
        "ISO 27701 Lead Implementer",
        "ISO 27701:2019 Lead Implementer PECB - Fundamentos de PIMS: extension de privacidad de ISO 27001, conceptos de PIMS, papel de Controlador vs Operador, integracion con ISO 27001 e ISO 27002, ciclo de vida de datos personales.")
    total += n
else:
    print("  Arquivo nao encontrado")

print(f"\n{'='*60}")
print(f"  CONCLUIDO! {total} questao(es) substituida(s)")
print(f"{'='*60}")
