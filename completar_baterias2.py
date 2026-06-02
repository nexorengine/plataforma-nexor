#!/usr/bin/env python3
"""
NEXOR - COMPLETADOR DE BATERIAS v2
Completa os 6 quizzes restantes.
Execute em: C:\\NEXOR\\nexor_quiz\\
"""
import os, json, re, time
from pathlib import Path
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY",""))
QUIZ_DIR = Path("static/quizzes")

CONTEXTS = {
    "cfe/financial_transactions": {
        "cert": "CFE / ACFE",
        "domain": "Financial Transactions & Fraud Schemes",
        "context": "CFE Fraud Examiners Manual 2024 - Financial Transactions and Fraud Schemes: skimming, cash larceny, lapping, kiting, channel stuffing, funcionario fantasma, management override, adulteracao de cheques, capitalizacao indevida, cookie jar reserves, shell vendor scheme, reconhecimento indevido de receitas, manipulacao de estoques, transacoes com partes relacionadas, fraude em demonstracoes financeiras, casos reais (Enron, WorldCom, Tyco, Madoff, Satyam, HealthSouth, Olympus, Toshiba, Siemens, Wells Fargo), equacao contabil fundamental, Lei de Benford aplicada a dados financeiros, analise de tendencias e indices, contas transitórias, estruturacao (smurfing), lavagem de dinheiro (colocacao, estratificacao, integracao)."
    },
    "iso27001_li/fundamentals_isms": {
        "cert": "ISO 27001 Lead Implementer",
        "domain": "Fundamentos e Gestão de ISMS",
        "context": "ISO 27001:2022 Lead Implementer PECB - Fundamentos: conceitos CIA, nao-repudio, familia ISO 27000, estrutura HLS, ciclo PDCA, valor da informacao, analise de riscos qualitativa vs quantitativa, ameacas humanas/naturais/tecnicas, vulnerabilidades, ciclo de incidentes, medidas preventivas/detectivas/corretivas/repressivas, classificacao da informacao, autenticacao multifator, zonas de protecao fisica, SGSI, malware e tipos, engenharia social, legislacao de protecao de dados, LGPD, politica de uso aceitavel, monitoramento de funcionarios, backup e recuperacao, continuidade de negocios."
    },
}

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

def gera_questao(cert_name, domain_name, context, quiz_num, q_num, textos_existentes):
    topicos = list(textos_existentes)[:8]
    prompt = f"""Voce e um examinador senior de certificacao para {cert_name}.
Dominio: {domain_name}
Contexto: {context}

Gere EXATAMENTE 1 questao UNICA E ORIGINAL numero {q_num} para o Quiz #{quiz_num}.
Aborde aspecto DIFERENTE dos topicos ja cobertos:
{chr(10).join(f'- {t[:60]}' for t in topicos)}

Regras: nivel senior, 4 alternativas, justificativas normativas, PORTUGUES BRASILEIRO.
Retorne APENAS JSON valido:
{{"questions":[{{"num":{q_num},"text":"QUESTAO","tag":"TAG","options":["A. op1","B. op2","C. op3","D. op4"],"correct":0,"justification_correct":"justificativa.","justification_wrong":"justificativa."}}]}}"""
    try:
        msg = client.messages.create(model="claude-haiku-4-5-20251001",max_tokens=1000,messages=[{"role":"user","content":prompt}])
        raw = "".join(b.text for b in msg.content if hasattr(b,"text"))
        return extract_question(raw)
    except Exception as e:
        print(f"ERRO API: {e}")
        return None

def completa_quiz(path, ctx):
    data = json.loads(path.read_text(encoding="utf-8"))
    questions = data.get("questions",[])
    n_atual = len(questions)
    faltam = 50 - n_atual
    if faltam <= 0: return 0

    textos = {normaliza(q.get("text","")) for q in questions}
    adicionadas = 0

    for i in range(faltam):
        q_num = n_atual + i + 1
        print(f"    Q#{q_num}...", end=" ", flush=True)
        nova = gera_questao(ctx["cert"], ctx["domain"], ctx["context"], data.get("quiz_num",1), q_num, textos)
        if nova:
            nova["num"] = q_num
            t_norm = normaliza(nova.get("text",""))
            if t_norm in textos:
                print("dup, retentando...", end=" ", flush=True)
                nova = gera_questao(ctx["cert"], ctx["domain"], ctx["context"], data.get("quiz_num",1), q_num, textos)
                if nova: nova["num"] = q_num; t_norm = normaliza(nova.get("text",""))
            if nova:
                questions.append(nova)
                textos.add(t_norm)
                adicionadas += 1
                print("OK")
            else: print("FALHOU")
        else: print("FALHOU")
        time.sleep(0.3)

    data["questions"] = questions
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return adicionadas

print("=" * 60)
print("  NEXOR — COMPLETADOR v2 (6 quizzes restantes)")
print("=" * 60)

total = 0
for path in sorted(QUIZ_DIR.rglob("quiz_*_pt.json")):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        n = len(data.get("questions",[]))
        if n >= 50: continue
        cert_id = data.get("cert_id","")
        domain_id = data.get("domain_id","")
        chave = f"{cert_id}/{domain_id}"
        if chave not in CONTEXTS:
            print(f"SEM CONTEXTO: {chave} — pulando")
            continue
        faltam = 50 - n
        print(f"\n📁 {path.name} — {n} questoes (faltam {faltam})")
        n_add = completa_quiz(path, CONTEXTS[chave])
        total += n_add
        print(f"   ✅ {n_add} adicionadas → total: {n+n_add}")
    except Exception as e:
        print(f"ERRO: {e}")

print(f"\n{'='*60}")
print(f"  CONCLUIDO! {total} questoes adicionadas.")
print(f"{'='*60}")
