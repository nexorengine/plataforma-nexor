"""
auditar_flashcards.py — NEXOR CFE Flashcard Audit
Detecta duplicatas exatas e near-duplicatas por domínio e idioma.
Gera relatório completo antes de qualquer modificação.

Uso:
    python auditar_flashcards.py
    python auditar_flashcards.py --lang pt
    python auditar_flashcards.py --domain accounting_concepts
"""

import json
import os
import hashlib
import argparse
from pathlib import Path
from collections import defaultdict

# ── CONFIG ────────────────────────────────────────────────────────────────────
BASE_DIR    = Path(r"C:\ARAGORN\aragorn_quiz\static\flashcards\cfe")
REPORT_OUT  = Path(r"C:\ARAGORN\aragorn_quiz\audit_flashcards_report.txt")
LANGS       = ["pt", "en", "es"]
SIMILARITY_THRESHOLD = 0.82  # jaccard — acima disso = near-duplicate

# ── HELPERS ──────────────────────────────────────────────────────────────────

def normalize(text: str) -> str:
    """Lowercase, strip, remove pontuação básica para comparação."""
    import re
    return re.sub(r"[^\w\s]", "", text.lower().strip())

def md5(text: str) -> str:
    return hashlib.md5(normalize(text).encode()).hexdigest()

def jaccard(a: str, b: str) -> float:
    """Similaridade Jaccard entre dois textos (por palavras)."""
    sa = set(normalize(a).split())
    sb = set(normalize(b).split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)

def load_flashcards(path: Path) -> list:
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        # suporta tanto lista direta quanto {"flashcards": [...]}
        if isinstance(data, list):
            return data
        for key in ("flashcards", "cards", "data"):
            if key in data and isinstance(data[key], list):
                return data[key]
        return []
    except Exception as e:
        return []

def get_text(card: dict, field: str, lang: str) -> str:
    """Extrai texto de front ou back para um idioma."""
    val = card.get(field, {})
    if isinstance(val, dict):
        return val.get(lang, val.get("en", "")).strip()
    if isinstance(val, str):
        return val.strip()
    return ""

# ── ANÁLISE POR ARQUIVO ───────────────────────────────────────────────────────

def audit_file(path: Path, lang: str) -> dict:
    cards = load_flashcards(path)
    total = len(cards)

    if total == 0:
        return {"total": 0, "exact_dupes": [], "near_dupes": [], "empty": 0, "good": 0, "path": str(path)}

    fronts      = []
    hash_map    = defaultdict(list)  # md5 → [ids]
    empty_ids   = []

    for card in cards:
        cid   = card.get("id", "?")
        front = get_text(card, "front", lang)
        if not front:
            empty_ids.append(cid)
            fronts.append(("", cid))
            continue
        h = md5(front)
        hash_map[h].append((cid, front))
        fronts.append((front, cid))

    # Duplicatas exatas
    exact_dupes = []
    for h, entries in hash_map.items():
        if len(entries) > 1:
            exact_dupes.append({
                "ids":    [e[0] for e in entries],
                "front":  entries[0][1][:100]
            })

    # Near-duplicates (O(n²) — aceitável para n≤50)
    near_dupes = []
    seen_pairs = set()
    valid = [(f, cid) for f, cid in fronts if f]
    for i in range(len(valid)):
        for j in range(i+1, len(valid)):
            fi, idi = valid[i]
            fj, idj = valid[j]
            pair = tuple(sorted([idi, idj]))
            if pair in seen_pairs:
                continue
            # Pula se já são exatas
            if md5(fi) == md5(fj):
                continue
            sim = jaccard(fi, fj)
            if sim >= SIMILARITY_THRESHOLD:
                seen_pairs.add(pair)
                near_dupes.append({
                    "ids":        [idi, idj],
                    "similarity": round(sim, 2),
                    "front_a":    fi[:80],
                    "front_b":    fj[:80]
                })

    exact_ids = set()
    for d in exact_dupes:
        exact_ids.update(d["ids"][1:])  # mantém o primeiro, marca o resto
    near_ids = set()
    for d in near_dupes:
        near_ids.add(d["ids"][1])

    problem_ids = exact_ids | near_ids | set(empty_ids)
    good = total - len(problem_ids)

    return {
        "path":        str(path),
        "total":       total,
        "good":        good,
        "exact_dupes": exact_dupes,
        "near_dupes":  near_dupes,
        "empty":       len(empty_ids),
        "problem_count": len(problem_ids),
    }

# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang",   default=None, help="Filtrar por idioma: pt/en/es")
    parser.add_argument("--domain", default=None, help="Filtrar por domínio específico")
    args = parser.parse_args()

    target_langs   = [args.lang] if args.lang else LANGS
    target_domains = [args.domain] if args.domain else None

    if not BASE_DIR.exists():
        print(f"[ERRO] Diretório não encontrado: {BASE_DIR}")
        return

    domains = sorted([d for d in BASE_DIR.iterdir() if d.is_dir()])
    if target_domains:
        domains = [d for d in domains if d.name in target_domains]

    lines        = []
    grand_total  = 0
    grand_good   = 0
    grand_exact  = 0
    grand_near   = 0
    grand_empty  = 0
    domain_needs_regen = []

    sep = "─" * 72

    lines.append("╔══════════════════════════════════════════════════════════════════════╗")
    lines.append("║         NEXOR · AUDITORIA DE FLASHCARDS · CFE 2026                  ║")
    lines.append("╚══════════════════════════════════════════════════════════════════════╝")
    lines.append(f"  Base: {BASE_DIR}")
    lines.append(f"  Idiomas auditados: {', '.join(target_langs).upper()}")
    lines.append(f"  Domínios: {len(domains)}")
    lines.append("")

    for domain_dir in domains:
        domain_name = domain_dir.name
        domain_lines = []
        domain_has_problem = False
        domain_total = 0
        domain_good  = 0

        for lang in target_langs:
            fpath = domain_dir / f"flashcards_{lang}.json"
            if not fpath.exists():
                domain_lines.append(f"    [{lang.upper()}] ⚠  arquivo não encontrado")
                continue

            r = audit_file(fpath, lang)
            domain_total += r["total"]
            domain_good  += r["good"]
            grand_total  += r["total"]
            grand_good   += r["good"]
            grand_exact  += len(r["exact_dupes"])
            grand_near   += len(r["near_dupes"])
            grand_empty  += r["empty"]

            status = "✅" if r["problem_count"] == 0 else "⚠ "
            if r["problem_count"] > 0:
                domain_has_problem = True

            domain_lines.append(
                f"    [{lang.upper()}] {status}  total={r['total']:>2}  bons={r['good']:>2}"
                f"  exatas={len(r['exact_dupes']):>2}  near={len(r['near_dupes']):>2}  vazios={r['empty']}"
            )

            # Detalhe de duplicatas exatas
            for d in r["exact_dupes"]:
                domain_lines.append(f"           EXATA ids={d['ids']} → \"{d['front'][:70]}\"")

            # Detalhe de near-dupes
            for d in r["near_dupes"]:
                domain_lines.append(
                    f"           SIMILAR {d['similarity']*100:.0f}% ids={d['ids']}"
                    f"\n             A: \"{d['front_a']}\""
                    f"\n             B: \"{d['front_b']}\""
                )

        verdict = "REGENERAR" if domain_has_problem else "OK"
        if domain_has_problem:
            domain_needs_regen.append(domain_name)

        lines.append(f"  [{verdict:>9}]  {domain_name}")
        lines.extend(domain_lines)
        lines.append("")

    # SUMÁRIO FINAL
    lines.append(sep)
    lines.append("  SUMÁRIO GERAL")
    lines.append(sep)
    lines.append(f"  Domínios auditados : {len(domains)}")
    lines.append(f"  Total de cards     : {grand_total}")
    lines.append(f"  Cards sem problema : {grand_good}")
    lines.append(f"  Duplicatas exatas  : {grand_exact}")
    lines.append(f"  Near-duplicatas    : {grand_near}")
    lines.append(f"  Cards vazios       : {grand_empty}")
    lines.append(f"  Domínios p/ regen  : {len(domain_needs_regen)}")
    lines.append("")

    if domain_needs_regen:
        lines.append("  DOMÍNIOS QUE PRECISAM DE REGENERAÇÃO FRACTAL:")
        for d in domain_needs_regen:
            lines.append(f"    · {d}")
    else:
        lines.append("  ✅ Nenhum domínio precisa de regeneração.")

    lines.append(sep)

    report = "\n".join(lines)
    print(report)

    with open(REPORT_OUT, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n  Relatório salvo em: {REPORT_OUT}")

if __name__ == "__main__":
    main()
