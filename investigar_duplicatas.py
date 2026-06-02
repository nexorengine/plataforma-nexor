#!/usr/bin/env python3
"""
NEXOR - INVESTIGADOR DE DUPLICIDADES
Detecta:
1. Questoes duplicadas dentro do mesmo quiz
2. Alternativas duplicadas dentro de uma questao
3. Questoes duplicadas entre quizzes do mesmo dominio

Execute em: C:\\NEXOR\\nexor_quiz\\
"""

import json
from pathlib import Path
from collections import defaultdict

QUIZ_DIR = Path("static/quizzes")

total_quizzes = 0
total_questoes = 0
alertas = []

def normaliza(texto):
    """Normaliza texto para comparacao."""
    return ' '.join(str(texto).lower().strip().split())

def investiga_quiz(path):
    global total_quizzes, total_questoes
    
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  ERRO ao ler {path}: {e}")
        return

    questions = data.get("questions", [])
    if not questions:
        return

    total_quizzes += 1
    total_questoes += len(questions)
    
    cert = data.get("cert_id", "?")
    domain = data.get("domain_id", "?")
    lang = data.get("lang", "?")
    quiz_num = data.get("quiz_num", "?")
    label = f"{cert}/{domain}/quiz_{quiz_num:03d}_{lang}" if isinstance(quiz_num, int) else str(path)

    # ── 1. ALTERNATIVAS DUPLICADAS dentro de cada questao ──────────────────
    for q in questions:
        opts = q.get("options", [])
        if not opts:
            continue
        opts_norm = [normaliza(o) for o in opts]
        vistos = {}
        for i, opt in enumerate(opts_norm):
            if opt in vistos:
                alertas.append({
                    "tipo": "ALTERNATIVA_DUPLICADA",
                    "arquivo": label,
                    "questao": q.get("num", "?"),
                    "detalhe": f"Opcao {i} duplica opcao {vistos[opt]}: '{opts[i][:60]}'"
                })
            else:
                vistos[opt] = i

    # ── 2. QUESTOES DUPLICADAS dentro do mesmo quiz ─────────────────────────
    textos_vistos = {}
    for q in questions:
        texto = normaliza(q.get("text", ""))
        if not texto:
            continue
        if texto in textos_vistos:
            alertas.append({
                "tipo": "QUESTAO_DUPLICADA_INTERNA",
                "arquivo": label,
                "questao": q.get("num", "?"),
                "detalhe": f"Duplica questao #{textos_vistos[texto]}"
            })
        else:
            textos_vistos[texto] = q.get("num", "?")

    return textos_vistos

# ── EXECUTA INVESTIGACAO ───────────────────────────────────────────────────────
print("=" * 60)
print("  NEXOR — INVESTIGADOR DE DUPLICIDADES")
print("=" * 60)

# Agrupa por cert/domain/lang para detectar duplicatas entre quizzes
grupos = defaultdict(dict)  # grupos[cert/domain/lang][num_questao] = texto

for path in sorted(QUIZ_DIR.rglob("quiz_*.json")):
    textos = investiga_quiz(path)
    if textos:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            cert = data.get("cert_id", "?")
            domain = data.get("domain_id", "?")
            lang = data.get("lang", "?")
            quiz_num = data.get("quiz_num", "?")
            grupo_key = f"{cert}/{domain}/{lang}"
            
            for texto_norm, num in textos.items():
                chave = f"{grupo_key}::{texto_norm}"
                if chave in grupos:
                    alertas.append({
                        "tipo": "QUESTAO_DUPLICADA_ENTRE_QUIZZES",
                        "arquivo": f"{grupo_key}/quiz_{quiz_num}",
                        "questao": num,
                        "detalhe": f"Duplica questao em quiz_{grupos[chave]}"
                    })
                else:
                    grupos[chave] = quiz_num
        except:
            pass

# ── RELATORIO ─────────────────────────────────────────────────────────────────
print(f"\n📊 ESTATISTICAS:")
print(f"   Quizzes analisados: {total_quizzes}")
print(f"   Questoes analisadas: {total_questoes}")
print(f"   Alertas encontrados: {len(alertas)}")

if not alertas:
    print("\n✅ NENHUMA DUPLICIDADE ENCONTRADA!")
else:
    print("\n⚠️  DUPLICIDADES ENCONTRADAS:\n")
    
    # Agrupa por tipo
    por_tipo = defaultdict(list)
    for a in alertas:
        por_tipo[a["tipo"]].append(a)
    
    for tipo, lista in por_tipo.items():
        print(f"\n{'─'*60}")
        print(f"  {tipo}: {len(lista)} ocorrencia(s)")
        print(f"{'─'*60}")
        for a in lista[:20]:  # mostra max 20 por tipo
            print(f"  📁 {a['arquivo']}")
            print(f"     Q#{a['questao']}: {a['detalhe']}")
        if len(lista) > 20:
            print(f"  ... e mais {len(lista)-20} ocorrencias")

print("\n" + "=" * 60)
print("  INVESTIGACAO CONCLUIDA")
print("=" * 60)
