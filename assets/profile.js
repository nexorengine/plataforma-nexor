const PROFILE = {
  name: "Residente",
  email: "seu@email.com.br",
  initials: "R",
  plan: "Plano Anual",
  planStatus: "ativo",
  memberSince: "—",
  stats: { progress: "0%", streak: 0, domains: 0 }
};

// Configurações persistidas em localStorage
const CFG_KEY = 'nx_config';
function loadConfig() {
  try { return JSON.parse(localStorage.getItem(CFG_KEY)) || {}; } catch(e) { return {}; }
}
function saveConfig(cfg) {
  localStorage.setItem(CFG_KEY, JSON.stringify(cfg));
}

document.addEventListener('DOMContentLoaded', () => {
  const overlay = document.createElement('div');
  overlay.id = 'nx-profile-overlay';
  overlay.style.cssText = 'position:fixed;inset:0;z-index:299;background:rgba(0,0,0,0.6);opacity:0;pointer-events:none;transition:opacity 0.3s;';
  overlay.onclick = closeProfile;

  const sheet = document.createElement('div');
  sheet.id = 'nx-profile-sheet';
  sheet.className = 'nx-profile-sheet';
  sheet.innerHTML = `
    <div class="nx-sheet-handle"></div>

    <div style="display:flex;align-items:center;gap:14px;padding:20px 20px 16px;">
      <div id="nx-prof-avatar" style="width:52px;height:52px;border-radius:50%;background:#14213D;border:2px solid #0EA5E9;display:flex;align-items:center;justify-content:center;font-family:'Barlow',sans-serif;font-weight:700;font-size:18px;color:#0EA5E9;flex-shrink:0;">—</div>
      <div>
        <div id="nx-prof-name" style="font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:16px;color:#F5F5F5;line-height:1.2;">Carregando…</div>
        <div id="nx-prof-email" style="font-size:11px;color:#A8A8A8;margin-top:2px;"></div>
        <div id="nx-prof-plan-badge" style="display:inline-flex;align-items:center;gap:4px;margin-top:5px;background:rgba(74,222,128,0.1);border:1px solid rgba(74,222,128,0.25);border-radius:4px;padding:2px 8px;">
          <i class="ti ti-circle-check" style="font-size:11px;color:#4ade80;"></i>
          <span id="nx-prof-plan-txt" style="font-size:10px;font-family:'Barlow',sans-serif;font-weight:400;color:#4ade80;">—</span>
        </div>
      </div>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin:0 16px 16px;background:#060e1a;border:1px solid #1E2D44;border-radius:8px;padding:12px 8px;">
      <div style="text-align:center;">
        <div style="font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:18px;color:#0EA5E9;" id="nx-stat-prog">${PROFILE.stats.progress}</div>
        <div style="font-size:10px;color:#888;margin-top:2px;">progresso</div>
      </div>
      <div style="text-align:center;border-left:1px solid #1E2D44;border-right:1px solid #1E2D44;">
        <div style="font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:18px;color:#0EA5E9;display:flex;align-items:center;justify-content:center;gap:3px;">
          <i class="ti ti-flame" style="font-size:16px;color:#f97316;"></i><span id="nx-stat-streak">${PROFILE.stats.streak}</span>
        </div>
        <div style="font-size:10px;color:#888;margin-top:2px;">dias seguidos</div>
      </div>
      <div style="text-align:center;">
        <div style="font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:18px;color:#0EA5E9;" id="nx-stat-doms">${PROFILE.stats.domains}</div>
        <div style="font-size:10px;color:#888;margin-top:2px;">domínios</div>
      </div>
    </div>

    <div style="border-top:1px solid #1E2D44;padding:8px 0;">
      <div class="nx-profile-item nx-profile-soon" onclick="profileComingSoon()">
        <i class="ti ti-chart-bar" style="color:#555;"></i>
        <span style="color:#555;">Meu Progresso</span>
        <span style="margin-left:auto;font-size:9px;font-family:'Barlow',sans-serif;background:#1E2D44;color:#555;padding:2px 6px;border-radius:3px;">em breve</span>
      </div>
      <div class="nx-profile-item nx-profile-soon" onclick="profileComingSoon()">
        <i class="ti ti-trophy" style="color:#555;"></i>
        <span style="color:#555;">Conquistas</span>
        <span style="margin-left:auto;font-size:9px;font-family:'Barlow',sans-serif;background:#1E2D44;color:#555;padding:2px 6px;border-radius:3px;">em breve</span>
      </div>
      <div class="nx-profile-item" onclick="openConfig()">
        <i class="ti ti-settings" style="color:#0EA5E9;"></i>
        <span>Configurações</span>
        <i class="ti ti-chevron-right" style="margin-left:auto;color:#555;"></i>
      </div>
      <div class="nx-profile-item" onclick="openSupport()">
        <i class="ti ti-help-circle" style="color:#0EA5E9;"></i>
        <span>Suporte</span>
        <i class="ti ti-chevron-right" style="margin-left:auto;color:#555;"></i>
      </div>
    </div>

    <div style="border-top:1px solid #1E2D44;padding:8px 0 4px;">
      <div class="nx-profile-item" onclick="doLogout()" style="color:#ef4444;">
        <i class="ti ti-logout" style="color:#ef4444;"></i>
        <span>Sair da conta</span>
      </div>
    </div>

    <div style="padding:12px 20px;text-align:center;">
      <span id="nx-prof-since" style="font-size:10px;color:#707070;font-family:'Barlow',sans-serif;">nexor_med v1.0</span>
    </div>
  `;

  // Painel de Configurações
  const cfgSheet = document.createElement('div');
  cfgSheet.id = 'nx-config-sheet';
  cfgSheet.className = 'nx-profile-sheet';
  cfgSheet.style.zIndex = '301';
  cfgSheet.innerHTML = `
    <div class="nx-sheet-handle"></div>
    <div style="display:flex;align-items:center;gap:10px;padding:16px 20px 12px;border-bottom:1px solid #1E2D44;">
      <button onclick="closeConfig()" style="background:transparent;border:none;color:#888;cursor:pointer;padding:0;display:flex;align-items:center;gap:4px;font-size:13px;font-family:'Barlow',sans-serif;">
        <i class="ti ti-arrow-left"></i> voltar
      </button>
      <span style="font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:15px;color:#F5F5F5;">Configurações</span>
    </div>

    <div style="padding:16px 20px;border-bottom:1px solid #1E2D44;">
      <div style="font-size:10px;color:#0EA5E9;font-family:'Barlow',sans-serif;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:12px;">Notificações</div>
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
          <div style="font-size:14px;color:#F5F5F5;font-family:'Barlow',sans-serif;">Alertas de estudo</div>
          <div style="font-size:11px;color:#888;margin-top:2px;">lembretes diários e sequência</div>
        </div>
        <label class="nx-toggle">
          <input type="checkbox" id="cfg-notif" onchange="saveCfg()" checked>
          <span class="nx-toggle-slider"></span>
        </label>
      </div>
    </div>

    <div style="padding:16px 20px;">
      <div style="font-size:10px;color:#0EA5E9;font-family:'Barlow',sans-serif;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:12px;">Voz (TTS)</div>
      <div style="font-size:13px;color:#888;font-family:'Barlow',sans-serif;margin-bottom:10px;">Velocidade da leitura em voz alta</div>
      <div style="display:flex;gap:8px;" id="cfg-speed-btns">
        <button class="nx-speed-btn" data-speed="0.8" onclick="setSpeed(this)">0.8×</button>
        <button class="nx-speed-btn active" data-speed="0.95" onclick="setSpeed(this)">1.0×</button>
        <button class="nx-speed-btn" data-speed="1.2" onclick="setSpeed(this)">1.2×</button>
        <button class="nx-speed-btn" data-speed="1.5" onclick="setSpeed(this)">1.5×</button>
      </div>
    </div>
  `;

  document.body.appendChild(overlay);
  document.body.appendChild(sheet);
  document.body.appendChild(cfgSheet);

  // Carrega dados reais do usuário (iniciais no header + perfil completo)
  _loadProfileUser();

  // Restaura configurações salvas
  const cfg = loadConfig();
  if (cfg.ttsSpeed) {
    window._ttsSpeed = cfg.ttsSpeed;
  } else {
    window._ttsSpeed = 0.95;
  }
});

function _calcStreak(dates) {
  // dates = array de strings 'YYYY-MM-DD' únicas, qualquer ordem
  if (!dates.length) return 0;
  const set = new Set(dates);
  const today = new Date();
  today.setHours(0,0,0,0);
  // Grace period: começa de hoje ou ontem
  let cursor = new Date(today);
  const toKey = d => d.toISOString().slice(0,10);
  if (!set.has(toKey(cursor))) {
    cursor.setDate(cursor.getDate() - 1);
    if (!set.has(toKey(cursor))) return 0;
  }
  let streak = 0;
  while (set.has(toKey(cursor))) {
    streak++;
    cursor.setDate(cursor.getDate() - 1);
  }
  return streak;
}

async function _loadProfileUser() {
  try {
    const { data: { session } } = await _sb.auth.getSession();
    if (!session) return;
    const u = session.user;

    // Nome: full_name do Google OAuth, ou parte antes do @ no email
    const fullName = u.user_metadata?.full_name || u.user_metadata?.name || '';
    const displayName = fullName || u.email.split('@')[0];

    // Iniciais: até 2 letras do nome completo, ou 2 primeiras do email slug
    const initials = fullName
      ? fullName.split(' ').filter(Boolean).map(w => w[0]).join('').toUpperCase().slice(0, 2)
      : displayName.slice(0, 2).toUpperCase();

    // Membro desde
    const since = u.created_at
      ? new Date(u.created_at).toLocaleDateString('pt-BR', { month: 'short', year: 'numeric' })
      : '—';

    // Plano
    let planTxt = 'Trial ativo';
    let planColor = '#0EA5E9';
    let planBg = 'rgba(14,165,233,0.10)';
    let planBorder = 'rgba(14,165,233,0.25)';
    let planIcon = 'ti-clock';
    if (typeof Auth !== 'undefined') {
      const sub = await Auth.subscription();
      if (sub) {
        if (sub.plan === 'annual') { planTxt = 'Plano Anual · ativo'; }
        else if (sub.plan === 'monthly') { planTxt = 'Plano Mensal · ativo'; }
        else if (sub.plan === 'trial') {
          const dias = Math.ceil((new Date(sub.trial_ends_at) - new Date()) / 86400000);
          planTxt = dias > 0 ? `Trial · ${dias}d restante${dias > 1 ? 's' : ''}` : 'Trial expirado';
          if (dias <= 0) { planColor = '#f87171'; planBg = 'rgba(239,68,68,0.08)'; planBorder = 'rgba(239,68,68,0.25)'; planIcon = 'ti-lock'; }
        }
        if (sub.plan !== 'trial') {
          planColor = '#4ade80'; planBg = 'rgba(74,222,128,0.1)'; planBorder = 'rgba(74,222,128,0.25)'; planIcon = 'ti-circle-check';
        }
      }
    }

    // Atualiza DOM
    const avatarEl = document.getElementById('nx-prof-avatar');
    if (avatarEl) avatarEl.textContent = initials;

    const nameEl = document.getElementById('nx-prof-name');
    if (nameEl) nameEl.textContent = displayName;

    const emailEl = document.getElementById('nx-prof-email');
    if (emailEl) emailEl.textContent = u.email;

    const badgeEl = document.getElementById('nx-prof-plan-badge');
    if (badgeEl) {
      badgeEl.style.background = planBg;
      badgeEl.style.borderColor = planBorder;
      badgeEl.querySelector('i').className = `ti ${planIcon}`;
      badgeEl.querySelector('i').style.color = planColor;
    }
    const planTxtEl = document.getElementById('nx-prof-plan-txt');
    if (planTxtEl) { planTxtEl.textContent = planTxt; planTxtEl.style.color = planColor; }

    const sinceEl = document.getElementById('nx-prof-since');
    if (sinceEl) sinceEl.textContent = `membro desde ${since} · nexor_med v1.0`;

    // Atualiza também o avatar no header
    const headerAvatar = document.querySelector('.nx-avatar-btn');
    if (headerAvatar) headerAvatar.textContent = initials;

  } catch(e) { console.warn('Erro ao carregar perfil do usuário:', e); }
}

async function _loadProfileStats() {
  try {
    const {data:{session}} = await _sb.auth.getSession();
    if (!session) return;
    const {data:rows} = await _sb.from('study_sessions')
      .select('created_at,dominio,tipo,score')
      .eq('user_id', session.user.id);
    if (!rows || !rows.length) return;

    // Streak
    const dates = [...new Set(rows.map(r => new Date(r.created_at).toLocaleDateString('sv-SE')))];
    const streak = _calcStreak(dates);

    // Domínios concluídos (quiz_1 + quiz_2 ≥ 50% cada)
    const byDom = {};
    rows.forEach(r => {
      if (r.tipo !== 'quiz') return;
      if (!byDom[r.dominio]) byDom[r.dominio] = {};
      const best = byDom[r.dominio][r.modulo] || 0;
      byDom[r.dominio][r.modulo] = Math.max(best, parseFloat(r.score) || 0);
    });
    const dominiosConcluidos = Object.values(byDom)
      .filter(m => (m.quiz_1 >= 50) && (m.quiz_2 >= 50)).length;

    // Progresso global = domínios concluídos / total do catálogo
    const totalDominios = typeof CATALOG !== 'undefined'
      ? Object.values(CATALOG).reduce((acc, a) => acc + a.dominios.length, 0)
      : 0;
    const progresso = totalDominios > 0
      ? Math.round(dominiosConcluidos / totalDominios * 100)
      : 0;

    // Atualiza DOM
    const streakEl   = document.getElementById('nx-stat-streak');
    const domsEl     = document.getElementById('nx-stat-doms');
    const progEl     = document.getElementById('nx-stat-prog');
    if (streakEl) streakEl.textContent = streak;
    if (domsEl)   domsEl.textContent   = dominiosConcluidos;
    if (progEl)   progEl.textContent   = progresso + '%';
  } catch(e) { console.warn('Erro ao carregar stats do perfil:', e); }
}

function toggleProfile() {
  const sheet = document.getElementById('nx-profile-sheet');
  const overlay = document.getElementById('nx-profile-overlay');
  if (!sheet) return;
  if (sheet.classList.contains('open')) {
    closeProfile();
  } else {
    sheet.classList.add('open');
    overlay.style.opacity = '1';
    overlay.style.pointerEvents = 'auto';
    _loadProfileUser();
    _loadProfileStats();
  }
}

function closeProfile() {
  const sheet = document.getElementById('nx-profile-sheet');
  const overlay = document.getElementById('nx-profile-overlay');
  if (!sheet) return;
  sheet.classList.remove('open');
  overlay.style.opacity = '0';
  overlay.style.pointerEvents = 'none';
}

function profileComingSoon() {
  // Itens "em breve" — não fazem nada
}

function openConfig() {
  closeProfile();
  const cfg = loadConfig();
  setTimeout(() => {
    const cfgSheet = document.getElementById('nx-config-sheet');
    const overlay = document.getElementById('nx-profile-overlay');
    // Restaura estado dos toggles
    const notifEl = document.getElementById('cfg-notif');
    if (notifEl) notifEl.checked = cfg.notif !== false;
    // Restaura botão de velocidade ativo
    const speed = cfg.ttsSpeed || 0.95;
    document.querySelectorAll('.nx-speed-btn').forEach(btn => {
      btn.classList.toggle('active', parseFloat(btn.dataset.speed) === speed);
    });
    cfgSheet.classList.add('open');
    overlay.style.opacity = '1';
    overlay.style.pointerEvents = 'auto';
  }, 200);
}

function closeConfig() {
  const cfgSheet = document.getElementById('nx-config-sheet');
  const overlay = document.getElementById('nx-profile-overlay');
  cfgSheet.classList.remove('open');
  overlay.style.opacity = '0';
  overlay.style.pointerEvents = 'none';
}

function setSpeed(btn) {
  document.querySelectorAll('.nx-speed-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  const speed = parseFloat(btn.dataset.speed);
  window._ttsSpeed = speed;
  saveCfg();
}

function saveCfg() {
  const notifEl = document.getElementById('cfg-notif');
  const cfg = {
    notif: notifEl ? notifEl.checked : true,
    ttsSpeed: window._ttsSpeed || 0.95
  };
  saveConfig(cfg);
}

async function doLogout() {
  closeProfile();
  await Auth.logout();
}

function openSupport() {
  closeProfile();
  window.open('https://wa.me/5547992544143?text=Ol%C3%A1%2C+preciso+de+suporte+com+o+nexor_med', '_blank');
}
