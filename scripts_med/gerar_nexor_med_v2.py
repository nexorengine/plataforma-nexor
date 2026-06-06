"""
gerar_nexor_med_v2.py
NEXOR MED — 3 Camadas com badges, botões voltar corrigidos, sem emojis
"""
import json, os

BASE      = r"C:\ARAGORN\aragorn_quiz\static"
QUIZ_DIR  = rf"{BASE}\quizzes\med\cirurgia_geral"
FLASH_DIR = rf"{BASE}\flashcards\med\cirurgia_geral"
MINI_BASE = rf"{BASE}\mini_apps\med\cirurgia_geral"
DASH_DIR  = rf"{BASE}\med\cirurgia_geral"
BADGE_CG  = "../../badges/med/cirurgia_geral"   # relativo ao mini_app
BADGE_AR  = "badges/med/areas"                   # relativo ao static root

DOMINIOS = [
    {"id":"d1","key":"abdome_agudo",    "name":"Abdome Agudo",                 "code":"D01","color":"#8b1a1a",
     "badge":"D01_ABDOME_AGUDO.png",
     "flash":"flashcards_pt.json",    "q1":"quiz_001_pt.json",    "q2":"quiz_002_pt.json"},
    {"id":"d2","key":"hepatobiliar",    "name":"Hepatobiliar e Pâncreas",      "code":"D02","color":"#7a6010",
     "badge":"D02_HEPATOBILIARES.png",
     "flash":"flashcards_d2_pt.json","q1":"quiz_d2_001_pt.json","q2":"quiz_d2_002_pt.json"},
    {"id":"d3","key":"trauma",          "name":"Trauma",                       "code":"D03","color":"#7a3a10",
     "badge":"D03_TRAUMA.png",
     "flash":"flashcards_d3_pt.json","q1":"quiz_d3_001_pt.json","q2":"quiz_d3_002_pt.json"},
    {"id":"d4","key":"perioperatorio",  "name":"Perioperatório",               "code":"D04","color":"#10407a",
     "badge":"D04_PERIOPERATORIO.png",
     "flash":"flashcards_d4_pt.json","q1":"quiz_d4_001_pt.json","q2":"quiz_d4_002_pt.json"},
    {"id":"d5","key":"hernias",         "name":"Parede Abdominal e Hérnias",   "code":"D05","color":"#3a4a5a",
     "badge":"D05_HERNIAS.png",
     "flash":"flashcards_d5_pt.json","q1":"quiz_d5_001_pt.json","q2":"quiz_d5_002_pt.json"},
    {"id":"d6","key":"tgi_superior",    "name":"Trato Digestivo Superior",     "code":"D06","color":"#1a5a2a",
     "badge":"D06_TGI_SUPERIOR.png",
     "flash":"flashcards_d6_pt.json","q1":"quiz_d6_001_pt.json","q2":"quiz_d6_002_pt.json"},
    {"id":"d7","key":"tgi_inferior",    "name":"TGI Inferior e Coloproctologia","code":"D07","color":"#5a3a1a",
     "badge":"D07_TGI_INFERIOR.png",
     "flash":"flashcards_d7_pt.json","q1":"quiz_d7_001_pt.json","q2":"quiz_d7_002_pt.json"},
    {"id":"d8","key":"vascular",        "name":"Cirurgia Vascular",            "code":"D08","color":"#1a3a6a",
     "badge":"D08_VASCULAR.png",
     "flash":"flashcards_d8_pt.json","q1":"quiz_d8_001_pt.json","q2":"quiz_d8_002_pt.json"},
    {"id":"d9","key":"queimaduras",     "name":"Queimaduras",                  "code":"D09","color":"#7a2a1a",
     "badge":"D09_QUEIMADURAS.png",
     "flash":"flashcards_d9_pt.json","q1":"quiz_d9_001_pt.json","q2":"quiz_d9_002_pt.json"},
]

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">'

CSS_BASE = """*{box-sizing:border-box;margin:0;padding:0;}
:root{
  --bg:#07090f;--bg2:#0d1120;--bg3:#111827;
  --border:#1a2a45;--border2:#243550;
  --blue:#4a8fd4;--green:#27ae60;--red:#c0392b;--amber:#d4a017;
  --text:#c8d6e8;--text2:#7a9bbf;--text3:#3a5575;
  --med:#8b1a1a;--med2:#a52020;
}
body{font-family:'Inter',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;}
.app{max-width:900px;margin:0 auto;padding:0 1rem 3rem;}
.hdr{display:flex;align-items:center;gap:10px;padding:1rem 0;border-bottom:1px solid var(--border);margin-bottom:1.5rem;}
.hdr-logo{font-size:14px;font-weight:700;letter-spacing:2px;color:#e8f0fa;}
.hdr-logo span{color:var(--med2);}
.hdr-title{font-size:10px;color:var(--text2);letter-spacing:1px;flex:1;}
.hdr-back{background:none;border:1px solid var(--border);border-radius:4px;padding:4px 12px;cursor:pointer;font-family:'Inter',sans-serif;font-size:9px;color:var(--text3);letter-spacing:1px;transition:all .15s;text-decoration:none;display:inline-block;}
.hdr-back:hover{border-color:var(--blue);color:var(--blue);}
.btn{background:var(--bg2);border:1px solid var(--border);border-radius:6px;padding:8px 18px;cursor:pointer;font-family:'Inter',sans-serif;font-size:11px;color:var(--text2);transition:all .15s;text-decoration:none;display:inline-block;}
.btn:hover{border-color:var(--blue);color:var(--blue);}
.btn.primary{background:var(--med);border-color:var(--med2);color:#fff;}
.btn.primary:hover{background:var(--med2);}
.slabel{font-size:9px;letter-spacing:2.5px;color:var(--text3);text-transform:uppercase;margin-bottom:12px;}"""

# ═══════════════════════════════════════════════════════════════════════════
# CAMADA 1 — PORTAL
# ═══════════════════════════════════════════════════════════════════════════
def gerar_portal():
    areas = [
        {"name":"CIRURGIA GERAL",       "sub":"9 domínios · Residência Médica","badge":"CIRURGIA_PREMIUM.png",  "link":"med/cirurgia_geral/index.html","active":True},
        {"name":"GINECO & OBSTETRÍCIA", "sub":"Em breve",                      "badge":"GINECO_PREMIUM.png",    "link":"#","active":False},
        {"name":"PEDIATRIA",            "sub":"Em breve",                      "badge":"PEDIATRIA_PREMIUM.png", "link":"#","active":False},
        {"name":"CLÍNICA MÉDICA",       "sub":"Em breve",                      "badge":"CLINICA_PREMIUM.png",   "link":"#","active":False},
        {"name":"MEDICINA PREVENTIVA",  "sub":"Em breve",                      "badge":"PREVENTIVA_PREMIUM.png","link":"#","active":False},
    ]

    cards = ""
    for a in areas:
        badge_path = f"{BADGE_AR}/{a['badge']}"
        if a["active"]:
            cards += f"""
    <a href="{a['link']}" class="area-card active">
      <img src="{badge_path}" class="area-badge-img" alt="{a['name']}">
      <div class="area-name">{a['name']}</div>
      <div class="area-sub">{a['sub']}</div>
      <div class="area-status available">DISPONÍVEL</div>
    </a>"""
        else:
            cards += f"""
    <div class="area-card soon">
      <img src="{badge_path}" class="area-badge-img soon-img" alt="{a['name']}">
      <div class="area-name muted">{a['name']}</div>
      <div class="area-sub">{a['sub']}</div>
      <div class="area-status soon-tag">EM BREVE</div>
    </div>"""

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NEXOR MED</title>
{FONTS}
<style>
{CSS_BASE}
.hero{{text-align:center;padding:2rem 0 1.5rem;}}
.hero-label{{font-size:9px;letter-spacing:3px;color:var(--med2);text-transform:uppercase;margin-bottom:10px;}}
.hero-title{{font-size:30px;font-weight:700;color:#e8f0fa;letter-spacing:1px;margin-bottom:6px;}}
.hero-title span{{color:var(--med2);}}
.hero-sub{{font-size:12px;color:var(--text2);letter-spacing:1px;margin-bottom:1.5rem;}}
.hero-tag{{display:inline-block;background:rgba(139,26,26,.15);border:1px solid rgba(165,32,32,.4);border-radius:4px;padding:4px 14px;font-size:10px;letter-spacing:2px;color:var(--med2);}}
.area-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:16px;margin:1.5rem 0;}}
.area-card{{background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:1.5rem 1rem;text-align:center;text-decoration:none;color:inherit;display:flex;flex-direction:column;align-items:center;transition:all .2s;}}
.area-card.active{{cursor:pointer;}}
.area-card.active:hover{{border-color:var(--med2);background:var(--bg3);transform:translateY(-2px);box-shadow:0 8px 24px rgba(0,0,0,.4);}}
.area-card.soon{{cursor:default;}}
.area-badge-img{{width:80px;height:80px;object-fit:contain;margin-bottom:12px;}}
.soon-img{{opacity:.45;filter:grayscale(40%);}}
.area-name{{font-size:12px;font-weight:700;color:#e8f0fa;margin-bottom:4px;letter-spacing:.3px;}}
.area-name.muted{{color:var(--text3);}}
.area-sub{{font-size:10px;color:var(--text3);margin-bottom:10px;}}
.area-status{{display:inline-block;border:1px solid;border-radius:3px;padding:2px 8px;font-size:8px;letter-spacing:1.5px;font-weight:600;}}
.available{{border-color:var(--med2);color:var(--med2);background:rgba(165,32,32,.1);}}
.soon-tag{{border-color:var(--border2);color:var(--text3);}}
.footer{{text-align:center;padding:2rem 0;border-top:1px solid var(--border);margin-top:1rem;}}
.footer-text{{font-size:9px;color:var(--text3);letter-spacing:1.5px;}}
</style>
</head>
<body>
<div class="app">
  <div class="hdr">
    <div class="hdr-logo">nexor_<span>MED</span></div>
    <div class="hdr-title">Certification Readiness Engine · Powered by FractalLearning™</div>
    <a href="index.html" class="hdr-back">← NEXOR CERTIFIED</a>
  </div>
  <div class="hero">
    <div class="hero-label">NEXOR MED · BETA</div>
    <div class="hero-title">Residência <span>Médica</span></div>
    <div class="hero-sub">Prepare-se com a metodologia FractalLearning™</div>
    <div class="hero-tag">PROTOTYPE · PT ONLY</div>
  </div>
  <div class="slabel">Selecione sua área</div>
  <div class="area-grid">{cards}</div>
  <div class="footer"><div class="footer-text">NEXOR MED · nexorengine.com · FractalLearning™</div></div>
</div>
</body>
</html>"""

# ═══════════════════════════════════════════════════════════════════════════
# CAMADA 2 — DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════
def gerar_dashboard():
    rows = ""
    for d in DOMINIOS:
        badge_path = f"../../badges/med/cirurgia_geral/{d['badge']}"
        rows += f"""
    <a href="../../mini_apps/med/cirurgia_geral/{d['key']}/index.html" class="domain-row">
      <div class="domain-row-left">
        <img src="{badge_path}" class="domain-badge-img" alt="{d['name']}">
        <div>
          <div class="domain-row-name">{d['name']}</div>
          <div class="domain-row-meta">{d['code']} · 48 flashcards · 2 quizzes · 100 questões</div>
        </div>
      </div>
      <div class="domain-row-right">
        <div class="domain-progress" id="prog-{d['key']}">—</div>
        <div class="domain-arrow">→</div>
      </div>
    </a>"""

    progress_js = ""
    for d in DOMINIOS:
        progress_js += f"""
  try{{
    const q1=localStorage.getItem('nx_med_{d['key']}_q1');
    const q2=localStorage.getItem('nx_med_{d['key']}_q2');
    const el=document.getElementById('prog-{d['key']}');
    if(el&&q1){{
      const d1=JSON.parse(q1);
      const p=q2?Math.round((d1.correct/d1.total+JSON.parse(q2).correct/JSON.parse(q2).total)/2*100):Math.round(d1.correct/d1.total*100);
      el.textContent=p+'%';el.style.color=p>=80?'#27ae60':p>=60?'#d4a017':'#c0392b';
    }}
  }}catch(e){{}}"""

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NEXOR MED — Cirurgia Geral</title>
{FONTS}
<style>
{CSS_BASE}
.cert-header{{display:flex;align-items:center;gap:16px;margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:1px solid var(--border);}}
.cert-badge-img{{width:72px;height:72px;object-fit:contain;}}
.cert-title{{font-size:20px;font-weight:700;color:#e8f0fa;}}
.cert-meta{{font-size:10px;color:var(--text3);margin-top:2px;letter-spacing:1px;}}
.cert-tag{{display:inline-block;margin-top:6px;background:rgba(139,26,26,.15);border:1px solid rgba(165,32,32,.4);border-radius:3px;padding:2px 8px;font-size:9px;letter-spacing:1.5px;color:var(--med2);}}
.stats-bar{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:1.5rem;}}
.stat-box{{background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:.9rem;text-align:center;}}
.stat-num{{font-size:22px;font-weight:700;color:#e8f0fa;}}
.stat-lbl{{font-size:9px;color:var(--text3);letter-spacing:1px;text-transform:uppercase;margin-top:2px;}}
.domain-row{{background:var(--bg2);border:1px solid var(--border);border-radius:10px;padding:1rem 1.2rem;cursor:pointer;transition:all .2s;display:flex;align-items:center;justify-content:space-between;text-decoration:none;color:inherit;margin-bottom:10px;}}
.domain-row:hover{{border-color:var(--med2);background:var(--bg3);}}
.domain-row-left{{display:flex;align-items:center;gap:14px;}}
.domain-badge-img{{width:44px;height:44px;object-fit:contain;}}
.domain-row-name{{font-size:13px;color:#e8f0fa;font-weight:500;margin-bottom:3px;}}
.domain-row-meta{{font-size:10px;color:var(--text3);}}
.domain-row-right{{display:flex;align-items:center;gap:12px;}}
.domain-progress{{font-size:13px;font-weight:600;color:var(--text3);}}
.domain-arrow{{font-size:14px;color:var(--text3);}}
</style>
</head>
<body>
<div class="app">
  <div class="hdr">
    <div class="hdr-logo">nexor_<span style="color:var(--med2)">MED</span></div>
    <div class="hdr-title">CIRURGIA GERAL · RESIDÊNCIA MÉDICA</div>
    <a href="../../index_med.html" class="hdr-back">← Áreas</a>
  </div>
  <div class="cert-header">
    <img src="../../badges/med/cirurgia_geral/CIRURGIA_PREMIUM.png" class="cert-badge-img" alt="Cirurgia Geral">
    <div>
      <div class="cert-title">Cirurgia Geral</div>
      <div class="cert-meta">ACM/SC · AMRIGS · ENARE · Provas Unificadas</div>
      <div class="cert-tag">9 DOMÍNIOS · PT ONLY · BETA</div>
    </div>
  </div>
  <div class="stats-bar">
    <div class="stat-box"><div class="stat-num">9</div><div class="stat-lbl">Domínios</div></div>
    <div class="stat-box"><div class="stat-num">432</div><div class="stat-lbl">Flashcards</div></div>
    <div class="stat-box"><div class="stat-num">900</div><div class="stat-lbl">Questões</div></div>
  </div>
  <div class="slabel">Domínios</div>
{rows}
</div>
<script>{progress_js}
var _ttsOn=false,_ttsBtn=null;
function ttsStop(){{if(window.speechSynthesis)window.speechSynthesis.cancel();_ttsOn=false;if(_ttsBtn){{_ttsBtn.innerHTML='&#128266;';_ttsBtn.classList.remove('playing');}}_ttsBtn=null;}}
function ttsTxt(txt,btn){{if(_ttsOn){{ttsStop();return;}}if(!window.speechSynthesis||!txt)return;try{{_ttsOn=true;_ttsBtn=btn||null;if(btn){{btn.innerHTML='&#9209;';btn.classList.add('playing');}}var u=new SpeechSynthesisUtterance(txt);u.lang='pt-BR';u.onend=u.onerror=function(){{ttsStop();}};window.speechSynthesis.speak(u);}}catch(e){{ttsStop();}}}}
function ttsQ(btn){{var qq=document.getElementById('qq');var qo=document.getElementById('qo');if(!qq)return;var txt=qq.textContent+'. '+Array.from(qo.querySelectorAll('.opt-text')).map(function(o){{return o.textContent;}}).join('. ');ttsTxt(txt,btn);}}
function ttsFc(btn){{var front=document.getElementById('fc-front-text');var back=document.getElementById('fc-back-text');var txt=(front&&back)?front.textContent+'. '+back.textContent:(front?front.textContent:'');ttsTxt(txt,btn);}}

</script>
</body>
</html>"""

# ═══════════════════════════════════════════════════════════════════════════
# CAMADA 3 — MINI-APP
# ═══════════════════════════════════════════════════════════════════════════
def load_json(path):
    if not os.path.exists(path):
        print(f"    AVISO: {path}")
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def gerar_miniapp(d):
    flash_data = load_json(os.path.join(FLASH_DIR, d["flash"]))
    q1_data    = load_json(os.path.join(QUIZ_DIR,  d["q1"]))
    q2_data    = load_json(os.path.join(QUIZ_DIR,  d["q2"]))
    flash_json = json.dumps(flash_data["flashcards"] if flash_data else [], ensure_ascii=False)
    q1_json    = json.dumps(q1_data["questions"]    if q1_data    else [], ensure_ascii=False)
    q2_json    = json.dumps(q2_data["questions"]    if q2_data    else [], ensure_ascii=False)

    name  = d["name"]
    code  = d["code"]
    key   = d["key"]
    color = d["color"]
    badge_path = f"{BADGE_CG}/{d['badge']}"

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NEXOR MED — {name}</title>
{FONTS}
<style>
{CSS_BASE}
:root{{--accent:{color};--accent2:{color}dd;}}
.screen{{display:none;}}.screen.active{{display:block;}}
.domain-header{{display:flex;align-items:center;gap:14px;margin-bottom:1.5rem;}}
.domain-badge-img{{width:56px;height:56px;object-fit:contain;}}
.domain-title{{font-size:18px;font-weight:700;color:#e8f0fa;}}
.domain-sub{{font-size:10px;color:var(--text3);letter-spacing:1px;margin-top:2px;}}
.menu-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:1.5rem;}}
.menu-card{{background:var(--bg2);border:1px solid var(--border);border-radius:10px;padding:1.3rem;cursor:pointer;transition:all .2s;}}
.menu-card:hover{{border-color:var(--accent2);background:var(--bg3);}}
.menu-card-title{{font-size:13px;font-weight:600;color:#e8f0fa;margin-bottom:4px;}}
.menu-card-meta{{font-size:10px;color:var(--text3);}}
.menu-card-badge{{display:inline-block;margin-top:8px;background:rgba(139,26,26,.12);border:1px solid rgba(165,32,32,.3);border-radius:3px;padding:2px 8px;font-size:9px;letter-spacing:1px;color:var(--med2);}}
.fc-progress{{font-size:10px;color:var(--text3);letter-spacing:1px;margin-bottom:.8rem;text-align:center;}}
.fc-layer-badge{{display:inline-block;padding:3px 10px;border-radius:3px;font-size:9px;letter-spacing:1.5px;font-weight:600;margin-bottom:.8rem;}}
.lF1{{background:rgba(74,143,212,.15);border:1px solid rgba(74,143,212,.4);color:#4a8fd4;}}
.lF2{{background:rgba(39,174,96,.15);border:1px solid rgba(39,174,96,.4);color:#27ae60;}}
.lF3{{background:rgba(212,160,23,.15);border:1px solid rgba(212,160,23,.4);color:#d4a017;}}
.lF4{{background:rgba(192,57,43,.15);border:1px solid rgba(192,57,43,.4);color:#c0392b;}}
.fc-card{{background:var(--bg2);border:1px solid var(--border2);border-radius:12px;padding:2rem 1.5rem;min-height:190px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;cursor:pointer;transition:all .3s;margin-bottom:.8rem;}}
.fc-card.flipped{{background:var(--bg3);border-color:var(--accent2);}}
.fc-side{{font-size:8px;letter-spacing:2px;color:var(--text3);text-transform:uppercase;margin-bottom:10px;}}
.fc-text{{font-size:15px;color:#e8f0fa;line-height:1.6;}}
.fc-hint{{font-size:10px;color:var(--text3);margin-top:12px;}}
.fc-nav{{display:flex;gap:8px;justify-content:center;margin-bottom:.8rem;flex-wrap:wrap;}}
.fc-btn{{background:var(--bg2);border:1px solid var(--border);border-radius:6px;padding:7px 16px;cursor:pointer;font-family:'Inter',sans-serif;font-size:11px;color:var(--text2);transition:all .15s;}}
.fc-btn:hover{{border-color:var(--blue);color:var(--blue);}}
.fc-btn.primary{{background:var(--med);border-color:var(--med2);color:#fff;}}
.fc-btn.primary:hover{{background:var(--med2);}}
.quiz-header{{display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem;}}
.quiz-prog{{font-size:10px;color:var(--text3);letter-spacing:1px;}}
.quiz-diff{{font-size:9px;padding:2px 8px;border-radius:3px;font-weight:600;letter-spacing:1px;}}
.dEASY{{background:rgba(39,174,96,.15);border:1px solid rgba(39,174,96,.3);color:#27ae60;}}
.dSTANDARD{{background:rgba(74,143,212,.15);border:1px solid rgba(74,143,212,.3);color:#4a8fd4;}}
.dHARD{{background:rgba(192,57,43,.15);border:1px solid rgba(192,57,43,.3);color:#c0392b;}}
.quiz-tag{{font-size:9px;color:var(--text3);letter-spacing:1px;margin-bottom:8px;text-transform:uppercase;}}
.quiz-q{{background:var(--bg2);border:1px solid var(--border2);border-radius:10px;padding:1.3rem;margin-bottom:.8rem;font-size:14px;color:#e8f0fa;line-height:1.7;}}
.quiz-opts{{display:flex;flex-direction:column;gap:8px;margin-bottom:.8rem;}}
.quiz-opt{{background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:11px 15px;cursor:pointer;font-size:13px;color:var(--text);transition:all .15s;text-align:left;font-family:'Inter',sans-serif;}}
.quiz-opt:hover:not([disabled]){{border-color:var(--blue);background:var(--bg3);}}
.quiz-opt.correct{{border-color:var(--green)!important;background:rgba(39,174,96,.1)!important;color:#27ae60!important;}}
.quiz-opt.wrong{{border-color:var(--red)!important;background:rgba(192,57,43,.1)!important;color:#c0392b!important;}}
.quiz-opt.reveal{{border-color:var(--green)!important;background:rgba(39,174,96,.05)!important;}}
.quiz-feedback{{background:var(--bg3);border:1px solid var(--border2);border-radius:8px;padding:1rem;margin-bottom:.8rem;font-size:12px;line-height:1.6;display:none;}}
.quiz-feedback.show{{display:block;}}
.fb-correct{{color:var(--green);font-weight:600;margin-bottom:4px;}}
.fb-wrong{{color:var(--text2);font-size:11px;}}
.quiz-next{{background:var(--med);border:1px solid var(--med2);border-radius:6px;padding:9px 22px;cursor:pointer;font-family:'Inter',sans-serif;font-size:12px;color:#fff;transition:all .15s;display:none;}}
.quiz-next.show{{display:inline-block;}}
.quiz-next:hover{{background:var(--med2);}}
.quiz-exit{{background:none;border:1px solid var(--border);border-radius:6px;padding:9px 16px;cursor:pointer;font-family:'Inter',sans-serif;font-size:11px;color:var(--text3);transition:all .15s;margin-left:8px;display:none;}}
.quiz-exit.show{{display:inline-block;}}
.quiz-exit:hover{{border-color:var(--blue);color:var(--blue);}}
.sc-box{{background:var(--bg2);border:1px solid var(--border2);border-radius:12px;padding:1.5rem;margin-bottom:1rem;}}
.sc-title{{font-size:11px;letter-spacing:2px;color:var(--text3);text-transform:uppercase;margin-bottom:1rem;}}
.sc-score{{font-size:40px;font-weight:700;color:#e8f0fa;margin-bottom:4px;}}
.sc-level{{display:inline-block;padding:4px 12px;border-radius:4px;font-size:10px;letter-spacing:2px;font-weight:600;margin-bottom:1rem;}}
.sc-level.ready{{background:rgba(39,174,96,.15);border:1px solid rgba(39,174,96,.4);color:#27ae60;}}
.sc-level.progress{{background:rgba(212,160,23,.15);border:1px solid rgba(212,160,23,.4);color:#d4a017;}}
.sc-level.training{{background:rgba(192,57,43,.15);border:1px solid rgba(192,57,43,.4);color:#c0392b;}}
.sc-bars{{margin:.8rem 0;}}
.sc-bar-row{{display:flex;align-items:center;gap:10px;margin-bottom:7px;}}
.sc-bar-lbl{{font-size:9px;color:var(--text3);letter-spacing:1px;width:60px;}}
.sc-bar-track{{flex:1;height:5px;background:var(--bg3);border-radius:3px;overflow:hidden;}}
.sc-bar-fill{{height:100%;border-radius:3px;transition:width .8s ease;}}
.feasy{{background:var(--green);}}.fstd{{background:var(--blue);}}.fhard{{background:var(--red);}}
.sc-bar-pct{{font-size:10px;color:var(--text2);width:32px;text-align:right;}}
.sc-msg{{font-size:12px;color:var(--text2);line-height:1.7;padding:1rem;background:var(--bg3);border-radius:8px;border-left:3px solid var(--med2);}}
.btn-row{{display:flex;gap:8px;flex-wrap:wrap;margin-top:1rem;}}
.qsel-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:1.5rem;}}
.qsel-card{{background:var(--bg2);border:1px solid var(--border);border-radius:10px;padding:1.3rem;cursor:pointer;transition:all .2s;position:relative;}}
.qsel-card:hover{{border-color:var(--accent2);background:var(--bg3);}}
.qsel-num{{font-size:28px;font-weight:700;color:var(--accent2);margin-bottom:6px;}}
.qsel-lbl{{font-size:12px;color:#e8f0fa;margin-bottom:3px;}}
.qsel-meta{{font-size:10px;color:var(--text3);}}
.saved-tag{{position:absolute;top:8px;right:8px;font-size:8px;letter-spacing:1px;color:var(--green);background:rgba(39,174,96,.1);border:1px solid rgba(39,174,96,.3);border-radius:2px;padding:1px 5px;display:none;}}
</style>
</head>
<body>
<div class="app">
<div class="hdr">
  <div class="hdr-logo">nexor_<span style="color:var(--med2)">MED</span></div>
  <div class="hdr-title">CIRURGIA GERAL · {code}</div>
  <a href="../../index.html" class="hdr-back" id="hdr-back-btn">← Domínios</a>
</div>

<!-- MENU -->
<div id="s-menu" class="screen active">
  <div class="domain-header">
    <img src="{badge_path}" class="domain-badge-img" alt="{name}">
    <div>
      <div class="domain-title">{name}</div>
      <div class="domain-sub">CIRURGIA GERAL · {code} · NEXOR MED</div>
    </div>
  </div>
  <div class="menu-grid">
    <div class="menu-card" onclick="startFlashcards()">
      <div class="menu-card-title">FractalFlashcards</div>
      <div class="menu-card-meta">48 cards · 4 camadas cognitivas</div>
      <div class="menu-card-badge">F1 · F2 · F3 · F4</div>
    </div>
    <div class="menu-card" onclick="showQSel()">
      <div class="menu-card-title">FractalQuiz</div>
      <div class="menu-card-meta">2 quizzes · 50 questões cada</div>
      <div class="menu-card-badge">EASY · STANDARD · HARD</div>
    </div>
  </div>
</div>

<!-- QUIZ SELECT -->
<div id="s-qsel" class="screen">
  <div class="domain-title" style="margin-bottom:4px">Selecionar Quiz</div>
  <div class="domain-sub" style="margin-bottom:1.5rem">{name}</div>
  <div class="qsel-grid">
    <div class="qsel-card" onclick="startQuiz(0)">
      <div class="saved-tag" id="sv1">SALVO</div>
      <div class="qsel-num">01</div>
      <div class="qsel-lbl">Quiz 001</div>
      <div class="qsel-meta">50 questões · FractalQuiz</div>
    </div>
    <div class="qsel-card" onclick="startQuiz(1)">
      <div class="saved-tag" id="sv2">SALVO</div>
      <div class="qsel-num">02</div>
      <div class="qsel-lbl">Quiz 002</div>
      <div class="qsel-meta">50 questões · Zero repeat</div>
    </div>
  </div>
  <button class="btn" onclick="show('s-menu')">← Voltar</button>
</div>

<!-- FLASHCARDS -->
<div id="s-fc" class="screen">
  <div class="fc-progress" id="fc-prog"></div>
  <div style="text-align:center"><span class="fc-layer-badge" id="fc-lb"></span></div>
  <div class="fc-card" id="fc-card" onclick="flipCard()">
    <div class="fc-side" id="fc-side">FRENTE</div>
    <div class="fc-text" id="fc-text"></div>
    <div class="fc-hint" id="fc-hint">Toque para revelar</div>
  </div>
  <div class="fc-nav">
    <button class="fc-btn" onclick="fcNav(-1)">← Anterior</button>
    <button class="fc-btn" onclick="flipCard()">Virar</button>
    <button class="fc-btn" onclick="fcNav(1)">Próximo →</button>
  </div>
  <div style="text-align:center;margin-top:.5rem">
    <button class="fc-btn primary" onclick="show('s-menu')">← Menu</button>
  </div>
</div>

<!-- QUIZ -->
<div id="s-quiz" class="screen">
  <div class="quiz-header">
    <div class="quiz-prog" id="qp"></div>
    <div class="quiz-diff" id="qd"></div>
  </div>
  <div class="quiz-tag" id="qt"></div>
  <div style="display:flex;align-items:center;gap:6px;"><div class="quiz-q" id="qq" style="flex:1"></div><button class="tts-btn" onclick="ttsQ(this)" title="Ouvir pergunta">&#128266;</button></div>
  <div class="quiz-opts" id="qo"></div>
  <div class="quiz-feedback" id="qf">
    <div style="display:flex;align-items:center;gap:6px;"><div class="fb-correct" id="fbc" style="flex:1"></div><button class="tts-btn" onclick="ttsTxt(document.getElementById('fbc').textContent,this)" title="Ouvir justificativa">&#128266;</button></div>
    <div style="display:flex;align-items:center;gap:6px;"><div class="fb-wrong" id="fbw" style="flex:1"></div><button class="tts-btn" onclick="ttsTxt(document.getElementById('fbw').textContent,this)" title="Ouvir distractors">&#128266;</button></div>
  </div>
  <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
    <button class="quiz-next" id="qn" onclick="nextQ()">Próxima →</button>
    <button class="quiz-exit" id="qe" onclick="show('s-qsel')">Sair do Quiz</button>
  </div>
</div>

<!-- SCORECARD -->
<div id="s-sc" class="screen">
  <div class="sc-box">
    <div class="sc-title">RESULTADO · {code}</div>
    <div class="sc-score" id="sc-score"></div>
    <div class="sc-level" id="sc-lv"></div>
    <div class="sc-bars">
      <div class="sc-bar-row"><div class="sc-bar-lbl">EASY</div><div class="sc-bar-track"><div class="sc-bar-fill feasy" id="b-easy" style="width:0%"></div></div><div class="sc-bar-pct" id="p-easy">0%</div></div>
      <div class="sc-bar-row"><div class="sc-bar-lbl">STANDARD</div><div class="sc-bar-track"><div class="sc-bar-fill fstd" id="b-std" style="width:0%"></div></div><div class="sc-bar-pct" id="p-std">0%</div></div>
      <div class="sc-bar-row"><div class="sc-bar-lbl">HARD</div><div class="sc-bar-track"><div class="sc-bar-fill fhard" id="b-hard" style="width:0%"></div></div><div class="sc-bar-pct" id="p-hard">0%</div></div>
    </div>
    <div class="sc-msg" id="sc-msg"></div>
  </div>
  <div class="btn-row">
    <button class="btn primary" onclick="startQuiz(curQ)">Refazer</button>
    <button class="btn" onclick="show('s-qsel')">Outro Quiz</button>
    <button class="btn" onclick="show('s-menu')">Menu</button>
    <a href="../../index.html" class="btn">← Domínios</a>
  </div>
</div>

</div>
<script>
const FC={flash_json};
const QZ=[{q1_json},{q2_json}];
const DK='{key}';

let fi=0,ff=false;
let qi=0,qdata=[],qans=[],qok=0,curQ=0;

function show(id){{
  document.querySelectorAll('.screen').forEach(s=>s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  // Atualiza botão voltar do header
  const hb=document.getElementById('hdr-back-btn');
  if(id==='s-menu'){{hb.href='../../index.html';hb.textContent='← Domínios';}}
  else if(id==='s-fc'||id==='s-qsel'){{hb.href='javascript:void(0)';hb.onclick=()=>show('s-menu');hb.textContent='← Menu';}}
  else if(id==='s-quiz'){{hb.href='javascript:void(0)';hb.onclick=()=>show('s-qsel');hb.textContent='← Quizzes';}}
  else if(id==='s-sc'){{hb.href='javascript:void(0)';hb.onclick=()=>show('s-menu');hb.textContent='← Menu';}}
}}

// FLASHCARDS
function startFlashcards(){{fi=0;ff=false;show('s-fc');renderFC();}}
function renderFC(){{
  const c=FC[fi];if(!c)return;ff=false;
  const ln={{F1:'F1 · Definição',F2:'F2 · Distinção',F3:'F3 · Aplicação',F4:'F4 · Síntese'}};
  const lc={{F1:'lF1',F2:'lF2',F3:'lF3',F4:'lF4'}};
  document.getElementById('fc-prog').textContent=(fi+1)+' / '+FC.length+' · '+c.camada;
  const lb=document.getElementById('fc-lb');lb.textContent=ln[c.camada]||c.camada;lb.className='fc-layer-badge '+(lc[c.camada]||'');
  document.getElementById('fc-side').textContent='FRENTE';
  document.getElementById('fc-text').textContent=c.frente;
  document.getElementById('fc-hint').textContent='Toque para revelar';
  document.getElementById('fc-card').classList.remove('flipped');
}}
function flipCard(){{
  const c=FC[fi];if(!c)return;
  if(!ff){{ff=true;document.getElementById('fc-side').textContent='VERSO';document.getElementById('fc-text').textContent=c.verso;document.getElementById('fc-hint').textContent='';document.getElementById('fc-card').classList.add('flipped');}}
  else{{ff=false;renderFC();}}
}}
function fcNav(d){{fi=Math.max(0,Math.min(FC.length-1,fi+d));renderFC();}}

// QUIZ
function showQSel(){{
  try{{if(localStorage.getItem('nx_med_'+DK+'_q1'))document.getElementById('sv1').style.display='block';}}catch(e){{}}
  try{{if(localStorage.getItem('nx_med_'+DK+'_q2'))document.getElementById('sv2').style.display='block';}}catch(e){{}}
  show('s-qsel');
}}
function startQuiz(idx){{
  curQ=idx;qdata=QZ[idx];qi=0;qok=0;
  qans=new Array(qdata.length).fill(null);
  show('s-quiz');renderQ();
}}
function renderQ(){{
  const q=qdata[qi];if(!q)return;
  document.getElementById('qp').textContent=(qi+1)+' / '+qdata.length;
  const dd=document.getElementById('qd');dd.textContent=q.difficulty||'';dd.className='quiz-diff d'+(q.difficulty||'STANDARD');
  document.getElementById('qt').textContent=(q.tag||'').replace(/_/g,' ').toUpperCase();
  document.getElementById('qq').textContent=q.text||q.enunciado||'';
  const oo=document.getElementById('qo');oo.innerHTML='';
  (q.options||[]).forEach((o,i)=>{{
    const b=document.createElement('button');b.className='quiz-opt';b.textContent=o;
    b.onclick=()=>ans(i+1,b,q);oo.appendChild(b);
  }});
  document.getElementById('qf').classList.remove('show');
  document.getElementById('qn').classList.remove('show');
  document.getElementById('qe').classList.remove('show');
}}
function ans(ch,btn,q){{
  document.querySelectorAll('.quiz-opt').forEach(o=>o.disabled=true);
  const ok=ch===q.correct;if(ok)qok++;qans[qi]=ch;
  document.querySelectorAll('.quiz-opt').forEach((o,i)=>{{
    if(i+1===q.correct)o.classList.add(ok?'correct':'reveal');
    else if(i+1===ch&&!ok)o.classList.add('wrong');
  }});
  document.getElementById('fbc').textContent=(ok?'✓ Correto! ':'✗ Incorreto. ')+(q.justification_correct||'');
  const jw=q.justification_wrong;document.getElementById('fbw').textContent=jw?(typeof jw==='object'?Object.entries(jw).map(([k,v])=>k+': '+v).join(' | '):jw):'';
  document.getElementById('qf').classList.add('show');
  document.getElementById('qn').classList.add('show');
  document.getElementById('qe').classList.add('show');
}}
function nextQ(){{
  if(qi<qdata.length-1){{qi++;renderQ();}}
  else{{saveResult();showSC();}}
}}
function saveResult(){{
  try{{localStorage.setItem('nx_med_'+DK+'_q'+(curQ+1),JSON.stringify({{correct:qok,total:qdata.length,answers:qans,ts:Date.now()}}));}}catch(e){{}}
}}
function showSC(){{
  show('s-sc');
  const tot=qdata.length,pct=Math.round(qok/tot*100);
  const bl={{EASY:{{ok:0,t:0}},STANDARD:{{ok:0,t:0}},HARD:{{ok:0,t:0}}}};
  qdata.forEach((q,i)=>{{const lv=q.difficulty||'STANDARD';if(bl[lv]){{bl[lv].t++;if(qans[i]===q.correct)bl[lv].ok++;}}}});
  const ep=bl.EASY.t>0?Math.round(bl.EASY.ok/bl.EASY.t*100):pct;
  const sp=bl.STANDARD.t>0?Math.round(bl.STANDARD.ok/bl.STANDARD.t*100):pct;
  const hp=bl.HARD.t>0?Math.round(bl.HARD.ok/bl.HARD.t*100):Math.max(0,pct-15);
  let lc,lt;
  if(pct>=80){{lc='ready';lt='EXAM READY';}}
  else if(pct>=60){{lc='progress';lt='IN PROGRESS';}}
  else{{lc='training';lt='TRAINING';}}
  let msg='';
  if(pct>=80)msg='<strong>Excelente domínio de {name}.</strong> Desempenho no nível dos aprovados.'+(hp<70?' Atenção extra nas questões Hard.':' Continue mantendo esse ritmo.');
  else if(pct>=60)msg='<strong>Progresso sólido em {name}.</strong> Você domina os fundamentos.'+(sp<70?' Reforce as questões Standard.':' Foque nas Hard.');
  else msg='<strong>Continue estudando {name}.</strong> '+(ep<70?'Revise os conceitos básicos.':'Você domina o básico — aprofunde nas Standard e Hard.');
  document.getElementById('sc-score').textContent=qok+'/'+tot+' ('+pct+'%)';
  const lel=document.getElementById('sc-lv');lel.textContent=lt;lel.className='sc-level '+lc;
  setTimeout(()=>{{
    const sb=(id,pid,v)=>{{const b=document.getElementById(id),p=document.getElementById(pid);if(b)b.style.width=v+'%';if(p)p.textContent=v+'%';}};
    sb('b-easy','p-easy',ep);sb('b-std','p-std',sp);sb('b-hard','p-hard',hp);
    const m=document.getElementById('sc-msg');if(m)m.innerHTML=msg;
  }},150);
}}

var _ttsOn=false,_ttsBtn=null;
function ttsStop(){{if(window.speechSynthesis)window.speechSynthesis.cancel();_ttsOn=false;if(_ttsBtn){{_ttsBtn.innerHTML='&#128266;';_ttsBtn.classList.remove('playing');}}_ttsBtn=null;}}
function ttsTxt(txt,btn){{if(_ttsOn){{ttsStop();return;}}if(!window.speechSynthesis||!txt)return;try{{_ttsOn=true;_ttsBtn=btn||null;if(btn){{btn.innerHTML='&#9209;';btn.classList.add('playing');}}var u=new SpeechSynthesisUtterance(txt);u.lang='pt-BR';u.onend=u.onerror=function(){{ttsStop();}};window.speechSynthesis.speak(u);}}catch(e){{ttsStop();}}}}
function ttsQ(btn){{var qq=document.getElementById('qq');var qo=document.getElementById('qo');if(!qq)return;var txt=qq.textContent+'. '+Array.from(qo.querySelectorAll('.opt-text')).map(function(o){{return o.textContent;}}).join('. ');ttsTxt(txt,btn);}}
function ttsFc(btn){{var front=document.getElementById('fc-front-text');var back=document.getElementById('fc-back-text');var txt=(front&&back)?front.textContent+'. '+back.textContent:(front?front.textContent:'');ttsTxt(txt,btn);}}

</script>
</body>
</html>"""

# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════
def main():
    print("="*60)
    print("NEXOR MED v2 — 3 Camadas + Badges + Navegação Corrigida")
    print("="*60)

    # C1
    portal_path = os.path.join(BASE, "index_med.html")
    with open(portal_path, "w", encoding="utf-8") as f:
        f.write(gerar_portal())
    print(f"\n[C1] Portal → {portal_path}")

    # C2
    os.makedirs(DASH_DIR, exist_ok=True)
    dash_path = os.path.join(DASH_DIR, "index.html")
    with open(dash_path, "w", encoding="utf-8") as f:
        f.write(gerar_dashboard())
    print(f"[C2] Dashboard → {dash_path}")

    # C3
    print("[C3] Mini-apps:")
    for d in DOMINIOS:
        out_dir = os.path.join(MINI_BASE, d["key"])
        os.makedirs(out_dir, exist_ok=True)
        html = gerar_miniapp(d)
        out_path = os.path.join(out_dir, "index.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  ✓ {d['code']} {d['name']}")

    print(f"""
{'='*60}
CONCLUÍDO v2

Melhorias aplicadas:
  ✓ Badges premium nas áreas (C1)
  ✓ Badges dos domínios no dashboard (C2)
  ✓ Badge premium no topo do dashboard
  ✓ Sem emojis em nenhuma camada
  ✓ Botão voltar do header dinâmico (atualiza por tela)
  ✓ Botão "Sair do Quiz" dentro do quiz
  ✓ Botão "← Domínios" no scorecard

Teste:
  start static\\index_med.html
{'='*60}""")

if __name__ == "__main__":
    main()
