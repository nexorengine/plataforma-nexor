"""
NEXOR MED — GERADOR DE CONTEUDO PEDIATRIA v1
Gera via API Anthropic:
  · 48 FractalFlashcards PT por dominio (F1x12 + F2x12 + F3x12 + F4x12)
  · Quiz 001 PT — 50 questoes
  · Quiz 002 PT — 50 questoes (zero repeat com Quiz 001)

Padrao FractalFlashcard v1:
  · frente <= 15 palavras
  · verso  <= 25 palavras
  · zero exemplos / zero narrativa

Quiz:
  · distribuicao EASY/STANDARD/HARD: 10/30/10 por quiz
  · 4 alternativas (A-D)
  · campos: question, options{A,B,C,D}, correct, difficulty,
            justification_correct, justification_wrong
  · anti-repeat: Quiz 002 nao repete temas do Quiz 001

USO:
    python gerar_conteudo_pediatria.py --dominio puericultura
    python gerar_conteudo_pediatria.py --todos

OUTPUT:
    flashcards\\med\\pediatria\\{dominio}\\flashcards_pt.json
    quizzes\\med\\pediatria\\{dominio}\\quiz_001_pt.json
    quizzes\\med\\pediatria\\{dominio}\\quiz_002_pt.json
"""

import json
import os
import sys
import time
import argparse
from pathlib import Path
import anthropic

# ═══ CONFIGURACAO ══════════════════════════════════════════════════
FLASHCARD_BASE = Path(r"flashcards\med\pediatria")
QUIZ_BASE      = Path(r"quizzes\med\pediatria")
MODEL          = "claude-haiku-4-5-20251001"
MAX_TOKENS     = 8000
RETRY_MAX      = 3
RETRY_DELAY    = 10  # segundos entre retries

# ═══ MAPA DE DOMINIOS ══════════════════════════════════════════════
DOMAINS = [
    {
        "key": "puericultura",
        "code": "PED_D01",
        "name": "Puericultura e Desenvolvimento",
        "topicos": (
            "marcos do desenvolvimento neuropsicomotor (DNPM), curvas de crescimento OMS, "
            "aleitamento materno exclusivo e complementar, calendario vacinal SBP/MS, "
            "triagem neonatal (teste do pezinho, olhinho, orelhinha, coracaozinho), "
            "consultas de puericultura, alimentacao complementar, prevencao de acidentes, "
            "vitamina D e ferro profilatico, sinais de alerta no desenvolvimento"
        ),
        "refs": "SBP (Sociedade Brasileira de Pediatria), Caderneta de Saude da Crianca MS, Nelson Textbook of Pediatrics"
    },
    {
        "key": "neonatologia",
        "code": "PED_D02",
        "name": "Neonatologia",
        "topicos": (
            "reanimacao neonatal em sala de parto (algoritmo SBP 2016/2021), "
            "indice de Apgar, classificacao do RN (IG, peso, curvas Fenton), "
            "ictericia neonatal fisiologica vs patologica, doenca hemolitica do RN, "
            "hipoglicemia neonatal, sepse neonatal precoce e tardia, "
            "sindrome do desconforto respiratorio (doenca da membrana hialina), "
            "enterocolite necrosante, prematuridade e suas complicacoes, "
            "triagem neonatal ampliada, alojamento conjunto"
        ),
        "refs": "SBP, Programa de Reanimacao Neonatal SBP, Nelson Textbook of Pediatrics, MS"
    },
    {
        "key": "pneumologia_ped",
        "code": "PED_D03",
        "name": "Pneumologia Pediatrica",
        "topicos": (
            "asma na infancia (classificacao GINA, escores de gravidade, manejo crise e manutencao), "
            "bronquiolite viral aguda (VRS, tratamento de suporte), "
            "pneumonia adquirida na comunidade pediatrica (etiologia por faixa etaria, antibioticoterapia), "
            "laringotraqueobronquite (crupe viral), epiglotite, "
            "corpo estranho em vias aereas, sibilancia recorrente no lactente, "
            "fibrose cistica (triagem, diagnostico, manejo), "
            "infeccao respiratoria aguda alta (otite media, sinusite, faringoamigdalite)"
        ),
        "refs": "SBP, GINA Pediatric, Nelson Textbook of Pediatrics, MS Protocolos"
    },
    {
        "key": "infectologia_ped",
        "code": "PED_D04",
        "name": "Infectologia Pediatrica",
        "topicos": (
            "doencas exantematicas (sarampo, rubeola, varicela, escarlatina, exantema subito, eritema infeccioso), "
            "meningite bacteriana e viral pediatrica (diagnostico, tratamento, quimioprofilaxia), "
            "sepse pediatrica (criterios, manejo bundle), "
            "doenca de Kawasaki (criterios diagnosticos, complicacoes, tratamento), "
            "imunizacoes especiais (imunocomprometidos, calendario especial SBIm), "
            "toxoplasmose congenita, citomegalovirus congenito, "
            "tuberculose na infancia (diagnostico, tratamento, PPD), "
            "parasitoses intestinais (giardia, ascaridíase, enterobiose)"
        ),
        "refs": "SBP, SBIm, MS Protocolos, Nelson Textbook of Pediatrics, ANVISA"
    },
    {
        "key": "emergencias_ped",
        "code": "PED_D05",
        "name": "Emergencias Pediatricas",
        "topicos": (
            "parada cardiorrespiratoria pediatrica (algoritmo PALS, RCP basica e avancada), "
            "anafilaxia (reconhecimento, adrenalina IM, doses pediatricas), "
            "convulsao febril (simples vs complexa, conduta, profilaxia), "
            "status epilepticus (protocolo de tratamento), "
            "choque pediatrico (tipos, reconhecimento, ressuscitacao volumetrica), "
            "broncoespasmo grave (manejo em emergencia), "
            "intoxicacoes exogenas na infancia (acetaminofen, organofosforados), "
            "trauma pediatrico (particularidades anatomicas, ATLS pediatrico), "
            "acesso vascular em emergencia (intraosseo)"
        ),
        "refs": "PALS (Pediatric Advanced Life Support), SBP, ATLS, MS Protocolos"
    },
    {
        "key": "gastro_ped",
        "code": "PED_D06",
        "name": "Gastroenterologia Pediatrica",
        "topicos": (
            "desidratacao (classificacao, planos A/B/C OMS/MS, terapia de reidratacao oral), "
            "diarreia aguda pediatrica (etiologias, rotavirus, conduta), "
            "estenose hipertrofica do piloro (clinica, diagnostico US, tratamento cirurgico), "
            "invaginacao intestinal (triada clinica, enema diagnostico-terapeutico), "
            "doenca do refluxo gastroesofagico pediatrico, "
            "alergia a proteina do leite de vaca (APLV), "
            "hepatite A na infancia, colestase neonatal (atresia de vias biliares), "
            "constipacao cronica funcional pediatrica, dor abdominal recorrente"
        ),
        "refs": "SBP, OMS, MS Protocolos, Nelson Textbook of Pediatrics, NASPGHAN"
    },
    {
        "key": "cardio_ped",
        "code": "PED_D07",
        "name": "Cardiologia Pediatrica",
        "topicos": (
            "cardiopatias congenitas acianogenicas (CIV, CIA, PCA, coartacao da aorta), "
            "cardiopatias congenitas cianogenicas (tetralogia de Fallot, TGA, DSAVT), "
            "avaliacao do sopro cardiaco na infancia (inocente vs patologico), "
            "febre reumatica (criterios de Jones, profilaxia secundaria), "
            "doenca de Kawasaki e aneurismas coronarianos, "
            "miocardite e pericardite pediatrica, "
            "hipertensao arterial na infancia (percentis, etiologias), "
            "arritmias pediatricas (TSV, tratamento adenosina), "
            "insuficiencia cardiaca na infancia"
        ),
        "refs": "SBC, SBP, AHA, Nelson Textbook of Pediatrics, Braunwald"
    },
    {
        "key": "hematologia_onco_ped",
        "code": "PED_D08",
        "name": "Hematologia e Oncologia Pediatrica",
        "topicos": (
            "anemia ferropriva (diagnostico, tratamento, profilaxia), "
            "anemia falciforme (triagem neonatal, complicacoes, manejo crise vaso-oclusiva), "
            "purpura trombocitopenica imune (PTI) pediatrica (diagnostico, tratamento), "
            "leucemia linfoblastica aguda (LLA) — mais comum na infancia, "
            "linfoma de Hodgkin e nao-Hodgkin pediatrico, "
            "tumor de Wilms (nefroblastoma), retinoblastoma, "
            "sindrome de lise tumoral (prevencao e manejo), "
            "coagulopatias hereditarias (hemofilia A e B, von Willebrand), "
            "neutropenia febril em oncologia pediatrica"
        ),
        "refs": "SBP, INCA, Nelson Textbook of Pediatrics, Sociedade Brasileira de Hematologia"
    },
    {
        "key": "endocrinologia_ped",
        "code": "PED_D09",
        "name": "Disturbios do Crescimento e Endocrinologia Pediatrica",
        "topicos": (
            "diabetes mellitus tipo 1 na infancia (diagnostico, cetoacidose diabetica pediatrica, insulinoterapia), "
            "hipotireoidismo congenito (triagem neonatal, levotiroxina, janela de tratamento), "
            "puberdade precoce central vs periferica (diagnostico, tratamento), "
            "baixa estatura (diagnostico diferencial, deficiencia de GH), "
            "hipoglicemia neonatal e da infancia (etiologias, manejo), "
            "insuficiencia adrenal (crise adrenal, hidrocortisona), "
            "hiperplasia adrenal congenita (triagem, forma classica perdedora de sal), "
            "disturbios da diferenciacao sexual, obesidade infantil (complicacoes, manejo)"
        ),
        "refs": "SBP, SBEM (Sociedade Brasileira de Endocrinologia), Nelson Textbook of Pediatrics, MS"
    },
]

# ═══ PROMPTS ═══════════════════════════════════════════════════════

def prompt_flashcards(domain):
    return f"""Voce e um especialista em Pediatria e residencia medica brasileira (ACM/SC, ENARE, AMRIGS).

Gere EXATAMENTE 48 FractalFlashcards para o dominio: {domain['name']}

Topicos obrigatorios: {domain['topicos']}
Referencias: {domain['refs']}

REGRAS ABSOLUTAS:
- frente: <= 15 palavras, pergunta direta ou termo clinico
- verso: <= 25 palavras, resposta minima suficiente, sem exemplos
- zero narrativa, zero contexto adicional, zero exemplos
- linguagem tecnica precisa (PT-BR medico)
- cada card deve ser independente e testavel

ESTRUTURA FractalFlashcard v1 (4 camadas x 12 cards):
- F1 (Definicao): 12 cards — conceitos fundamentais, definicoes, criterios
- F2 (Distincao): 12 cards — diferenciais clinicos, comparacoes, classificacoes
- F3 (Aplicacao): 12 cards — conduta, doses, protocolos, indicacoes
- F4 (Sintese): 12 cards — red flags, complicacoes, situacoes criticas, pegadinhas de prova

Responda APENAS com JSON valido, sem markdown, sem texto adicional:
{{
  "domain": "{domain['code']}",
  "domain_name": "{domain['name']}",
  "total": 48,
  "cards": [
    {{
      "id": "F1_01",
      "layer": "F1",
      "front": "texto da frente aqui",
      "back": "texto do verso aqui"
    }}
  ]
}}

Gere todos os 48 cards (F1_01 a F1_12, F2_01 a F2_12, F3_01 a F3_12, F4_01 a F4_12)."""


def prompt_quiz(domain, numero, temas_usados=""):
    anti_repeat = ""
    if temas_usados:
        anti_repeat = f"\nTEMAS JA USADOS NO QUIZ 001 (NAO REPETIR): {temas_usados}\n"

    return f"""Voce e um especialista em Pediatria e elaboracao de provas de residencia medica brasileira (ACM/SC, ENARE, AMRIGS).

Gere EXATAMENTE 50 questoes de multipla escolha para o dominio: {domain['name']}
Quiz numero: {numero}
{anti_repeat}
Topicos: {domain['topicos']}
Referencias: {domain['refs']}

DISTRIBUICAO OBRIGATORIA:
- EASY: 10 questoes (conceitos basicos, definicoes diretas)
- STANDARD: 30 questoes (casos clinicos, diagnostico, conduta)
- HARD: 10 questoes (diferenciais dificeis, complicacoes, situacoes atipicas)

REGRAS:
- 4 alternativas (A, B, C, D)
- apenas 1 correta
- alternativas plausíveis (erros comuns, distradores tecnicos)
- justification_correct: por que a resposta correta esta certa (max 40 palavras)
- justification_wrong: erro mais comum ou por que as outras estao erradas (max 40 palavras)
- questoes em PT-BR medico
- estilo ACM/SC/ENARE: caso clinico + pergunta de conduta ou diagnostico

Responda APENAS com JSON valido, sem markdown, sem texto adicional:
{{
  "domain": "{domain['code']}",
  "domain_name": "{domain['name']}",
  "quiz_number": {numero},
  "total": 50,
  "questions": [
    {{
      "id": "Q{numero:02d}_01",
      "question": "texto da questao",
      "options": {{
        "A": "opcao A",
        "B": "opcao B",
        "C": "opcao C",
        "D": "opcao D"
      }},
      "correct": "A",
      "difficulty": "EASY",
      "justification_correct": "explicacao da correta",
      "justification_wrong": "erro mais comum"
    }}
  ]
}}

Gere todas as 50 questoes numeradas Q{numero:02d}_01 a Q{numero:02d}_50."""


# ═══ HELPERS ═══════════════════════════════════════════════════════

def call_api(client, prompt, descricao):
    for attempt in range(1, RETRY_MAX + 1):
        try:
            print(f"    API call: {descricao} (tentativa {attempt}/{RETRY_MAX})...")
            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = response.content[0].text.strip()
            # limpa markdown se vier
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            data = json.loads(raw)
            return data
        except json.JSONDecodeError as e:
            print(f"    ERRO JSON: {e} — retry em {RETRY_DELAY}s")
            if attempt < RETRY_MAX:
                time.sleep(RETRY_DELAY)
        except Exception as e:
            print(f"    ERRO API: {e} — retry em {RETRY_DELAY}s")
            if attempt < RETRY_MAX:
                time.sleep(RETRY_DELAY)
    return None


def salvar_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"    SALVO: {path} ({path.stat().st_size:,} bytes)")


def extrair_temas_quiz(quiz_data):
    """Extrai resumo dos temas para anti-repeat no quiz 002"""
    if not quiz_data:
        return ""
    temas = []
    for q in quiz_data.get("questions", [])[:50]:
        txt = q.get("question", "")[:80]
        temas.append(txt)
    return " | ".join(temas[:20])


def auditoria_flashcards(fc_data, domain_code):
    cards = fc_data.get("cards", [])
    total = len(cards)
    erros = []

    layer_counts = {"F1": 0, "F2": 0, "F3": 0, "F4": 0}
    for c in cards:
        layer = c.get("layer", "?")
        if layer in layer_counts:
            layer_counts[layer] += 1
        frente = c.get("front", "")
        verso = c.get("back", "")
        if len(frente.split()) > 15:
            erros.append(f"  FRENTE longa ({len(frente.split())}w): {c['id']}")
        if len(verso.split()) > 25:
            erros.append(f"  VERSO longo ({len(verso.split())}w): {c['id']}")
        if not frente or not verso:
            erros.append(f"  VAZIO: {c['id']}")

    print(f"    AUDITORIA {domain_code}: {total}/48 cards | F1:{layer_counts['F1']} F2:{layer_counts['F2']} F3:{layer_counts['F3']} F4:{layer_counts['F4']}")
    if erros:
        print(f"    AVISOS ({len(erros)}):")
        for e in erros[:5]:
            print(f"      {e}")
    else:
        print(f"    OK — 0 erros")
    return total == 48 and not erros


def auditoria_quiz(quiz_data, domain_code, numero):
    questions = quiz_data.get("questions", [])
    total = len(questions)
    erros = []
    dist = {"EASY": 0, "STANDARD": 0, "HARD": 0}

    for q in questions:
        diff = q.get("difficulty", "?")
        if diff in dist:
            dist[diff] += 1
        if len(q.get("options", {})) != 4:
            erros.append(f"  OPCOES != 4: {q.get('id')}")
        if q.get("correct") not in ["A", "B", "C", "D"]:
            erros.append(f"  CORRETA invalida: {q.get('id')}")

    print(f"    AUDITORIA Quiz {numero:03d} {domain_code}: {total}/50 questoes | EASY:{dist['EASY']} STD:{dist['STANDARD']} HARD:{dist['HARD']}")
    if erros:
        for e in erros[:5]:
            print(f"      {e}")
    else:
        print(f"    OK — 0 erros")
    return total == 50


# ═══ MAIN ══════════════════════════════════════════════════════════

def gerar_dominio(client, domain):
    code = domain["code"]
    key  = domain["key"]
    print(f"\n{'='*60}")
    print(f"  {code} — {domain['name']}")
    print(f"{'='*60}")

    fc_path  = FLASHCARD_BASE / key / "flashcards_pt.json"
    q1_path  = QUIZ_BASE / key / "quiz_001_pt.json"
    q2_path  = QUIZ_BASE / key / "quiz_002_pt.json"

    # --- FLASHCARDS ---
    if fc_path.exists():
        print(f"  [SKIP] flashcards ja existem: {fc_path}")
        fc_data = json.loads(fc_path.read_text(encoding="utf-8"))
    else:
        print(f"  [1/3] Gerando FractalFlashcards...")
        fc_data = call_api(client, prompt_flashcards(domain), f"flashcards {code}")
        if not fc_data:
            print(f"  FALHA flashcards {code} — pulando dominio")
            return False
        auditoria_flashcards(fc_data, code)
        salvar_json(fc_path, fc_data)

    # --- QUIZ 001 ---
    if q1_path.exists():
        print(f"  [SKIP] quiz_001 ja existe: {q1_path}")
        q1_data = json.loads(q1_path.read_text(encoding="utf-8"))
    else:
        print(f"  [2/3] Gerando Quiz 001...")
        q1_data = call_api(client, prompt_quiz(domain, 1), f"quiz_001 {code}")
        if not q1_data:
            print(f"  FALHA quiz_001 {code} — pulando")
            return False
        auditoria_quiz(q1_data, code, 1)
        salvar_json(q1_path, q1_data)

    # --- QUIZ 002 ---
    if q2_path.exists():
        print(f"  [SKIP] quiz_002 ja existe: {q2_path}")
    else:
        print(f"  [3/3] Gerando Quiz 002 (anti-repeat)...")
        temas_q1 = extrair_temas_quiz(q1_data)
        q2_data = call_api(client, prompt_quiz(domain, 2, temas_q1), f"quiz_002 {code}")
        if not q2_data:
            print(f"  FALHA quiz_002 {code}")
            return False
        auditoria_quiz(q2_data, code, 2)
        salvar_json(q2_path, q2_data)

    print(f"  CONCLUIDO: {code} ✓")
    return True


def main():
    parser = argparse.ArgumentParser(description="Gerador NEXOR MED Pediatria")
    parser.add_argument("--dominio", help="key do dominio (ex: puericultura)")
    parser.add_argument("--todos", action="store_true", help="gerar todos os 9 dominios")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERRO: variavel ANTHROPIC_API_KEY nao encontrada")
        print("Defina com: $env:ANTHROPIC_API_KEY = 'sua-chave'")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    if args.todos:
        dominios = DOMAINS
    elif args.dominio:
        dominios = [d for d in DOMAINS if d["key"] == args.dominio]
        if not dominios:
            keys = [d["key"] for d in DOMAINS]
            print(f"Dominio '{args.dominio}' nao encontrado.")
            print(f"Opcoes: {', '.join(keys)}")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(0)

    print("=" * 60)
    print("  NEXOR MED — GERADOR PEDIATRIA v1")
    print(f"  {len(dominios)} dominio(s) a gerar")
    print("=" * 60)

    ok = 0
    falhou = []
    for domain in dominios:
        sucesso = gerar_dominio(client, domain)
        if sucesso:
            ok += 1
        else:
            falhou.append(domain["code"])
        # pausa entre dominios para nao sobrecarregar API
        if len(dominios) > 1:
            time.sleep(3)

    print(f"\n{'='*60}")
    print(f"  CONCLUIDO: {ok}/{len(dominios)} dominios")
    if falhou:
        print(f"  FALHARAM: {', '.join(falhou)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
