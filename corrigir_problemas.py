"""
corrigir_problemas.py
Corrige automaticamente os 25 problemas encontrados pelo verificar_duplicatas v2:
  - 2 alternativas duplicadas (corrige via API)
  - 23 questoes sem justificativa (preenche via API)

Uso:
    cd C:\\NEXOR\\nexor_quiz
    python corrigir_problemas.py
"""

import json, re, os, time, hashlib
from pathlib import Path
from collections import defaultdict
import anthropic

QUIZ_DIR = Path("static/quizzes")
client   = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

def norm_alt(s):
    return re.sub(r'^[A-Da-d]\.\s*', '', s).strip().lower()

def chamar_api(prompt):
    resp = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = resp.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"): raw = raw[4:]
    return raw.strip()

# ── 1. CORRIGE ALTERNATIVAS DUPLICADAS ───────────────────────────────────────
def corrigir_alt_duplicada(arq, q, idx_dup):
    """Pede a API para gerar uma alternativa substituta unica."""
    lang = json.loads(arq.read_text(encoding="utf-8")).get("lang", "pt")
    lang_label = {"pt":"PORTUGUES BRASILEIRO","en":"INGLES TECNICO","es":"ESPANHOL TECNICO"}.get(lang,"PORTUGUES BRASILEIRO")

    prompt = f"""Voce e especialista em certificacoes de seguranca da informacao.

A questao abaixo tem a alternativa {idx_dup+1} (indice {idx_dup}) IDENTICA a outra alternativa.
Gere uma nova alternativa UNICA e PLAUSIVEL para substituir a duplicada, mantendo o mesmo nivel de dificuldade e idioma ({lang_label}).

QUESTAO:
{json.dumps(q, ensure_ascii=False, indent=2)}

Alternativa duplicada (indice {idx_dup}): "{q['options'][idx_dup]}"

Retorne APENAS um JSON com este formato exato, sem markdown:
{{"nova_alternativa": "X. texto da nova alternativa aqui"}}

Onde X e a letra correspondente ao indice {idx_dup} (A=0, B=1, C=2, D=3).
A nova alternativa NAO pode ser correta (correct={q['correct']}).
"""
    raw = chamar_api(prompt)
    resultado = json.loads(raw)
    return resultado["nova_alternativa"]

# ── 2. CORRIGE JUSTIFICATIVAS AUSENTES ───────────────────────────────────────
def corrigir_justificativa(arq, data, q):
    lang = data.get("lang","pt")
    cert = data.get("cert_name","")
    domain = data.get("domain_name","")
    lang_label = {"pt":"PORTUGUES BRASILEIRO","en":"INGLES TECNICO","es":"ESPANHOL TECNICO"}.get(lang,"PORTUGUES BRASILEIRO")

    jc = q.get("justification_correct","").strip()
    jw = q.get("justification_wrong","").strip()

    faltam = []
    if not jc: faltam.append("justification_correct")
    if not jw: faltam.append("justification_wrong")

    prompt = f"""Voce e especialista em certificacoes de seguranca da informacao ({cert} — {domain}).

A questao abaixo esta faltando: {', '.join(faltam)}.

QUESTAO COMPLETA:
{json.dumps(q, ensure_ascii=False, indent=2)}

Gere as justificativas faltantes em {lang_label}, com referencias normativas quando aplicavel.

Retorne APENAS um JSON com os campos faltantes, sem markdown:
{json.dumps({f: "justificativa aqui" for f in faltam}, ensure_ascii=False)}
"""
    raw = chamar_api(prompt)
    return json.loads(raw)

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  NEXOR — CORRETOR AUTOMATICO DE PROBLEMAS")
    print("=" * 60)

    arquivos = sorted(QUIZ_DIR.rglob("quiz_*.json"))
    total_alt  = 0
    total_just = 0
    total_arq  = 0

    for arq in arquivos:
        try:
            data = json.loads(arq.read_text(encoding="utf-8"))
        except:
            continue

        modificado = False
        questoes   = data.get("questions", [])

        for i, q in enumerate(questoes):
            num  = q.get("num","?")
            opts = q.get("options", [])

            # ── Alternativas duplicadas ───────────────────────────────────
            vistos = {}
            for j, op in enumerate(opts):
                chave = norm_alt(op)
                if chave in vistos:
                    print(f"\n  [ALT-DUP] {arq.name} Q{num} — alternativa {j+1} duplicada")
                    print(f"           Gerando substituta via API...")
                    try:
                        nova = corrigir_alt_duplicada(arq, q, j)
                        print(f"           Nova: {nova}")
                        questoes[i]["options"][j] = nova
                        modificado = True
                        total_alt += 1
                    except Exception as e:
                        print(f"           ERRO: {e}")
                    time.sleep(2)
                else:
                    vistos[chave] = j

            # ── Justificativas ausentes ───────────────────────────────────
            jc = q.get("justification_correct","").strip()
            jw = q.get("justification_wrong","").strip()
            if not jc or not jw:
                print(f"\n  [SEM-JUST] {arq.name} Q{num} — preenchendo via API...")
                try:
                    resultado = corrigir_justificativa(arq, data, q)
                    for campo, valor in resultado.items():
                        questoes[i][campo] = valor
                        print(f"           {campo}: OK")
                    modificado = True
                    total_just += 1
                except Exception as e:
                    print(f"           ERRO: {e}")
                time.sleep(2)

        if modificado:
            data["questions"] = questoes
            arq.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"\n  SALVO: {arq}")
            total_arq += 1

    print("\n" + "=" * 60)
    print(f"  CONCLUIDO!")
    print(f"  Alternativas corrigidas  : {total_alt}")
    print(f"  Justificativas geradas   : {total_just}")
    print(f"  Arquivos modificados     : {total_arq}")
    print("=" * 60)

if __name__ == "__main__":
    main()
