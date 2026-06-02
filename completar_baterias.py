#!/usr/bin/env python3
"""
NEXOR - COMPLETADOR DE BATERIAS
Completa todos os quizzes com menos de 50 questoes ate o padrao de 50.
Execute em: C:\\NEXOR\\nexor_quiz\\
"""
import os, json, re, time
from pathlib import Path
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY",""))
QUIZ_DIR = Path("static/quizzes")

# Contextos por cert/domain
CONTEXTS = {
    "cfe/fraud_investigation": {
        "cert": "CFE / ACFE",
        "domain": "Fraud Investigation",
        "context": "CFE Fraud Examiners Manual 2024 - Fraud Investigation: metodologia de exame de fraude, predicacao, planejamento, coleta e preservacao de evidencias, entrevistas, interrogatorios, analise comportamental, documentacao, relatorios, cadeia de custodia, forense digital, rastreamento financeiro, Lei de Benford, analise de tendencias, papeis de trabalho, testemunho pericial."
    },
    "cfe/law_cfe": {
        "cert": "CFE / ACFE",
        "domain": "Law",
        "context": "CFE Fraud Examiners Manual 2024 - Law: elementos da fraude na common law, onus da prova (civil vs criminal), admissibilidade de provas, hearsay, prova direta vs circunstancial, cadeia de custodia, privilegio advogado-cliente, work product doctrine, Miranda rights, confissoes, difamacao, conspiração, wire fraud, FCPA, SOX, rescisao contratual, due process, protecao ao whistleblower, Padrao Daubert, lei de crimes computacionais, LGPD."
    },
    "cfe/prevention_deterrence": {
        "cert": "CFE / ACFE",
        "domain": "Fraud Prevention & Deterrence",
        "context": "CFE Fraud Examiners Manual 2024 - Fraud Prevention and Deterrence: Triangulo da Fraude, Diamante da Fraude, controles internos, segregacao de funcoes, tone at the top, cultura etica, avaliacao de risco de fraude, risco residual, programa antifraude, canal de denuncias, whistleblower, monitoramento continuo, analise de dados, red flags comportamentais, psicologia do crime de colarinho branco, moral disengagement, slippery slope, papel do conselho de administracao."
    },
    "cism/info_security_governance": {
        "cert": "CISM",
        "domain": "Information Security Governance",
        "context": "CISM Review Manual ISACA - Information Security Governance: governanca de seguranca da informacao, papeis executivos (CISO, CRO, CSO, CPO, CIRO), comite diretor de ciberseguranca, responsabilidade do conselho, decisoes de tratamento de risco, revisoes de acesso, custódia de ativos, metricas de seguranca, KPIs, TPRM, estrategia de seguranca, gap analysis, maturidade CMMI, estatuto do programa, declaracoes de missao e visao, auditoria interna e independencia, SOX, alinhamento estrategico."
    },
    "iso27001_li/fundamentals_isms": {
        "cert": "ISO 27001 Lead Implementer",
        "domain": "Fundamentos e Gestão de ISMS",
        "context": "ISO 27001:2022 Lead Implementer PECB - Fundamentos: conceitos CIA (confidencialidade, integridade, disponibilidade), nao-repudio, familia ISO 27000, estrutura HLS, ciclo PDCA, valor da informacao, analise qualitativa vs quantitativa de riscos, ameacas (humanas, naturais, tecnicas), vulnerabilidades, ciclo de incidentes, medidas preventivas/detectivas/corretivas/repressivas, classificacao da informacao, autenticacao multifator, zonas de protecao fisica, SGSI, malware, legislacao de protecao de dados, LGPD, politica de uso aceitavel, monitoramento de funcionarios."
    },
    "iso27001_li/planning_implementation": {
        "cert": "ISO 27001 Lead Implementer",
        "domain": "Planejamento e Implementação",
        "context": "ISO 27001:2022 Lead Implementer PECB - Planejamento e Implementacao: clausulas 4-10 da ISO 27001, contexto interno e externo, partes interessadas, escopo do SGSI, lideranca e comprometimento, politica de seguranca, objetivos de seguranca, avaliacao e tratamento de riscos, Plano de Tratamento de Riscos, Declaracao de Aplicabilidade (SoA), Anexo A controles, gestao de recursos, competencia, conscientizacao, comunicacao, informacao documentada, operacoes, auditoria interna, analise critica pela direção, nao conformidades, acoes corretivas, melhoria continua, auditorias Estagio 1 e 2, organismos de certificacao, KPIs do SGSI, gestao de terceiros, gestao de projetos de implementacao."
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
    # Lista de tópicos já cobertos para orientar geração de tópico diferente
    topicos = []
    for t in list(textos_existentes)[:10]:
        topicos.append(t[:60])

    prompt = f"""Voce e um examinador senior de certificacao para {cert_name}.
Dominio: {domain_name}
Contexto tecnico: {context}

Gere EXATAMENTE 1 questao de multipla escolha UNICA E ORIGINAL numero {q_num} para o Quiz #{quiz_num}.
A questao DEVE abordar um aspecto DIFERENTE dos seguintes topicos ja cobertos no quiz:
{chr(10).join(f'- {t}' for t in topicos[:8])}

Regras:
- Nivel senior/implementador
- Exatamente 4 alternativas (A, B, C, D)
- Justificativas tecnicas com referencias normativas
- TUDO em PORTUGUES BRASILEIRO nativo
- Questao desafiadora, nao trivial

Retorne APENAS JSON valido, sem markdown:
{{"questions":[{{"num":{q_num},"text":"TEXTO DA QUESTAO","tag":"SUBTOPICO","options":["A. opcao1","B. opcao2","C. opcao3","D. opcao4"],"correct":0,"justification_correct":"justificativa da resposta correta com referencia normativa.","justification_wrong":"justificativa das respostas incorretas."}}]}}

correct = indice 0-3 da opcao correta."""
    
    try:
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1000,
            messages=[{"role":"user","content":prompt}]
        )
        raw = "".join(b.text for b in msg.content if hasattr(b,"text"))
        return extract_question(raw)
    except Exception as e:
        print(f"    ERRO API: {e}")
        return None

def completa_quiz(path, ctx):
    data = json.loads(path.read_text(encoding="utf-8"))
    questions = data.get("questions",[])
    n_atual = len(questions)
    faltam = 50 - n_atual
    
    if faltam <= 0:
        return 0
    
    cert_name = ctx["cert"]
    domain_name = ctx["domain"]
    context = ctx["context"]
    quiz_num = data.get("quiz_num", 1)
    
    # Coleta textos existentes para evitar duplicatas
    textos_existentes = set()
    for q in questions:
        textos_existentes.add(normaliza(q.get("text","")))
    
    print(f"  Gerando {faltam} questoes novas...")
    adicionadas = 0
    
    for i in range(faltam):
        q_num = n_atual + i + 1
        print(f"    Q#{q_num}...", end=" ", flush=True)
        
        nova = gera_questao(cert_name, domain_name, context, quiz_num, q_num, textos_existentes)
        
        if nova:
            nova["num"] = q_num
            # Verifica duplicata
            texto_norm = normaliza(nova.get("text",""))
            if texto_norm in textos_existentes:
                print("duplicata detectada, tentando novamente...")
                nova = gera_questao(cert_name, domain_name, context, quiz_num, q_num, textos_existentes)
                if nova:
                    nova["num"] = q_num
                    texto_norm = normaliza(nova.get("text",""))
            
            if nova:
                questions.append(nova)
                textos_existentes.add(texto_norm)
                adicionadas += 1
                print("OK")
            else:
                print("FALHOU")
        else:
            print("FALHOU")
        
        time.sleep(0.3)
    
    data["questions"] = questions
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return adicionadas

# ── EXECUTA ───────────────────────────────────────────────────────────────────
print("=" * 65)
print("  NEXOR — COMPLETADOR DE BATERIAS")
print("=" * 65)

total_adicionadas = 0

for path in sorted(QUIZ_DIR.rglob("quiz_*_pt.json")):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        n = len(data.get("questions",[]))
        if n >= 50:
            continue
        
        cert_id = data.get("cert_id","")
        domain_id = data.get("domain_id","")
        chave = f"{cert_id}/{domain_id}"
        
        if chave not in CONTEXTS:
            print(f"\nSEM CONTEXTO: {chave} — pulando")
            continue
        
        faltam = 50 - n
        print(f"\n📁 {chave}/{path.name}")
        print(f"   {n} questoes atuais → completando ate 50 ({faltam} novas)")
        
        n_add = completa_quiz(path, CONTEXTS[chave])
        total_adicionadas += n_add
        print(f"   ✅ {n_add} questoes adicionadas → total: {n + n_add}")
        
    except Exception as e:
        print(f"ERRO em {path}: {e}")

print(f"\n{'='*65}")
print(f"  CONCLUIDO! {total_adicionadas} questoes adicionadas no total.")
print(f"{'='*65}")
