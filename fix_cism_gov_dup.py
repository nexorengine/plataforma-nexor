#!/usr/bin/env python3
"""
Fix duplicidades no cism/info_security_governance/quiz_003 (PT, EN, ES)
Execute em: C:\\NEXOR\\nexor_quiz\\
"""
import os, json, re, time
from pathlib import Path
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY",""))
QUIZ_DIR = Path("static/quizzes")

context = "CISM Information Security Governance - governance frameworks, risk decisions, security strategy, metrics, KPIs, BMIS, balanced scorecard, control frameworks, security policies, executive reporting, cybersecurity steering committee, CISO roles."

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

def regenera(q_num, lang, quiz_num):
    if lang == "pt":
        prompt = f"""Voce e examinador senior CISM. Contexto: {context}
Gere 1 questao UNICA numero {q_num} para Quiz #{quiz_num} em PORTUGUES BRASILEIRO.
Retorne APENAS JSON: {{"questions":[{{"num":{q_num},"text":"Q","tag":"T","options":["A. a","B. b","C. c","D. d"],"correct":0,"justification_correct":"j.","justification_wrong":"j."}}]}}"""
    elif lang == "en":
        prompt = f"""You are a senior CISM examiner. Context: {context}
Generate 1 UNIQUE question number {q_num} for Quiz #{quiz_num} in ENGLISH.
Return ONLY JSON: {{"questions":[{{"num":{q_num},"text":"Q","tag":"T","options":["A. a","B. b","C. c","D. d"],"correct":0,"justification_correct":"j.","justification_wrong":"j."}}]}}"""
    else:
        prompt = f"""Usted es examinador senior CISM. Contexto: {context}
Genere 1 pregunta UNICA numero {q_num} para Quiz #{quiz_num} en ESPAÑOL.
Retorne SOLO JSON: {{"questions":[{{"num":{q_num},"text":"P","tag":"T","options":["A. a","B. b","C. c","D. d"],"correct":0,"justification_correct":"j.","justification_wrong":"j."}}]}}"""

    msg = client.messages.create(model="claude-haiku-4-5-20251001", max_tokens=1000,
                                  messages=[{"role":"user","content":prompt}])
    raw = "".join(b.text for b in msg.content if hasattr(b,"text"))
    return extract_question(raw)

def fix_quiz(path, ref_path, lang):
    """Corrige duplicatas em path comparando com ref_path."""
    if not path.exists() or not ref_path.exists():
        print(f"  Arquivo nao encontrado: {path.name}")
        return 0

    data = json.loads(path.read_text(encoding="utf-8"))
    data_ref = json.loads(ref_path.read_text(encoding="utf-8"))

    textos_ref = {normaliza(q.get("text","")) for q in data_ref.get("questions",[])}
    questions = data.get("questions",[])
    quiz_num = data.get("quiz_num", 3)
    corrigidas = 0

    for i, q in enumerate(questions):
        if normaliza(q.get("text","")) in textos_ref:
            q_num = q.get("num", i+1)
            print(f"  [{lang.upper()}] Q#{q_num} duplicada — regenerando...")
            nova = regenera(q_num, lang, quiz_num)
            if nova:
                nova["num"] = q_num
                questions[i] = nova
                corrigidas += 1
                print(f"  [{lang.upper()}] Q#{q_num} substituída ✅")
            else:
                print(f"  [{lang.upper()}] Q#{q_num} falhou ❌")
            time.sleep(0.5)

    if corrigidas > 0:
        data["questions"] = questions
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    return corrigidas

print("=" * 55)
print("  FIX DUPLICIDADES — cism/info_security_governance/quiz_003")
print("=" * 55)

base = QUIZ_DIR / "cism/info_security_governance"
total = 0

for lang in ["pt", "en", "es"]:
    quiz3 = base / f"quiz_003_{lang}.json"
    quiz2 = base / f"quiz_002_{lang}.json"
    print(f"\n[{lang.upper()}] Verificando quiz_003 vs quiz_002...")
    n = fix_quiz(quiz3, quiz2, lang)
    total += n
    if n == 0:
        print(f"  Nenhuma duplicata encontrada em {lang.upper()}")

print(f"\n{'='*55}")
print(f"  CONCLUIDO! {total} questao(es) corrigida(s)")
print(f"{'='*55}")
