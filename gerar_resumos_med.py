#!/usr/bin/env python3
"""
Gerador de Resumos Analíticos — nexor_med
=========================================
Lê os quizzes de quizzes/med/ e gera resumos analíticos por domínio.
Salva em: prototipo-med/content/resumos/{area}/{dominio}/quiz_{001|002}_resumos.json

PADRÕES DE USO
--------------
# CG — domínios por arquivo na raiz (quiz_001_pt.json, quiz_d2_001_pt.json ...)
python gerar_resumos_med.py --area cirurgia_geral --cg-dominio 1 --quiz 001
python gerar_resumos_med.py --area cirurgia_geral --cg-dominio 2 --quiz 001

# GO, CM, PED, PREV — domínios em subpastas
python gerar_resumos_med.py --area gineco_obstetricia --dominio pre_natal --quiz 001
python gerar_resumos_med.py --area clinica_medica --dominio cardiologia --quiz 001
python gerar_resumos_med.py --area pediatria --dominio neonatologia --quiz 001
python gerar_resumos_med.py --area medicina_preventiva --dominio epidemiologia_geral --quiz 001

Modelo: claude-opus-4-8 (máxima qualidade para conteúdo médico)
"""

import anthropic
import json
import argparse
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

MODEL = "claude-opus-4-8"

REPO       = Path(__file__).parent
QUIZ_DIR   = REPO / "quizzes" / "med"
OUTPUT_DIR = REPO / "prototipo-med" / "content" / "resumos"

# Nomes dos domínios CG por índice
CG_DOMINIOS = {
    1: "abdome_agudo",
    2: "hepatobiliar_pancreas",
    3: "trauma_urgencia",
    4: "perioperatorio",
    5: "hernias_parede_abdominal",
    6: "trato_digestivo_superior",
    7: "trato_digestivo_inferior_coloproctologia",
    8: "cirurgia_vascular",
    9: "queimaduras",
}

# Fontes bibliográficas por área
REFERENCIAS = {
    "cirurgia_geral": [
        "Townsend CM Jr. et al. Sabiston Textbook of Surgery. 21ª ed. Elsevier, 2022.",
        "Brunicardi FC et al. Schwartz's Principles of Surgery. 11ª ed. McGraw-Hill, 2019.",
        "Coelho JCU. Aparelho Digestivo: Clínica e Cirurgia. 4ª ed. São Paulo: Atheneu, 2011.",
    ],
    "gineco_obstetricia": [
        "Rezende J, Montenegro CAB. Obstetrícia Fundamental. 14ª ed. Rio de Janeiro: Guanabara Koogan, 2022.",
        "Berek JS. Berek & Novak's Gynecology. 16ª ed. Lippincott Williams & Wilkins, 2019.",
        "Zugaib M. Obstetrícia. 3ª ed. São Paulo: Manole, 2016.",
        "Brasil. Ministério da Saúde. Protocolos da Atenção Básica — Saúde das Mulheres. Brasília: MS, 2021.",
    ],
    "clinica_medica": [
        "Goldman L, Schafer AI. Goldman-Cecil Medicine. 26ª ed. Elsevier, 2019.",
        "Longo DL et al. Harrison's Principles of Internal Medicine. 21ª ed. McGraw-Hill, 2022.",
        "Martins MA et al. Clínica Médica USP. 2ª ed. São Paulo: Manole, 2016.",
    ],
    "pediatria": [
        "Kliegman RM et al. Nelson Textbook of Pediatrics. 21ª ed. Elsevier, 2020.",
        "Sucupira ACSL et al. Pediatria em Consultório. 5ª ed. São Paulo: Sarvier, 2010.",
        "Brasil. Ministério da Saúde. Cadernos de Atenção Básica — Saúde da Criança. Brasília: MS, 2021.",
        "Sociedade Brasileira de Pediatria. Guias de Orientação SBP. Rio de Janeiro: SBP, 2023.",
    ],
    "medicina_preventiva": [
        "Medronho RA et al. Epidemiologia. 2ª ed. São Paulo: Atheneu, 2009.",
        "Rouquayrol MZ, Gurgel M. Epidemiologia & Saúde. 7ª ed. Rio de Janeiro: MedBook, 2013.",
        "Brasil. Ministério da Saúde. Guia de Vigilância em Saúde. 5ª ed. Brasília: MS, 2022.",
        "Hulley SB et al. Delineando a Pesquisa Clínica. 4ª ed. Porto Alegre: Artmed, 2015.",
    ],
}

SYSTEM_PROMPT = """Você é especialista em medicina e educação médica, responsável por criar
resumos analíticos de alta qualidade para questões de residência médica.

O resumo deve:
1. Explicar por que a alternativa CORRETA é a resposta certa, com base fisiopatológica e clínica sólida
2. Explicar de forma precisa por que cada alternativa INCORRETA está errada
3. Contextualizar o tema na prática clínica e nas provas de residência médica brasileiras
4. Usar linguagem técnica precisa, em português brasileiro
5. Ter entre 150 e 280 palavras — texto corrido em parágrafos, sem listas ou bullet points
6. NÃO incluir seções de "macete", "dica", "resumo", "lembre-se" ou similares
7. Indicar ao final a referência bibliográfica mais adequada para aprofundamento

Responda APENAS com JSON neste formato exato:
{
  "texto": "texto corrido do resumo analítico...",
  "fonte": "Autor(es). Título. Edição. Cidade: Editora, Ano. Cap./pág. se relevante."
}

Nenhum texto fora do JSON."""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def localizar_json_cg(dominio_idx: int, quiz: str) -> Path:
    """CG: domínio 1 = quiz_001_pt.json, domínio N>1 = quiz_dN_001_pt.json"""
    if dominio_idx == 1:
        p = QUIZ_DIR / "cirurgia_geral" / f"quiz_{quiz}_pt.json"
    else:
        p = QUIZ_DIR / "cirurgia_geral" / f"quiz_d{dominio_idx}_{quiz}_pt.json"
    if not p.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {p}")
    return p

def localizar_json_subpasta(area: str, dominio: str, quiz: str) -> Path:
    """GO, CM, PED, PREV: quizzes/med/{area}/{dominio}/quiz_{quiz}_pt.json ou *quiz_{quiz}_pt.json"""
    pasta = QUIZ_DIR / area / dominio
    p = pasta / f"quiz_{quiz}_pt.json"
    if p.exists():
        return p
    candidatos = list(pasta.glob(f"*quiz_{quiz}_pt.json"))
    if candidatos:
        return candidatos[0]
    raise FileNotFoundError(
        f"Arquivo não encontrado em {pasta}\n"
        f"Arquivos disponíveis: {[f.name for f in pasta.iterdir() if f.suffix == '.json']}"
    )

def gerar_resumo(client: anthropic.Anthropic, questao: dict, area: str) -> dict:
    refs = "\n".join(f"- {r}" for r in REFERENCIAS.get(area, []))
    opcoes = questao.get("options", questao.get("alternativas", []))
    correct_idx = questao.get("correct", 0)

    if isinstance(correct_idx, int) and 1 <= correct_idx <= len(opcoes):
        correta_txt = opcoes[correct_idx - 1]
    else:
        correta_txt = str(correct_idx)

    user_msg = f"""Questão:
{questao.get('text', questao.get('pergunta', ''))}

Alternativas:
{chr(10).join(str(o) for o in opcoes)}

Alternativa correta:
{correta_txt}

Justificativa da correta (expanda com base clínica):
{questao.get('justification_correct', '')}

Justificativa das erradas (expanda de forma precisa):
{questao.get('justification_wrong', '')}

Referências bibliográficas para esta área:
{refs}

Gere o resumo analítico conforme as instruções do sistema."""

    resp = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )

    raw = resp.content[0].text.strip()

    # Remove markdown code fences se presentes
    if "```" in raw:
        parts = raw.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("{"):
                raw = part
                break

    raw = raw.strip()

    # Tenta parse direto
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Tenta extrair o JSON via regex (fallback para respostas com texto extra)
    import re
    m = re.search(r'\{[\s\S]*"texto"[\s\S]*"fonte"[\s\S]*\}', raw)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass

    # Último recurso: extrai texto e fonte separadamente
    m_texto = re.search(r'"texto"\s*:\s*"([\s\S]*?)",\s*"fonte"', raw)
    m_fonte = re.search(r'"fonte"\s*:\s*"([\s\S]*?)"[\s\}]', raw)
    if m_texto and m_fonte:
        return {"texto": m_texto.group(1), "fonte": m_fonte.group(1)}

    raise ValueError(f"Não foi possível extrair JSON da resposta:\n{raw[:300]}")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Gerador de Resumos Analíticos nexor_med")
    parser.add_argument("--area", required=True,
        help="cirurgia_geral | gineco_obstetricia | clinica_medica | pediatria | medicina_preventiva")
    parser.add_argument("--dominio", default=None,
        help="Nome do subdomínio (GO/CM/PED/PREV). Ex: pre_natal, cardiologia, neonatologia")
    parser.add_argument("--cg-dominio", type=int, default=None,
        help="Índice do domínio CG (1–9). Use apenas com --area cirurgia_geral")
    parser.add_argument("--quiz", required=True, help="001 ou 002")
    parser.add_argument("--delay", type=float, default=1.5,
        help="Delay entre chamadas à API em segundos (default: 1.5)")
    args = parser.parse_args()

    area  = args.area.lower()
    quiz  = args.quiz.zfill(3)

    # Localiza o JSON e define o nome do domínio para a pasta de saída
    if area == "cirurgia_geral":
        if args.cg_dominio is None:
            parser.error("Para cirurgia_geral use --cg-dominio 1..9")
        idx = args.cg_dominio
        json_path   = localizar_json_cg(idx, quiz)
        dominio_key = CG_DOMINIOS.get(idx, f"d{idx}")
    else:
        if args.dominio is None:
            parser.error("Para esta área use --dominio <nome_do_dominio>")
        dominio_key = args.dominio.lower()
        json_path   = localizar_json_subpasta(area, dominio_key, quiz)

    print(f"\n{'='*64}")
    print(f"  nexor_med — Resumos Analíticos")
    print(f"  Área:    {area}")
    print(f"  Domínio: {dominio_key}")
    print(f"  Quiz:    {quiz}")
    print(f"  Modelo:  {MODEL}")
    print(f"  Fonte:   {json_path.name}")
    print(f"{'='*64}\n")

    with open(json_path, encoding="utf-8") as f:
        dados = json.load(f)

    questoes = dados.get("questions", dados.get("questoes", []))
    titulo   = dados.get("domain_name", dados.get("titulo", dominio_key))
    total    = len(questoes)
    print(f"Domínio: {titulo} — {total} questões\n")

    client = anthropic.Anthropic()

    out_dir = OUTPUT_DIR / area / dominio_key
    out_dir.mkdir(parents=True, exist_ok=True)
    saida_path = out_dir / f"quiz_{quiz}_resumos.json"

    # Retomada de progresso
    if saida_path.exists():
        with open(saida_path, encoding="utf-8") as f:
            saida = json.load(f)
        ja = len(saida["resumos"])
        print(f"Retomando — {ja}/{total} resumos já gerados.\n")
    else:
        saida = {
            "area":    area,
            "dominio": dominio_key,
            "titulo":  titulo,
            "quiz":    quiz,
            "modelo":  MODEL,
            "resumos": []
        }

    ids_prontos = {r["num"] for r in saida["resumos"]}

    for i, q in enumerate(questoes, 1):
        num = q.get("num", i)
        if num in ids_prontos:
            print(f"  [{i:02d}/{total}] Q{num:02d} — já gerado, pulando.")
            continue

        print(f"  [{i:02d}/{total}] Q{num:02d} — gerando...", end=" ", flush=True)
        try:
            resumo = gerar_resumo(client, q, area)
            saida["resumos"].append({"num": num, "texto": resumo["texto"], "fonte": resumo["fonte"]})
            with open(saida_path, "w", encoding="utf-8") as f:
                json.dump(saida, f, ensure_ascii=False, indent=2)
            print("OK")
        except Exception as e:
            print(f"ERRO: {e}")

        if i < total:
            time.sleep(args.delay)

    concluidos = len(saida["resumos"])
    print(f"\nConcluído! {concluidos}/{total} resumos gerados.")
    print(f"Arquivo: {saida_path}\n")


if __name__ == "__main__":
    main()
