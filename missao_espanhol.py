#!/usr/bin/env python3
"""
NEXOR — Missão Espanhol
Detecta todos os quizzes com PT+EN mas sem ES e gera o ES automaticamente.
Execute em: C:\NEXOR\nexor_quiz\
"""

import os, json, re, time, random
from pathlib import Path
import anthropic

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
client = anthropic.Anthropic(api_key=API_KEY)
QUIZ_DIR = Path("static/quizzes")

BATCHES = [
    (1,  5,  "fundamental"),
    (6,  10, "fundamental-intermediate"),
    (11, 15, "intermediate"),
    (16, 20, "intermediate-advanced"),
    (21, 25, "advanced"),
    (26, 30, "advanced-applied"),
    (31, 35, "applied"),
    (36, 40, "applied-expert"),
    (41, 45, "expert"),
    (46, 50, "expert-synthesis"),
]

def make_prompt_es(cert_name, domain_context, quiz_num, start, end, fase):
    count = end - start + 1
    return f"""Usted es un examinador senior de certificacion profesional para {cert_name}.
Dominio: {domain_context}

Genere exactamente {count} preguntas de opcion multiple (P{start} a P{end}) para el Quiz #{quiz_num}. Enfoque: topicos {fase}.

Reglas: nivel senior de certificacion, exactamente 4 alternativas por pregunta, justificaciones tecnicas con referencias normativas precisas. TODO en ESPANOL TECNICO.

Retorne SOLO JSON valido, sin markdown. Justificaciones max 80 palabras:
{{"questions":[{{"num":{start},"text":"PREGUNTA","tag":"SUBTEMA","options":["A. op1","B. op2","C. op3","D. op4"],"correct":0,"justification_correct":"justificacion correcta.","justification_wrong":"justificacion incorrecta."}}]}}

Genere exactamente {count} preguntas de {start} a {end}. correct = indice 0-3."""

def extract_questions(raw):
    txt = re.sub(r'```json\s*', '', raw.strip())
    txt = re.sub(r'```\s*', '', txt).strip()
    try:
        data = json.loads(txt)
        if "questions" in data:
            return data["questions"]
    except:
        pass
    start_idx = txt.find('[')
    if start_idx != -1:
        depth = 0
        for i in range(start_idx, len(txt)):
            if txt[i] == '[': depth += 1
            elif txt[i] == ']':
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(txt[start_idx:i+1])
                    except:
                        break
    decoder = json.JSONDecoder()
    for i in range(len(txt)):
        if txt[i] == '{':
            try:
                obj, _ = decoder.raw_decode(txt, i)
                if "questions" in obj:
                    return obj["questions"]
            except:
                continue
    raise ValueError(f"Nao foi possivel parsear. Amostra: {repr(txt[:200])}")

def shuffle_options(questions):
    for q in questions:
        if 'options' not in q or 'correct' not in q:
            continue
        correct_text = q['options'][q['correct']]
        indices = list(range(len(q['options'])))
        random.shuffle(indices)
        q['options'] = [q['options'][i] for i in indices]
        q['correct'] = q['options'].index(correct_text)
    return questions

def gerar_es(pt_path):
    """Gera o arquivo ES baseado nos metadados do arquivo PT."""
    data_pt = json.loads(pt_path.read_text(encoding="utf-8"))
    cert_name = data_pt.get("cert_name", "Certificacao")
    domain_name = data_pt.get("domain_name", "Dominio")
    cert_id = data_pt.get("cert_id", "")
    domain_id = data_pt.get("domain_id", "")
    quiz_num = data_pt.get("quiz_num", 1)

    # Tenta recuperar context do server.py
    domain_context = f"{cert_name} — {domain_name}"

    es_path = pt_path.parent / pt_path.name.replace("_pt.json", "_es.json")

    print(f"\n  📋 Cert: {cert_name} | Domínio: {domain_name} | Quiz #{quiz_num}")
    print(f"  🎯 Gerando ES em {es_path.name}...")

    all_q = []
    for start, end, fase in BATCHES:
        print(f"     Batch {start}-{end} [{fase}]...", end=" ", flush=True)
        prompt = make_prompt_es(cert_name, domain_context, quiz_num, start, end, fase)
        try:
            msg = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=8192,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = "".join(b.text for b in msg.content if hasattr(b, "text"))
            qs = extract_questions(raw)
            qs = shuffle_options(qs)
            all_q.extend(qs)
            print(f"✅ {len(qs)} questões")
        except Exception as e:
            print(f"❌ Erro: {e}")
            continue
        time.sleep(0.5)

    data_es = {
        "cert_id": cert_id,
        "domain_id": domain_id,
        "quiz_num": quiz_num,
        "domain_name": domain_name,
        "cert_name": cert_name,
        "lang": "es",
        "questions": all_q
    }
    es_path.write_text(json.dumps(data_es, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  💾 Salvo: {len(all_q)} questões em ES")
    return len(all_q)

def main():
    print("=" * 60)
    print("  NEXOR — MISSÃO ESPANHOL")
    print("  Completando o acervo com versões ES")
    print("=" * 60)

    pt_files = sorted(QUIZ_DIR.rglob("*_pt.json"))
    pendentes = []

    for pt in pt_files:
        es = pt.parent / pt.name.replace("_pt.json", "_es.json")
        if not es.exists():
            pendentes.append(pt)

    if not pendentes:
        print("\n✅ Todos os quizzes já têm versão ES. Missão cumprida!")
        return

    print(f"\n🔍 Encontrados {len(pendentes)} quiz(zes) sem versão ES:\n")
    for p in pendentes:
        print(f"   • {p.parent.parent.name}/{p.parent.name}/{p.name}")

    print(f"\n🚀 Iniciando geração ES para {len(pendentes)} quiz(zes)...")
    print(f"   Estimativa: ~{len(pendentes) * 6} minutos\n")

    total_gerado = 0
    for i, pt in enumerate(pendentes, 1):
        print(f"\n[{i}/{len(pendentes)}] Processando...")
        try:
            qtd = gerar_es(pt)
            total_gerado += qtd
        except Exception as e:
            print(f"  ❌ Erro fatal neste quiz: {e}")
            continue

    print("\n" + "=" * 60)
    print(f"  ✅ MISSÃO CONCLUÍDA!")
    print(f"  📊 Total gerado: {total_gerado} questões em ES")
    print(f"  🌎 Acervo agora trilíngue: PT + EN + ES")
    print("=" * 60)

if __name__ == "__main__":
    main()
