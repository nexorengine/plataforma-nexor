#!/usr/bin/env python3
import os, json, re, time
from pathlib import Path
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY",""))
path = Path("static/quizzes/iso27001_li/fundamentals_isms/quiz_004_pt.json")

def normaliza(t):
    return ' '.join(str(t).lower().strip().split())

def extract_question(raw):
    txt = re.sub(r'```json\s*','',raw.strip())
    txt = re.sub(r'```\s*','',txt).strip()
    try:
        d = json.loads(txt)
        if "questions" in d and d["questions"]: return d["questions"][0]
    except: pass
    dec = json.JSONDecoder()
    for i in range(len(txt)):
        if txt[i]=='{':
            try:
                obj,_ = dec.raw_decode(txt,i)
                if "text" in obj: return obj
            except: continue
    return None

data = json.loads(path.read_text(encoding="utf-8"))
questions = data.get("questions",[])

textos = {}
duplicatas = []
for i,q in enumerate(questions):
    t = normaliza(q.get("text",""))
    if t in textos:
        duplicatas.append(i)
        print(f"Duplicata: Q#{q.get('num')} duplica Q#{questions[textos[t]].get('num')}")
    else:
        textos[t] = i

if not duplicatas:
    print("Nenhuma duplicata encontrada.")
else:
    ctx = "ISO 27001:2022 Fundamentos do SGSI: conceitos CIA, familia ISO 27000, estrutura HLS, ciclo PDCA, caso de negocio para seguranca da informacao, escopo do SGSI, partes interessadas, requisitos de lideranca, politica de seguranca, objetivos de seguranca, gestao de riscos basica."
    for idx in duplicatas:
        q_num = questions[idx].get("num", idx+1)
        print(f"Regenerando Q#{q_num}...")
        prompt = f"""Voce e um examinador senior de ISO 27001 Lead Implementer PECB.
Contexto: {ctx}
Gere EXATAMENTE 1 questao UNICA E ORIGINAL numero {q_num} para o Quiz #4 de Fundamentos do SGSI.
A questao deve abordar aspecto DIFERENTE das anteriores. Nivel fundamentos, 4 alternativas, justificativas com referencias normativas. PORTUGUES BRASILEIRO.
Retorne APENAS JSON valido:
{{"questions":[{{"num":{q_num},"text":"QUESTAO","tag":"SUBTOPICO","options":["A. op1","B. op2","C. op3","D. op4"],"correct":0,"justification_correct":"justificativa.","justification_wrong":"justificativa."}}]}}"""
        msg = client.messages.create(model="claude-haiku-4-5-20251001",max_tokens=1000,messages=[{"role":"user","content":prompt}])
        raw = "".join(b.text for b in msg.content if hasattr(b,"text"))
        nova = extract_question(raw)
        if nova:
            nova["num"] = q_num
            questions[idx] = nova
            print(f"OK - Q#{q_num} substituida")
        else:
            print(f"ERRO - Q#{q_num} nao regenerada")
    data["questions"] = questions
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    print("Arquivo salvo.")
print("Concluido.")
