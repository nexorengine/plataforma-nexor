#!/usr/bin/env python3
"""
NEXOR - TRADUTOR CISM PENDENTES
Traduz os 3 quizzes CISM completos para EN e ES.
Ignora o quiz_004 incompleto (5q).
Execute em: C:\\NEXOR\\nexor_quiz\\
"""
import os, json, re, time
from pathlib import Path
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY",""))
QUIZ_DIR = Path("static/quizzes")

ALVOS = [
    "cism/incident_management/quiz_001_pt.json",
    "cism/info_risk_management/quiz_001_pt.json",
    "cism/info_security_governance/quiz_003_pt.json",
]

def extract_questions(raw):
    txt = re.sub(r'```json\s*','',raw.strip())
    txt = re.sub(r'```\s*','',txt).strip()
    try:
        d = json.loads(txt)
        if "questions" in d: return d["questions"]
        if isinstance(d, list): return d
    except: pass
    match = re.search(r'\[.*\]', txt, re.DOTALL)
    if match:
        try: return json.loads(match.group())
        except: pass
    return None

def traduz_batch(questions, lang, cert_name):
    lang_label = "American English" if lang == "en" else "Latin American Spanish"
    lang_instr = "ALL in fluent technical English" if lang == "en" else "TODO en español técnico"

    q_min = []
    for q in questions:
        q_min.append({
            "num": q.get("num"),
            "text": q.get("text","")[:350],
            "tag": q.get("tag",""),
            "options": [o[:120] for o in q.get("options",[])],
            "correct": q.get("correct",0),
            "justification_correct": q.get("justification_correct","")[:180],
            "justification_wrong": q.get("justification_wrong","")[:120]
        })

    prompt = f"""Translate {len(questions)} exam questions for {cert_name} from Portuguese to {lang_label}.
{lang_instr}. Keep correct index unchanged. Keep question numbers. Translate tags and options (keep A. B. C. D. prefix).
Return ONLY JSON: {{"questions":[...]}}

{json.dumps(q_min, ensure_ascii=False)}"""

    try:
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2500,
            messages=[{"role":"user","content":prompt}]
        )
        raw = "".join(b.text for b in msg.content if hasattr(b,"text"))
        return extract_questions(raw)
    except Exception as e:
        print(f"ERRO: {e}")
        return None

def traduz_quiz(path_pt, lang):
    path_out = Path(str(path_pt).replace("_pt.json", f"_{lang}.json"))
    if path_out.exists():
        return "ja_existe"

    data = json.loads(path_pt.read_text(encoding="utf-8"))
    questions = data.get("questions", [])
    cert_name = data.get("cert_name", "")
    if not questions: return "vazio"

    todas = []
    bs = 5
    n_batches = (len(questions) + bs - 1) // bs

    for i in range(0, len(questions), bs):
        batch = questions[i:i+bs]
        bn = i//bs + 1
        print(f"    B{bn}/{n_batches}...", end=" ", flush=True)

        result = traduz_batch(batch, lang, cert_name)
        if result and len(result) >= len(batch) - 1:
            todas.extend(result[:len(batch)])
            print("OK")
        else:
            time.sleep(3)
            print("retry...", end=" ", flush=True)
            result = traduz_batch(batch, lang, cert_name)
            if result and len(result) > 0:
                todas.extend(result[:len(batch)])
                print(f"OK({len(result)})")
            else:
                todas.extend(batch)  # fallback: mantém PT
                print("fallback PT")
        time.sleep(1.5)

    for i, q in enumerate(todas):
        if i < len(questions):
            q["num"] = questions[i].get("num", i+1)

    data_out = dict(data)
    data_out["lang"] = lang
    data_out["questions"] = todas
    path_out.write_text(json.dumps(data_out, ensure_ascii=False, indent=2), encoding="utf-8")
    return "ok"

print("=" * 60)
print("  TRADUTOR CISM — 3 quizzes × EN + ES")
print("=" * 60)

ok_en = ok_es = 0

for alvo in ALVOS:
    path_pt = QUIZ_DIR / alvo
    if not path_pt.exists():
        print(f"\nNAO ENCONTRADO: {alvo}")
        continue

    data = json.loads(path_pt.read_text(encoding="utf-8"))
    label = f"{data.get('cert_id','?')}/{data.get('domain_id','?')}/quiz_{data.get('quiz_num','?'):03d}"
    n = len(data.get("questions",[]))
    print(f"\n📁 {label} ({n}q)")

    for lang in ["en","es"]:
        path_out = Path(str(path_pt).replace("_pt.json",f"_{lang}.json"))
        if path_out.exists():
            print(f"  [{lang.upper()}] Ja existe")
            continue
        print(f"  [{lang.upper()}] Traduzindo (batches de 5)...")
        r = traduz_quiz(path_pt, lang)
        if r == "ok":
            if lang=="en": ok_en+=1
            else: ok_es+=1
            print(f"  [{lang.upper()}] ✅ Salvo")
        else:
            print(f"  [{lang.upper()}] Resultado: {r}")
        time.sleep(1)

print(f"\n{'='*60}")
print(f"  CONCLUIDO! EN:{ok_en} ES:{ok_es}")
print(f"{'='*60}")
