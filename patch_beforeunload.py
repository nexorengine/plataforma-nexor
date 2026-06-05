"""
patch_beforeunload.py — Adiciona limpeza beforeunload nos mini-apps
Corrige travamento ao navegar entre domínios (TTS + timers)
"""
from pathlib import Path

MINI_APPS_DIR = Path(r"C:\ARAGORN\aragorn_quiz\mini_apps\cfe")

OLD = "g('btn-back').onclick=function(){window.location.href='/cfe/index.html';};"

NEW = """g('btn-back').onclick=function(){
  ttsStop();
  clearInterval(Q1.tint);clearInterval(Q2.tint);
  if(window.speechSynthesis)window.speechSynthesis.cancel();
  window.location.href='/cfe/index.html';
};
window.addEventListener('beforeunload',function(){
  ttsStop();
  clearInterval(Q1.tint);clearInterval(Q2.tint);
  if(window.speechSynthesis)window.speechSynthesis.cancel();
});"""

ok = skip = err = 0
for domain_dir in sorted(MINI_APPS_DIR.iterdir()):
    html = domain_dir / "index.html"
    if not html.exists():
        continue
    try:
        c = html.read_text(encoding="utf-8")
        if "beforeunload" in c:
            skip += 1
            continue
        if OLD in c:
            c = c.replace(OLD, NEW)
            html.write_text(c, encoding="utf-8")
            ok += 1
        else:
            skip += 1
    except Exception as e:
        err += 1
        print(f"  ✗ {domain_dir.name} — {e}")

print(f"OK: {ok} · Skip: {skip} · Erros: {err}")
