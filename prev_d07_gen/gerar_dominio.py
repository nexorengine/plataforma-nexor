#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de domínio NEXOR MED (flashcards FractalFlashcard v1 + 2 quizzes de 50 questões)
via API Anthropic (Claude Sonnet 4.6).

USO:
    set ANTHROPIC_API_KEY=sk-ant-...        (Windows PowerShell: $env:ANTHROPIC_API_KEY="sk-ant-...")
    python gerar_dominio.py CM_D04 Nefrologia "AKI,DRC,Glomerulopatias,DHE,Acido-base,..."

SAÍDA:
    {CODIGO}_flashcards_pt.json
    {CODIGO}_quiz_001_pt.json
    {CODIGO}_quiz_002_pt.json

Custo aproximado: ~$0.50-1.50 por domínio completo (9 chamadas de API).
"""

import json
import os
import re
import sys
import time
import urllib.request

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 8000
MAX_TOKENS_QUIZ = 16000

# ---------------------------------------------------------------------------
# PROMPT BASE - replica o padrão FractalFlashcard v1 / estrutura de quiz NEXOR
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """Você é um especialista em educação médica brasileira, criando conteúdo para a plataforma NEXOR MED (preparação para residência médica - ENARE/AMRIGS/ACM-SC).

REGRAS GERAIS:
- Português do Brasil, terminologia médica precisa, baseada em diretrizes atuais (SBP, sociedades de especialidade, UpToDate-level evidence).
- Responda APENAS com JSON válido, sem markdown, sem texto antes/depois, sem ```json.
- Não repita temas/casos clínicos já usados em outras partes do domínio (você receberá lista de temas já cobertos).
- Tom denso, técnico, direto - sem floreios, sem "vamos pensar", sem exemplos triviais.
"""

FLASHCARD_PROMPT_TEMPLATE = """Gere exatamente {n} flashcards da camada {layer} para o domínio "{titulo}" ({especialidade}).

CAMADA {layer}: {layer_desc}

PADRÃO FractalFlashcard v1:
- F1: front <= 15 palavras, back <= 25 palavras, SEM exemplos, definição pura.
- F2/F3/F4: sem limite rígido, mas mantenha conciso (front 1 frase pergunta/comando, back 2-4 frases).
- Zero exemplos triviais. Foco em distinções, aplicação clínica e síntese multi-conceito.

TEMAS JÁ COBERTOS NESTE DOMÍNIO (não repetir):
{temas_cobertos}

TEMAS-CHAVE SUGERIDOS PARA ESTA CAMADA (pode ajustar conforme necessidade pedagógica):
{temas_sugeridos}

Formato de saída (array JSON, SEM chave externa):
[
  {{"layer": "{layer}", "front": "...", "back": "..."}},
  ...
]

Gere {n} cards agora."""

QUIZ_PROMPT_TEMPLATE = """Gere exatamente {n} questões de múltipla escolha nível {nivel} para o domínio "{titulo}" ({especialidade}), quiz {quiz_num}.

NÍVEL {nivel}: {nivel_desc}

TEMAS/QUESTÕES JÁ USADOS NESTE DOMÍNIO (não repetir conteúdo/casos):
{temas_cobertos}

Cada questão deve ter:
- "pergunta": enunciado (caso clínico para STANDARD/HARD, pergunta direta para EASY)
- "alternativas": array com 4 opções (1 correta + 3 distratores plausíveis)
- "correct": texto exato da alternativa correta (deve ser idêntico a um item de "alternativas")
- "justification_correct": por que a alternativa correta está certa (2-3 frases, mecanismo/evidência)
- "justification_wrong": por que as outras 3 estão erradas, cobrindo cada uma (2-4 frases)

Formato de saída (array JSON, SEM chave externa):
[
  {{"pergunta": "...", "alternativas": ["...", "...", "...", "..."], "correct": "...", "justification_correct": "...", "justification_wrong": "..."}},
  ...
]

Gere {n} questões agora."""

LAYER_DESC = {
    "F1": "Definições puras - conceito central, classificação, critério diagnóstico básico.",
    "F2": "Distinções - diferenciar dois conceitos/condições relacionadas (diagnóstico diferencial, mecanismos opostos).",
    "F3": "Aplicação clínica - caso clínico breve + pergunta de conduta, resposta = conduta correta com racional.",
    "F4": "Síntese - integração de múltiplos conceitos/sistemas, fisiopatologia encadeada, 'como X leva a Y leva a Z'.",
}

NIVEL_DESC = {
    "EASY": "Pergunta direta de conhecimento factual/definição. Sem caso clínico complexo.",
    "STANDARD": "Pergunta 'por que' com racional fisiopatológico/terapêutico, ou caso clínico objetivo de conduta.",
    "HARD": "Caso clínico complexo com múltiplas variáveis, decisão entre condutas próximas, integração de conceitos avançados/exceções/atualizações de diretrizes.",
}


def call_api(system, user_prompt, max_tokens=MAX_TOKENS, retries=3):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY não definida no ambiente.")

    body = json.dumps({
        "model": MODEL,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": user_prompt}],
    }).encode("utf-8")

    req = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )

    last_err = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = "".join(
                    block.get("text", "") for block in data.get("content", [])
                    if block.get("type") == "text"
                )
                usage = data.get("usage", {})
                return text, usage
        except Exception as e:
            last_err = e
            wait = 15 * (attempt + 1)
            print(f"  [retry {attempt+1}/{retries}] erro: {e} -- aguardando {wait}s")
            time.sleep(wait)
    raise RuntimeError(f"Falha após {retries} tentativas: {last_err}")


def extract_json_array(text):
    """Extrai array JSON da resposta, tolerando markdown fences acidentais."""
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"```\s*$", "", text)
    text = text.strip()
    return json.loads(text)


def validate_f1_limits(cards):
    issues = []
    for i, c in enumerate(cards, 1):
        if c["layer"] != "F1":
            continue
        fw = len(c["front"].split())
        bw = len(c["back"].split())
        if fw > 15 or bw > 25:
            issues.append((i, fw, bw))
    return issues


def fix_f1_limits(cards, system, titulo, especialidade):
    """Pede à API para encurtar cards F1 que excedem limites."""
    issues = validate_f1_limits(cards)
    attempts = 0
    while issues and attempts < 3:
        idxs = [i for i, _, _ in issues]
        print(f"  Ajustando {len(idxs)} cards F1 acima do limite (tentativa {attempts+1})...")
        targets = [cards[i-1] for i in idxs]
        prompt = f"""Os seguintes flashcards F1 do domínio "{titulo}" ({especialidade}) excedem o limite (front<=15 palavras, back<=25 palavras).
Reescreva-os mantendo o significado, dentro dos limites.

{json.dumps(targets, ensure_ascii=False, indent=2)}

Responda APENAS com array JSON na mesma ordem, mesmo formato {{"layer":"F1","front":"...","back":"..."}}."""
        text, _ = call_api(system, prompt, max_tokens=2000)
        fixed = extract_json_array(text)
        for idx, new_card in zip(idxs, fixed):
            cards[idx-1] = new_card
        issues = validate_f1_limits(cards)
        attempts += 1
    return cards


def generate_flashcards(titulo, especialidade, temas_por_camada):
    all_cards = []
    temas_cobertos = []
    for layer in ["F1", "F2", "F3", "F4"]:
        print(f"Gerando {layer}...")
        prompt = FLASHCARD_PROMPT_TEMPLATE.format(
            n=12,
            layer=layer,
            layer_desc=LAYER_DESC[layer],
            titulo=titulo,
            especialidade=especialidade,
            temas_cobertos="\n".join(temas_cobertos) if temas_cobertos else "(nenhum ainda)",
            temas_sugeridos=temas_por_camada.get(layer, "Use sua curadoria padrão para este domínio."),
        )
        text, usage = call_api(SYSTEM_PROMPT, prompt)
        print(f"  tokens: in={usage.get('input_tokens')} out={usage.get('output_tokens')}")
        cards = extract_json_array(text)
        if len(cards) != 12:
            print(f"  AVISO: esperado 12, recebido {len(cards)}")
        all_cards.extend(cards)
        for c in cards:
            temas_cobertos.append(f"- [{layer}] {c['front'][:80]}")

    all_cards = fix_f1_limits(all_cards, SYSTEM_PROMPT, titulo, especialidade)

    issues = validate_f1_limits(all_cards)
    if issues:
        print(f"  AVISO: {len(issues)} cards F1 ainda fora do limite após correção: {issues}")

    return all_cards


def generate_quiz(titulo, especialidade, quiz_num, temas_cobertos_global, codigo):
    partial_fname = f"{codigo}_quiz_{quiz_num}.partial.json"

    if os.path.exists(partial_fname):
        print(f"  Encontrado checkpoint {partial_fname}, retomando...")
        questoes = json.load(open(partial_fname, encoding="utf-8"))
    else:
        questoes = []

    temas_cobertos = list(temas_cobertos_global)
    for q in questoes:
        temas_cobertos.append(f"- [{q['nivel']}] {q['pergunta'][:100]}")

    # quantas já temos por nível
    ja_geradas = {}
    for q in questoes:
        ja_geradas[q["nivel"]] = ja_geradas.get(q["nivel"], 0) + 1

    plano = [("EASY", 10, 10), ("STANDARD", 20, 10), ("HARD", 20, 10)]
    for nivel, total, batch in plano:
        feitas = ja_geradas.get(nivel, 0)
        restante = total - feitas
        while restante > 0:
            n = min(batch, restante)
            print(f"Gerando quiz {quiz_num} - {nivel} ({n} de {restante} restantes)...")
            prompt = QUIZ_PROMPT_TEMPLATE.format(
                n=n,
                nivel=nivel,
                nivel_desc=NIVEL_DESC[nivel],
                titulo=titulo,
                especialidade=especialidade,
                quiz_num=quiz_num,
                temas_cobertos="\n".join(temas_cobertos) if temas_cobertos else "(nenhum ainda)",
            )
            text, usage = call_api(SYSTEM_PROMPT, prompt, max_tokens=MAX_TOKENS_QUIZ)
            print(f"  tokens: in={usage.get('input_tokens')} out={usage.get('output_tokens')}")
            try:
                qs = extract_json_array(text)
            except json.JSONDecodeError as e:
                print(f"  ERRO de parse ({e}); tentando reparo automatico...")
                qs = extract_json_array(repair_truncated_array(text))
            if len(qs) != n:
                print(f"  AVISO: esperado {n}, recebido {len(qs)}")
            for q in qs:
                q["nivel"] = nivel
                temas_cobertos.append(f"- [{nivel}] {q['pergunta'][:100]}")
            questoes.extend(qs)
            restante -= len(qs) if qs else n

            # checkpoint após cada lote
            json.dump(questoes, open(partial_fname, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    return questoes, temas_cobertos


def repair_truncated_array(text):
    """Tenta recuperar um array JSON truncado removendo o último objeto incompleto."""
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"```\s*$", "", text)
    text = text.strip()
    if not text.startswith("["):
        raise ValueError("Resposta não começa com '['")
    # encontra o último '},' ou '}' fechando um objeto completo antes do ponto de corte
    last_good = text.rfind("},")
    if last_good == -1:
        last_good = text.rfind("}")
        if last_good == -1:
            raise ValueError("Nenhum objeto completo encontrado")
        return text[:last_good+1] + "]"
    return text[:last_good+1] + "]"


def assemble_quiz(codigo, titulo, quiz_num, questoes):
    for i, q in enumerate(questoes, 1):
        q["id"] = i
    return {
        "dominio": codigo,
        "titulo": titulo,
        "quiz": quiz_num,
        "total_questoes": len(questoes),
        "questoes": questoes,
    }


def main():
    if len(sys.argv) < 4:
        print("Uso: python gerar_dominio.py CODIGO TITULO ESPECIALIDADE [temas_extras]")
        print('Ex:  python gerar_dominio.py CM_D04 Nefrologia "Clinica Medica"')
        sys.exit(1)

    codigo = sys.argv[1]
    titulo = sys.argv[2]
    especialidade = sys.argv[3] if len(sys.argv) > 3 else "Clinica Medica"

    print(f"=== Gerando domínio {codigo} - {titulo} ({especialidade}) ===\n")

    # Temas sugeridos por camada - pode customizar aqui antes de rodar
    temas_por_camada = {
        "F1": "Use curadoria padrão de definições centrais do domínio.",
        "F2": "Use curadoria padrão de distinções diagnósticas/fisiopatológicas centrais.",
        "F3": "Use curadoria padrão de casos clínicos de conduta imediata.",
        "F4": "Use curadoria padrão de integrações multi-sistema/síntese fisiopatológica.",
    }

    t0 = time.time()

    fname = f"{codigo}_flashcards_pt.json"
    if os.path.exists(fname):
        print(f"-> {fname} já existe, reaproveitando (delete o arquivo para regerar)\n")
        flashcards_data = json.load(open(fname, encoding="utf-8"))
        cards = flashcards_data["cards"]
    else:
        cards = generate_flashcards(titulo, especialidade, temas_por_camada)
        flashcards_data = {
            "dominio": codigo,
            "titulo": titulo,
            "especialidade": especialidade,
            "total_cards": len(cards),
            "cards": cards,
        }
        json.dump(flashcards_data, open(fname, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"-> {fname} ({len(cards)} cards)\n")

    temas_cobertos_global = [f"- {c['front'][:80]}" for c in cards]

    # 2. Quiz 001
    fname1 = f"{codigo}_quiz_001_pt.json"
    if os.path.exists(fname1):
        print(f"-> {fname1} já existe, reaproveitando (delete o arquivo para regerar)\n")
        quiz1_data = json.load(open(fname1, encoding="utf-8"))
        q1 = quiz1_data["questoes"]
        temas_cobertos_global += [f"- [{q['nivel']}] {q['pergunta'][:100]}" for q in q1]
    else:
        q1, temas_cobertos_global = generate_quiz(titulo, especialidade, "001", temas_cobertos_global, codigo)
        quiz1_data = assemble_quiz(codigo, titulo, "001", q1)
        json.dump(quiz1_data, open(fname1, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        partial1 = f"{codigo}_quiz_001.partial.json"
        if os.path.exists(partial1):
            os.remove(partial1)
        print(f"-> {fname1} ({len(q1)} questoes)\n")

    # 3. Quiz 002
    fname2 = f"{codigo}_quiz_002_pt.json"
    if os.path.exists(fname2):
        print(f"-> {fname2} já existe, reaproveitando (delete o arquivo para regerar)\n")
        quiz2_data = json.load(open(fname2, encoding="utf-8"))
        q2 = quiz2_data["questoes"]
    else:
        q2, _ = generate_quiz(titulo, especialidade, "002", temas_cobertos_global, codigo)
        quiz2_data = assemble_quiz(codigo, titulo, "002", q2)
        json.dump(quiz2_data, open(fname2, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        partial2 = f"{codigo}_quiz_002.partial.json"
        if os.path.exists(partial2):
            os.remove(partial2)
        print(f"-> {fname2} ({len(q2)} questoes)\n")

    elapsed = time.time() - t0
    print(f"=== Concluído em {elapsed:.1f}s ===")
    print(f"Total: {len(cards)} flashcards + {len(q1)+len(q2)} questoes")


if __name__ == "__main__":
    main()
