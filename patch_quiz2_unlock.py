"""
patch_quiz2_unlock.py — NEXOR
Atualiza a lógica de desbloqueio do Quiz 2 em todos os mini-apps CFE.

Regra nova:
  - Quiz 2 desbloqueia após o usuário COMPLETAR o Quiz 1 pelo menos 1 vez
    (independente da nota)
  - Se nota >= 80%: destaque visual "Avançar!" 
  - Se nota < 80%: disponível mas com mensagem sutil de incentivo

Uso:
    python patch_quiz2_unlock.py --dry-run
    python patch_quiz2_unlock.py --executar
"""

import os
import argparse
from pathlib import Path
from datetime import datetime

MINI_APPS_DIR = Path(r"C:\ARAGORN\aragorn_quiz\mini_apps\cfe")
LOG_FILE      = Path(r"C:\ARAGORN\aragorn_quiz\patch_quiz2_unlock_log.txt")

# ── PATCH 1: função unlocked() ────────────────────────────────────────────────
OLD_UNLOCKED = "function unlocked(){return best()>=70;}"

NEW_UNLOCKED = """function unlocked(){return h1.length>0;}
function q2recommended(){return best()>=80;}"""

# ── PATCH 2: updateHero — lógica do cadeado e mensagem ───────────────────────
OLD_HERO = """  var lk=g('q2lock');if(lk)lk.innerHTML=unlocked()?'':'&#128274;';
  st('q2lockprog',b>0?tr('q2best')+' '+b+'%':'');"""

NEW_HERO = """  var lk=g('q2lock');
  if(lk){
    if(unlocked()){
      lk.innerHTML='';
    } else {
      lk.innerHTML='&#128274;';
    }
  }
  if(unlocked()){
    if(q2recommended()){
      st('q2lockprog',tr('q2ready')||'✓ Pronto para avançar!');
    } else {
      st('q2lockprog',b>0?(tr('q2best')||'Melhor')+': '+b+'% · '+(tr('q2tip')||'Recomendado: 80%+'):'');
    }
  } else {
    st('q2lockprog',tr('q2tip2')||'Complete o Quiz 1 para desbloquear');
  }"""

# ── PATCH 3: showTab — permitir acesso ao quiz2 se unlocked ──────────────────
OLD_SHOWTAB = """function showTab(name){
  ['flash','quiz1','quiz2','score'].forEach(function(t){
    g('tab-'+t).style.display=t===name?'block':'none';
    var b=g('tbn-'+t);if(b)b.classList.toggle('active',t===name);
  });
  if(name==='quiz1'&&!Q1.qs.length)startQ(1);
  if(name==='quiz2'){if(!unlocked())return;if(!Q2.qs.length)startQ(2);}
  if(name==='score')renderScore();
}"""

NEW_SHOWTAB = """function showTab(name){
  ['flash','quiz1','quiz2','score'].forEach(function(t){
    g('tab-'+t).style.display=t===name?'block':'none';
    var b=g('tbn-'+t);if(b)b.classList.toggle('active',t===name);
  });
  if(name==='quiz1'&&!Q1.qs.length)startQ(1);
  if(name==='quiz2'){
    if(!unlocked()){
      // Mostra mensagem amigável em vez de ignorar o clique
      showTab('quiz1');
      var tip=g('q2lockprog');
      if(tip){tip.style.color='var(--amber)';tip.style.fontWeight='600';}
      return;
    }
    if(!Q2.qs.length)startQ(2);
  }
  if(name==='score')renderScore();
}"""

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def patch_file(path: Path, dry_run: bool) -> str:
    content = path.read_text(encoding="utf-8")
    original = content
    changes = []

    if OLD_UNLOCKED in content:
        content = content.replace(OLD_UNLOCKED, NEW_UNLOCKED)
        changes.append("unlocked()")

    if OLD_HERO in content:
        content = content.replace(OLD_HERO, NEW_HERO)
        changes.append("updateHero()")

    if OLD_SHOWTAB in content:
        content = content.replace(OLD_SHOWTAB, NEW_SHOWTAB)
        changes.append("showTab()")

    if not changes:
        return "SKIP — nenhum padrão encontrado"

    if content == original:
        return "SKIP — sem alterações"

    if not dry_run:
        path.write_text(content, encoding="utf-8")
        return f"OK — patches: {', '.join(changes)}"
    else:
        return f"DRY — patches: {', '.join(changes)}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--executar", action="store_true")
    parser.add_argument("--domain", default=None)
    args = parser.parse_args()
    dry_run = not args.executar

    log("=" * 64)
    log(f"NEXOR · patch_quiz2_unlock · {'DRY-RUN' if dry_run else 'EXECUTANDO'}")
    log("=" * 64)

    domains = sorted(MINI_APPS_DIR.iterdir())
    if args.domain:
        domains = [d for d in domains if d.name == args.domain]

    ok = skip = err = 0
    for domain_dir in domains:
        html = domain_dir / "index.html"
        if not html.exists():
            continue
        try:
            result = patch_file(html, dry_run)
            if result.startswith("OK"):
                ok += 1
                log(f"  ✅ {domain_dir.name} — {result}")
            elif result.startswith("DRY"):
                ok += 1
                log(f"  [DRY] {domain_dir.name} — {result}")
            else:
                skip += 1
                log(f"  ⚠  {domain_dir.name} — {result}")
        except Exception as e:
            err += 1
            log(f"  ✗  {domain_dir.name} — ERRO: {e}")

    log(f"\n{'='*64}")
    log(f"CONCLUÍDO — OK: {ok} · Skip: {skip} · Erros: {err}")
    log("=" * 64)

if __name__ == "__main__":
    main()
