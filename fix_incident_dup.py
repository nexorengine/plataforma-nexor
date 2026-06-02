#!/usr/bin/env python3
import os, json, re, time
from pathlib import Path
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY",""))
path = Path("static/quizzes/cism/incident_management/quiz_001_pt.json")

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
    ctx = "CISM Incident Management - tipos de teste de plano de resposta a incidentes (revisao de documentos, walkthrough, simulacao), dwell time, privilegio advogado-cliente, cadeia de custodia, BCP, RTO, RPO, hot/warm/cold site, SIEM, forense digital, ransomware, seguro cibernetico, comunicacao de incidentes, lições aprendidas."
    for idx in duplicatas:
        q_num = questions[idx].get("num", idx+1)
        print(f"Regenerando Q#{q_num}...")
        prompt = f"""Voce e examinador senior CISM. Contexto: {ctx}
Gere 1 questao UNICA numero {q_num} sobre um topico DIFERENTE das anteriores. PORTUGUES BRASILEIRO.
Retorne APENAS JSON: {{"questions":[{{"num":{q_num},"text":"Q","tag":"T","options":["A. a","B. b","C. c","D. d"],"correct":0,"justification_correct":"j.","justification_wrong":"j."}}]}}"""
        msg = client.messages.create(model="claude-haiku-4-5-20251001",max_tokens=1000,
                                      messages=[{"role":"user","content":prompt}])
        raw = "".join(b.text for b in msg.content if hasattr(b,"text"))
        nova = extract_question(raw)
        if nova:
            nova["num"] = q_num
            questions[idx] = nova
            print(f"OK - Q#{q_num} substituída")
        else:
            print(f"ERRO - Q#{q_num}")
    data["questions"] = questions
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Salvo.")
