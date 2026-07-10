"""
Pass 4 -- Sonnet 4.6, textos >1000 chars, alvo 600-950 chars.
"""

import anthropic
import json
import os
import time
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed

client = anthropic.Anthropic()
MODEL  = "claude-sonnet-4-6"
ALVO_MIN = 600
ALVO_MAX = 950
LIMITE_ENTRADA = 1000
MAX_TENTATIVAS = 3
WORKERS = 6

SYSTEM = """Voce e editor medico. Reescreva o resumo abaixo em EXATAMENTE 700 a 900 caracteres (conte os caracteres com espacos).

Regras:
- Mantenha: por que a alternativa correta esta certa e por que as erradas estao erradas
- Linguagem tecnica e compacta, sem introducoes nem conclusoes
- Retorne APENAS o texto reescrito, sem mais nada"""


def comprimir(num, resumo_atual, tentativa=1):
    instrucao = ""
    if tentativa == 2:
        instrucao = "\n\nSua resposta anterior ficou longa. Seja mais conciso -- maximo 900 caracteres."
    elif tentativa == 3:
        instrucao = "\n\nCORTE MAIS: escreva entre 700 e 900 caracteres. Elimine detalhes secundarios."

    prompt = f"Resumo atual ({len(resumo_atual)} chars):\n{resumo_atual}{instrucao}"

    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=500,
            system=SYSTEM,
            messages=[{"role": "user", "content": prompt}]
        )
        texto = resp.content[0].text.strip()
        chars = len(texto)
        if ALVO_MIN <= chars <= ALVO_MAX:
            return (num, texto, chars, True)
        if tentativa < MAX_TENTATIVAS:
            return comprimir(num, texto, tentativa + 1)
        return (num, texto, chars, False)
    except Exception as e:
        time.sleep(3)
        return (num, resumo_atual, len(resumo_atual), False)


def processar_arquivo(caminho_resumo):
    with open(caminho_resumo, encoding="utf-8-sig") as f:
        data = json.load(f)

    tarefas = [r for r in data["resumos"] if len(r["texto"].strip()) > LIMITE_ENTRADA]
    if not tarefas:
        return 0, 0

    alteracoes = {}
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futuros = {pool.submit(comprimir, r["num"], r["texto"]): r["num"] for r in tarefas}
        for fut in as_completed(futuros):
            num, novo_texto, chars, ok = fut.result()
            alteracoes[num] = (novo_texto, chars, ok)

    ok_count = 0
    for r in data["resumos"]:
        if r["num"] in alteracoes:
            novo_texto, chars, ok = alteracoes[r["num"]]
            r["texto"] = novo_texto
            if ok:
                ok_count += 1

    with open(caminho_resumo, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return len(tarefas), ok_count


def main():
    BASE = r"C:\NEXOR_MED\plataforma-nexor\content\resumos"
    arquivos = sorted(glob.glob(os.path.join(BASE, "**", "*.json"), recursive=True))

    total_tarefas = total_ok = 0
    inicio = time.time()

    for i, caminho in enumerate(arquivos, 1):
        print(f"[{i:02d}/{len(arquivos)}] {os.path.relpath(caminho, BASE)}", end="  ", flush=True)
        tarefas, ok = processar_arquivo(caminho)
        total_tarefas += tarefas
        total_ok += ok
        if tarefas == 0:
            print("(sem alvo)")
        else:
            pct = round(ok / tarefas * 100) if tarefas else 0
            print(f"{tarefas} processados | {ok} OK ({pct}%)")

    elapsed = round(time.time() - inicio)
    print(f"\nConcluido em {elapsed}s")
    print(f"Total: {total_tarefas} | Na faixa: {total_ok} | Fora: {total_tarefas - total_ok}")


if __name__ == "__main__":
    main()