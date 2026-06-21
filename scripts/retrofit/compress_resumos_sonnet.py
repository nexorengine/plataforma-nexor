"""
Comprime resumos analíticos acima de 800 caracteres para a faixa 600-800 chars.
Usa claude-sonnet-4-6 (custo ~10x menor que Opus, qualidade suficiente para compressão).

Escopo: 3.383 resumos acima de 800 chars
Estimativa de custo: ~$15
Tempo estimado: ~25 minutos (5 workers paralelos)

Uso:
    python compress_resumos_sonnet.py              # roda tudo
    python compress_resumos_sonnet.py --piloto     # roda só abdome_agudo (50 resumos, teste)
    python compress_resumos_sonnet.py --area cirurgia_geral  # roda uma área
"""

import anthropic
import json
import os
import sys
import time
import glob
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

client = anthropic.Anthropic()
MODEL  = "claude-sonnet-4-6"
ALVO_MIN = 600
ALVO_MAX = 800
ALVO_MAX_TOLERANCIA = 850  # aceita até 850 para evitar loop excessivo de retries
MAX_TENTATIVAS = 3
WORKERS = 5

SYSTEM = """Você é editor médico especializado em material de estudo para Residência Médica brasileira.

Recebe um resumo analítico de uma questão de múltipla escolha. Sua tarefa é reescrevê-lo para caber EXATAMENTE entre 600 e 800 caracteres (conte os caracteres, não as palavras).

Regras obrigatórias:
- Entre 600 e 800 caracteres no total (incluindo espaços e pontuação)
- Mantenha: o raciocínio da alternativa correta, por que as erradas estão erradas, e a referência clínica se houver
- Linguagem técnica, compacta, sem floreios
- Retorne APENAS o texto do resumo — sem cabeçalho, sem marcadores, sem aspas"""


def montar_prompt(questao, opts, correta_idx, resumo_atual, tentativa=1):
    opts_str = "\n".join(f"{chr(65+i)}) {o}" for i, o in enumerate(opts))
    instrucao_extra = ""
    if tentativa > 1:
        instrucao_extra = f"\n\nATENCAO: o texto deve ter entre {ALVO_MIN} e {ALVO_MAX} caracteres. Sua resposta anterior ficou fora da faixa. Seja mais {'conciso' if tentativa == 2 else 'detalhado'}."
    return f"""QUESTAO:
{questao}

ALTERNATIVAS:
{opts_str}

ALTERNATIVA CORRETA: {chr(65 + correta_idx)}

RESUMO ATUAL ({len(resumo_atual)} chars — reescreva dentro de 600-800 chars):
{resumo_atual}{instrucao_extra}"""


def comprimir(arquivo, num_questao, questao, opts, correta_idx, resumo_atual):
    """Processa um único resumo. Retorna (num, novo_texto, chars, ok)."""
    texto = resumo_atual
    for t in range(1, MAX_TENTATIVAS + 1):
        try:
            resp = client.messages.create(
                model=MODEL,
                max_tokens=350,
                system=SYSTEM,
                messages=[{"role": "user", "content": montar_prompt(questao, opts, correta_idx, texto, t)}]
            )
            texto = resp.content[0].text.strip()
            chars = len(texto)
            if ALVO_MIN <= chars <= ALVO_MAX_TOLERANCIA:
                return (num_questao, texto, chars, True)
        except Exception as e:
            time.sleep(2)
    return (num_questao, texto, len(texto), False)


def processar_arquivo(caminho_resumo, caminho_quiz):
    """Processa todos os resumos fora da faixa em um arquivo JSON."""
    with open(caminho_resumo, encoding="utf-8-sig") as f:
        data_r = json.load(f)
    with open(caminho_quiz, encoding="utf-8-sig") as f:
        data_q = json.load(f)

    questoes = {q["num"] if "num" in q else (i+1): q
                for i, q in enumerate(data_q.get("questions", []))}

    tarefas = []
    for r in data_r["resumos"]:
        if len(r["texto"].strip()) > ALVO_MAX_TOLERANCIA:
            num = r["num"]
            q = questoes.get(num, {})
            tarefas.append({
                "num": num,
                "questao": q.get("q", ""),
                "opts": q.get("opts", []),
                "correta_idx": q.get("c", 0),
                "resumo_atual": r["texto"]
            })

    if not tarefas:
        return 0, 0  # nenhuma alteração necessária

    alteracoes = {}
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futuros = {
            pool.submit(comprimir,
                        caminho_resumo,
                        t["num"], t["questao"], t["opts"],
                        t["correta_idx"], t["resumo_atual"]): t["num"]
            for t in tarefas
        }
        for fut in as_completed(futuros):
            num, novo_texto, chars, ok = fut.result()
            alteracoes[num] = (novo_texto, chars, ok)

    # Aplica alterações no JSON
    ok_count = 0
    for r in data_r["resumos"]:
        if r["num"] in alteracoes:
            novo_texto, chars, ok = alteracoes[r["num"]]
            r["texto"] = novo_texto
            if ok:
                ok_count += 1

    with open(caminho_resumo, "w", encoding="utf-8") as f:
        json.dump(data_r, f, ensure_ascii=False, indent=2)

    return len(tarefas), ok_count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--piloto", action="store_true", help="Roda apenas abdome_agudo")
    parser.add_argument("--area", default=None, help="Roda apenas uma area especifica")
    args = parser.parse_args()

    BASE_RESUMOS = r"C:\ARAGORN\plataforma-nexor\content\resumos"
    BASE_QUIZZES = r"C:\ARAGORN\plataforma-nexor\content\quizzes"

    arquivos = sorted(glob.glob(os.path.join(BASE_RESUMOS, "**", "*.json"), recursive=True))

    if args.piloto:
        arquivos = [a for a in arquivos if "abdome_agudo" in a]
        print(f"MODO PILOTO: {len(arquivos)} arquivo(s) de abdome_agudo")
    elif args.area:
        arquivos = [a for a in arquivos if args.area in a]
        print(f"MODO AREA ({args.area}): {len(arquivos)} arquivo(s)")
    else:
        print(f"MODO COMPLETO: {len(arquivos)} arquivos")

    total_tarefas = 0
    total_ok = 0
    inicio = time.time()

    for i, caminho_resumo in enumerate(arquivos, 1):
        # Monta caminho do quiz correspondente
        rel = os.path.relpath(caminho_resumo, BASE_RESUMOS)
        nome_quiz = os.path.basename(rel).replace("_resumos", "")
        caminho_quiz = os.path.join(BASE_QUIZZES, os.path.dirname(rel), nome_quiz)

        if not os.path.exists(caminho_quiz):
            print(f"  [SKIP] Quiz nao encontrado: {caminho_quiz}")
            continue

        area_dom = os.path.dirname(rel)
        print(f"[{i:02d}/{len(arquivos)}] {area_dom}/{nome_quiz}", end="  ", flush=True)

        tarefas, ok = processar_arquivo(caminho_resumo, caminho_quiz)
        total_tarefas += tarefas
        total_ok += ok

        if tarefas == 0:
            print("(todos na faixa, sem alteracao)")
        else:
            pct = round(ok/tarefas*100) if tarefas else 0
            print(f"{tarefas} comprimidos | {ok} OK ({pct}%)")

    elapsed = round(time.time() - inicio)
    print(f"\nConcluido em {elapsed}s")
    print(f"Total processados: {total_tarefas} | Na faixa: {total_ok} | Fora: {total_tarefas - total_ok}")
    if total_tarefas > total_ok:
        print("Os que ficaram fora da faixa foram salvos mesmo assim — revisar manualmente se necessario.")


if __name__ == "__main__":
    main()
