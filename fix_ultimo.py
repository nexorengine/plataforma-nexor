#!/usr/bin/env python3
import os, json, re, time
from pathlib import Path
import anthropic

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
client = anthropic.Anthropic(api_key=API_KEY)

path = Path("static/quizzes/iso27001_li/fundamentals_isms/quiz_003_es.json")

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

data = json.loads(path.read_text(encoding="utf-8"))
questions = data.get("questions", [])

# Detecta duplicatas
textos_vistos = {}
duplicatas = []
for i, q in enumerate(questions):
    texto = normaliza(q.get("text", ""))
    if texto in textos_vistos:
        duplicatas.append(i)
        print(f"Duplicata: Q#{q.get('num')} duplica Q#{questions[textos_vistos[texto]].get('num')}")
    else:
        textos_vistos[texto] = i

if not duplicatas:
    print("Nenhuma duplicata encontrada.")
else:
    domain_context = "ISO 27001:2022 Lead Implementer PECB - Fundamentos: conceptos CIA, familia ISO 27000, HLS, PDCA, caso de negocio para SI, alcance del SGSI, partes interesadas, requisitos de liderazgo."
    
    for idx in duplicatas:
        q_num = questions[idx].get("num", idx + 1)
        print(f"Regenerando Q#{q_num} em ES...")
        
        prompt = f"""Usted es un examinador senior de certificacion profesional para ISO 27001 Lead Implementer.
Dominio: {domain_context}

Genere EXACTAMENTE 1 pregunta de opcion multiple UNICA Y ORIGINAL para el Quiz #3, pregunta numero {q_num}.
La pregunta debe abordar un aspecto DIFERENTE de las preguntas anteriores del mismo quiz.

Reglas: nivel senior, exactamente 4 alternativas, justificaciones tecnicas con referencias normativas. TODO en ESPANOL TECNICO.

Retorne SOLO JSON valido, sin markdown:
{{"questions":[{{"num":{q_num},"text":"PREGUNTA","tag":"SUBTEMA","options":["A. op1","B. op2","C. op3","D. op4"],"correct":0,"justification_correct":"justificacion correcta.","justification_wrong":"justificacion incorrecta."}}]}}

correct = indice 0-3."""

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
            print(f"OK - Q#{q_num} substituida")
        else:
            print(f"ERRO - nao foi possivel parsear")

    data["questions"] = questions
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Arquivo salvo.")

print("Concluido.")
