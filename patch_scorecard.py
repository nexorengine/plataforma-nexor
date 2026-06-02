"""
NEXOR -- PATCH SCORECARD v1
Injeta o sistema de Scorecard relampago na tela de resultados
do index.html existente. Nao quebra nenhuma funcionalidade atual.

USO:
    python patch_scorecard.py
"""

import shutil
from datetime import datetime

INDEX_FILE = "static/index.html"
TIMESTAMP  = datetime.now().strftime("%Y%m%d_%H%M")

# ─── CSS DO SCORECARD (injetar antes de </style>) ────────────────────────────
SCORECARD_CSS = """
/* ── NEXOR SCORECARD ─────────────────────────────────────── */
.scorecard{margin:2rem 0 1.5rem;text-align:left;}
.sc-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:1.2rem;}
.sc-title{font-size:9px;letter-spacing:2px;text-transform:uppercase;color:var(--text3);font-weight:600;}
.sc-level{display:inline-flex;align-items:center;gap:6px;padding:4px 12px;border-radius:20px;font-size:10px;font-weight:700;letter-spacing:1px;}
.sc-level.training{background:rgba(192,57,43,.1);border:1px solid rgba(192,57,43,.3);color:#e74c3c;}
.sc-level.progress{background:rgba(212,160,23,.1);border:1px solid rgba(212,160,23,.3);color:#d4a017;}
.sc-level.ready{background:rgba(39,174,96,.1);border:1px solid rgba(39,174,96,.3);color:#27ae60;}

.sc-bars{display:flex;flex-direction:column;gap:10px;margin-bottom:1.4rem;}
.sc-bar-row{display:flex;align-items:center;gap:10px;}
.sc-bar-label{font-size:9px;letter-spacing:1px;text-transform:uppercase;color:var(--text3);width:64px;flex-shrink:0;}
.sc-bar-track{flex:1;height:6px;background:var(--bg2);border-radius:3px;overflow:hidden;}
.sc-bar-fill{height:100%;border-radius:3px;transition:width .6s cubic-bezier(.4,0,.2,1);}
.sc-bar-fill.easy{background:#27ae60;}
.sc-bar-fill.standard{background:#2980b9;}
.sc-bar-fill.hard{background:#8e44ad;}
.sc-bar-pct{font-size:10px;font-weight:700;color:var(--text2);width:34px;text-align:right;flex-shrink:0;}

.sc-message{background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:12px 14px;font-size:11px;color:var(--text2);line-height:1.6;margin-bottom:1.4rem;}
.sc-message strong{color:var(--blue);}

.sc-domains{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:1.2rem;}
.sc-domain-tag{font-size:9px;padding:4px 8px;border-radius:4px;border:1px solid var(--border);color:var(--text3);text-align:center;letter-spacing:.5px;}
.sc-domain-tag.strong{border-color:rgba(39,174,96,.4);color:#27ae60;background:rgba(39,174,96,.06);}
.sc-domain-tag.weak{border-color:rgba(192,57,43,.4);color:#e74c3c;background:rgba(192,57,43,.06);}

.sc-divider{height:1px;background:var(--border);margin:1.2rem 0;}
.sc-footer{font-size:9px;color:var(--text3);letter-spacing:1px;text-transform:uppercase;text-align:center;}
/* ── FIM SCORECARD ───────────────────────────────────────── */
"""

# ─── HTML DO SCORECARD (injetar dentro de s-results, antes de .res-btns) ────
SCORECARD_HTML = """
      <!-- NEXOR SCORECARD RELAMPAGO -->
      <div class="scorecard" id="scorecard-wrap">
        <div class="sc-header">
          <span class="sc-title">NEXOR Scorecard</span>
          <span class="sc-level" id="sc-level-badge">★☆☆ TRAINING</span>
        </div>
        <div class="sc-bars">
          <div class="sc-bar-row">
            <span class="sc-bar-label">Easy</span>
            <div class="sc-bar-track"><div class="sc-bar-fill easy" id="sc-bar-easy" style="width:0%"></div></div>
            <span class="sc-bar-pct" id="sc-pct-easy">0%</span>
          </div>
          <div class="sc-bar-row">
            <span class="sc-bar-label">Standard</span>
            <div class="sc-bar-track"><div class="sc-bar-fill standard" id="sc-bar-std" style="width:0%"></div></div>
            <span class="sc-bar-pct" id="sc-pct-std">0%</span>
          </div>
          <div class="sc-bar-row">
            <span class="sc-bar-label">Hard</span>
            <div class="sc-bar-track"><div class="sc-bar-fill hard" id="sc-bar-hard" style="width:0%"></div></div>
            <span class="sc-bar-pct" id="sc-pct-hard">0%</span>
          </div>
        </div>
        <div class="sc-message" id="sc-message">—</div>
        <div class="sc-divider"></div>
        <div class="sc-footer">FractalLearning™ · Psychometric Assessment</div>
      </div>
"""

# ─── JS DO SCORECARD (injetar antes de init();) ──────────────────────────────
SCORECARD_JS = """
// ── NEXOR SCORECARD ──────────────────────────────────────────────────────────
function calcScorecard() {
  const qs = quiz.questions;
  const total = qs.length;
  if (!total) return;

  // Separa por dificuldade
  const byLevel = { EASY: {tot:0,ok:0}, STANDARD: {tot:0,ok:0}, HARD: {tot:0,ok:0} };

  qs.forEach((q, i) => {
    const level = (q.difficulty || 'STANDARD').toUpperCase();
    if (!byLevel[level]) byLevel[level] = {tot:0, ok:0};
    byLevel[level].tot++;
    // Detecta se acertou: quiz.answers[i] === q.correct
    if (quiz.answers && quiz.answers[i] === q.correct) byLevel[level].ok++;
  });

  // Fallback: usa quiz.correct/wrong se answers nao disponivel
  const pct = Math.round(quiz.correct / total * 100);

  // Calcula pct por nivel
  const easyPct  = byLevel.EASY.tot  > 0 ? Math.round(byLevel.EASY.ok  / byLevel.EASY.tot  * 100) : pct;
  const stdPct   = byLevel.STANDARD.tot > 0 ? Math.round(byLevel.STANDARD.ok / byLevel.STANDARD.tot * 100) : pct;
  const hardPct  = byLevel.HARD.tot  > 0 ? Math.round(byLevel.HARD.ok  / byLevel.HARD.tot  * 100) : Math.max(0, pct - 15);

  // Nivel de prontidao
  let level, levelClass, levelText;
  if (pct >= 80) {
    level = 'ready'; levelText = '★★★ EXAM READY';
  } else if (pct >= 60) {
    level = 'progress'; levelText = '★★☆ IN PROGRESS';
  } else {
    level = 'training'; levelText = '★☆☆ TRAINING';
  }

  // Mensagem contextual
  let msg = '';
  const domainName = sel.domain ? sel.domain.name : 'este domínio';
  if (pct >= 80) {
    msg = `<strong>Excelente domínio de ${domainName}.</strong> Seu desempenho está no nível dos candidatos aprovados. ${hardPct < 70 ? 'Atenção extra nas questões Hard — são as que diferenciam no exame real.' : 'Continue mantendo esse ritmo nos demais domínios.'}`;
  } else if (pct >= 60) {
    msg = `<strong>Progresso sólido em ${domainName}.</strong> Você domina os conceitos fundamentais. ${stdPct < 70 ? 'Reforce as questões Standard — cobrem 60% do exame real.' : 'Foque nas Hard para elevar sua prontidão ao próximo nível.'}`;
  } else {
    msg = `<strong>Continue estudando ${domainName}.</strong> ${easyPct < 70 ? 'Revise os conceitos básicos antes de avançar para questões mais complexas.' : 'Você domina o básico — aprofunde nas questões Standard e Hard para consolidar.'}`;
  }

  // Atualiza UI
  setTimeout(() => {
    const badge = document.getElementById('sc-level-badge');
    if (badge) { badge.textContent = levelText; badge.className = 'sc-level ' + level; }

    const setBar = (id, pctId, val) => {
      const bar = document.getElementById(id);
      const lbl = document.getElementById(pctId);
      if (bar) bar.style.width = val + '%';
      if (lbl) lbl.textContent = val + '%';
    };

    setBar('sc-bar-easy', 'sc-pct-easy', easyPct);
    setBar('sc-bar-std',  'sc-pct-std',  stdPct);
    setBar('sc-bar-hard', 'sc-pct-hard', hardPct);

    const msgEl = document.getElementById('sc-message');
    if (msgEl) msgEl.innerHTML = msg;
  }, 150);
}
// ── FIM SCORECARD ─────────────────────────────────────────────────────────────
"""

def main():
    print("=" * 70)
    print("  NEXOR -- PATCH SCORECARD v1")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)

    # Backup
    bak = f"{INDEX_FILE}.bak_{TIMESTAMP}"
    shutil.copy2(INDEX_FILE, bak)
    print(f"\n  Backup: {bak}")

    with open(INDEX_FILE, encoding="utf-8") as f:
        content = f.read()

    errors = []

    # 1. Injeta CSS antes de </style>
    if "</style>" in content:
        content = content.replace("</style>", SCORECARD_CSS + "\n</style>", 1)
        print("  OK — CSS do Scorecard injetado")
    else:
        errors.append("ERRO — </style> nao encontrado")

    # 2. Injeta HTML do scorecard na tela s-results
    # Procura pelo div .res-btns dentro de s-results
    RES_BTNS_ANCHOR = '<div class="res-btns">'
    if RES_BTNS_ANCHOR in content:
        content = content.replace(
            RES_BTNS_ANCHOR,
            SCORECARD_HTML + "\n      " + RES_BTNS_ANCHOR,
            1
        )
        print("  OK — HTML do Scorecard injetado na tela de resultados")
    else:
        errors.append("ERRO — .res-btns nao encontrado no HTML")

    # 3. Injeta JS antes de init();
    if "init();" in content:
        content = content.replace("init();", SCORECARD_JS + "\ninit();", 1)
        print("  OK — JS do Scorecard injetado")
    else:
        errors.append("ERRO — init(); nao encontrado no JS")

    # 4. Chama calcScorecard() no final de showResults()
    # Injeta chamada logo apos goTo('s-results')
    GOTO_RESULTS = "goTo('s-results');"
    if GOTO_RESULTS in content:
        content = content.replace(
            GOTO_RESULTS,
            GOTO_RESULTS + "\n  calcScorecard();",
            1
        )
        print("  OK — calcScorecard() chamado ao fim de showResults()")
    else:
        errors.append("ERRO — goTo('s-results') nao encontrado")

    # 5. Rastreia respostas no quiz (injeta no objeto quiz e na funcao answer)
    # Adiciona answers:[] ao objeto quiz
    QUIZ_OBJ_ANCHOR = "quiz.correct = 0;"
    if QUIZ_OBJ_ANCHOR in content:
        content = content.replace(
            QUIZ_OBJ_ANCHOR,
            QUIZ_OBJ_ANCHOR + "\n  quiz.answers = [];",
            1
        )
        print("  OK — quiz.answers[] inicializado")
    else:
        errors.append("AVISO — quiz.correct = 0 nao encontrado — answers tracking manual")

    # Registra resposta em quiz.answers no momento de answer(chosen)
    ANSWER_CORRECT = "quiz.correct++;"
    ANSWER_WRONG   = "quiz.wrong++;"
    if ANSWER_CORRECT in content:
        content = content.replace(
            ANSWER_CORRECT,
            "quiz.answers.push(chosen); " + ANSWER_CORRECT,
            1
        )
        content = content.replace(
            ANSWER_WRONG,
            "quiz.answers.push(chosen); " + ANSWER_WRONG,
            1
        )
        print("  OK — respostas rastreadas em quiz.answers[]")

    if errors:
        print("\n  AVISOS/ERROS:")
        for e in errors:
            print(f"    · {e}")
        if any("ERRO" in e for e in errors):
            print("\n  ARQUIVO NAO SALVO devido a erros criticos")
            return

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n  Arquivo salvo: {INDEX_FILE}")

    print("\n" + "=" * 70)
    print("  CONCLUIDO")
    print("  O servidor detecta automaticamente a mudança (--reload)")
    print("  Abra o browser e faça um quiz para ver o Scorecard")
    print("=" * 70)

if __name__ == "__main__":
    main()
