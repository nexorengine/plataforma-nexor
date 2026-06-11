"""
NEXOR MED â€” AUDITORIA DE ARQUIVOS PEDIATRIA
Verifica se todos os arquivos foram copiados para as pastas corretas.
Checa: existencia, tamanho, contagem de itens e distribuicao.

USO:
    python auditar_pediatria.py
"""

import json
from pathlib import Path

BASE_FC = Path(r"flashcards\med\pediatria")
BASE_QZ = Path(r"quizzes\med\pediatria")

DOMINIOS = [
    {"key": "puericultura",         "code": "PED_D01", "status": "esperado"},
    {"key": "neonatologia",         "code": "PED_D02", "status": "esperado"},
    {"key": "pneumologia_ped",      "code": "PED_D03", "status": "esperado"},
    {"key": "infectologia_ped",     "code": "PED_D04", "status": "esperado"},
    {"key": "emergencias_ped",      "code": "PED_D05", "status": "esperado"},
    {"key": "gastro_ped",           "code": "PED_D06", "status": "esperado"},
    {"key": "cardio_ped",           "code": "PED_D07", "status": "esperado"},
    {"key": "hematologia_onco_ped", "code": "PED_D08", "status": "esperado"},
    {"key": "endocrinologia_ped",   "code": "PED_D09", "status": "esperado"},
]

def check(path, tipo):
    r = {"existe": False, "bytes": 0, "itens": 0, "distrib": {}, "erros": []}
    if not path.exists():
        r["erros"].append("ARQUIVO NAO ENCONTRADO")
        return r
    r["existe"] = True
    r["bytes"] = path.stat().st_size
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        r["erros"].append(f"ERRO JSON: {e}")
        return r

    if tipo == "fc":
        items = data.get("cards", [])
        r["itens"] = len(items)
        layers = {"F1": 0, "F2": 0, "F3": 0, "F4": 0}
        for c in items:
            layers[c.get("layer", "?")] = layers.get(c.get("layer", "?"), 0) + 1
            if len(c.get("front", "").split()) > 15:
                r["erros"].append(f"FRENTE longa: {c.get('id')}")
            if len(c.get("back", "").split()) > 25:
                r["erros"].append(f"VERSO longo: {c.get('id')}")
        r["distrib"] = layers
        if r["itens"] != 48:
            r["erros"].append(f"TOTAL: {r['itens']}/48")
        for l, n in layers.items():
            if n != 12:
                r["erros"].append(f"LAYER {l}: {n}/12")
    else:
        items = data.get("questions", [])
        r["itens"] = len(items)
        dist = {"EASY": 0, "STANDARD": 0, "HARD": 0}
        for q in items:
            dist[q.get("difficulty", "?")] = dist.get(q.get("difficulty", "?"), 0) + 1
            if q.get("correct") not in ["A","B","C","D"]:
                r["erros"].append(f"CORRETA invalida: {q.get('id')}")
        r["distrib"] = dist
        if r["itens"] != 50:
            r["erros"].append(f"TOTAL: {r['itens']}/50")
        if dist.get("EASY",0) != 10:
            r["erros"].append(f"EASY: {dist.get('EASY')}/10")
        if dist.get("STANDARD",0) != 30:
            r["erros"].append(f"STANDARD: {dist.get('STANDARD')}/30")
        if dist.get("HARD",0) != 10:
            r["erros"].append(f"HARD: {dist.get('HARD')}/10")
    return r

def fmt(tipo, d):
    if tipo == "fc":
        return f"F1={d.get('F1',0)} F2={d.get('F2',0)} F3={d.get('F3',0)} F4={d.get('F4',0)}"
    return f"E={d.get('EASY',0)} S={d.get('STANDARD',0)} H={d.get('HARD',0)}"

def main():
    print("=" * 68)
    print("  NEXOR MED â€” AUDITORIA PEDIATRIA")
    print("=" * 68)
    total_erros = 0
    ok = 0
    pendentes = 0

    for dom in DOMINIOS:
        key, code, status = dom["key"], dom["code"], dom["status"]
        print(f"\n  {code} â€” {key}")
        if status == "pendente":
            print(f"    [PENDENTE]")
            pendentes += 1
            continue

        arquivos = {
            "fc": BASE_FC / key / "flashcards_pt.json",
            "q1": BASE_QZ / key / "quiz_001_pt.json",
            "q2": BASE_QZ / key / "quiz_002_pt.json",
        }
        dom_ok = True
        for tipo, path in arquivos.items():
            r = check(path, tipo)
            lbl = {"fc":"FC ","q1":"Q01","q2":"Q02"}[tipo]
            if not r["existe"]:
                print(f"    [{lbl}] AUSENTE  â€” {path}")
                dom_ok = False
                total_erros += 1
            elif r["erros"]:
                print(f"    [{lbl}] ERRO     â€” {r['itens']} itens | {fmt(tipo,r['distrib'])} | {r['bytes']:,} bytes")
                for e in r["erros"]:
                    print(f"             ! {e}")
                dom_ok = False
                total_erros += len(r["erros"])
            else:
                print(f"    [{lbl}] OK       â€” {r['itens']} itens | {fmt(tipo,r['distrib'])} | {r['bytes']:,} bytes")
        if dom_ok:
            ok += 1

    esperados = sum(1 for d in DOMINIOS if d["status"] == "esperado")
    print("\n" + "=" * 68)
    print(f"  Dominios OK:        {ok}/{esperados}")
    print(f"  Dominios pendentes: {pendentes}/9")
    print(f"  Erros encontrados:  {total_erros}")
    if total_erros == 0 and ok == esperados:
        print(f"\n  STATUS: TUDO VERDE â€” {ok} dominios validados")
    else:
        print(f"\n  STATUS: ATENCAO â€” {total_erros} erro(s) a corrigir")
    print("=" * 68)

if __name__ == "__main__":
    main()





