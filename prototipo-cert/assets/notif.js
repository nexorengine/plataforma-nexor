const NOTIFS = [
  {
    group: "HOJE",
    items: [
      {
        id: 1, unread: true, color: "red",
        icon: "ti ti-flame", iconColor: "#ef4444",
        text: "<strong>Sequência em risco.</strong> Você não estuda há 2 dias — não perca seu ritmo agora.",
        time: "há 1h",
        link: "c2-med.html"
      },
      {
        id: 2, unread: true, color: "gold",
        icon: "ti ti-target", iconColor: "#FCA311",
        text: "<strong>Você está a 12 pts de aprovar CG_D06.</strong> Tente o Quiz 002 de Intestino Delgado novamente.",
        time: "há 3h",
        link: "c3-med.html"
      },
    ]
  },
  {
    group: "ESTA SEMANA",
    items: [
      {
        id: 3, unread: true, color: "green",
        icon: "ti ti-trophy", iconColor: "#22c55e",
        text: "<strong>CG_D01 Abdome Agudo concluído!</strong> Próximo domínio disponível: Trauma e Urgência Cirúrgica.",
        time: "ontem",
        link: "c3-med.html"
      },
      {
        id: 4, unread: false, color: "gold",
        icon: "ti ti-chart-bar", iconColor: "#FCA311",
        text: "<strong>Progresso atualizado.</strong> Cirurgia Geral subiu de 65% → 72%. Continue assim.",
        time: "2 dias atrás",
        link: "c2-med.html"
      },
      {
        id: 5, unread: false, color: "blue",
        icon: "ti ti-bell", iconColor: "#60a5fa",
        text: "<strong>Clínica Médica chegando em breve.</strong> Você será notificado assim que o conteúdo estiver disponível.",
        time: "3 dias atrás",
        link: null
      },
    ]
  },
  {
    group: "ESTE MÊS",
    items: [
      {
        id: 6, unread: false, color: "red",
        icon: "ti ti-credit-card", iconColor: "#f87171",
        text: "<strong>Seu plano vence em 7 dias.</strong> Renove agora para não perder o acesso.",
        time: "há 5 dias",
        link: "index.html"
      },
      {
        id: 7, unread: false, color: "green",
        icon: "ti ti-cards", iconColor: "#4ade80",
        text: "<strong>Meta diária atingida!</strong> 20 flashcards revisados em CG_D01.",
        time: "há 6 dias",
        link: null
      },
    ]
  }
];

const UNREAD_COUNT = NOTIFS.flatMap(g => g.items).filter(n => n.unread).length;

function buildSheet() {
  const sheet = document.createElement('div');
  sheet.className = 'nx-notif-sheet';
  sheet.id = 'nx-notif-sheet';

  let html = `
    <div class="nx-notif-handle"></div>
    <div class="nx-notif-header">
      <div class="nx-notif-title">Notificações <span style="font-size:11px;color:#ef4444;font-family:'Barlow',sans-serif;font-weight:400;margin-left:4px;">${UNREAD_COUNT} novas</span></div>
      <span class="nx-notif-mark" onclick="markAllRead()">marcar todas como lidas</span>
    </div>
    <div class="nx-notif-list" id="nx-notif-list">`;

  NOTIFS.forEach(group => {
    html += `<div class="nx-notif-group">${group.group}</div>`;
    group.items.forEach(n => {
      const cls = n.unread
        ? (n.color === 'red' ? 'nx-notif-item unread-red' : n.color === 'green' ? 'nx-notif-item unread-green' : 'nx-notif-item unread')
        : 'nx-notif-item';
      html += `
        <div class="${cls}" id="notif-${n.id}" onclick="handleNotif(${n.id}, '${n.link || ''}')">
          <div class="nx-notif-icon ${n.color}"><i class="${n.icon}" style="color:${n.iconColor};"></i></div>
          <div class="nx-notif-body">
            <div class="nx-notif-text">${n.text}</div>
            <div class="nx-notif-time">${n.time}</div>
          </div>
        </div>`;
    });
  });

  html += `</div>`;
  sheet.innerHTML = html;
  return sheet;
}

function buildOverlay() {
  const o = document.createElement('div');
  o.className = 'nx-notif-overlay';
  o.id = 'nx-notif-overlay';
  o.onclick = closeNotif;
  return o;
}

function buildBellBadge() {
  const btn = document.getElementById('nx-bell-btn');
  if (!btn) return;
  if (UNREAD_COUNT > 0) {
    btn.innerHTML = `<i class="ti ti-bell"></i><span class="nx-bell-badge"></span>`;
  } else {
    btn.innerHTML = `<i class="ti ti-bell"></i>`;
  }
}

function toggleNotif() {
  const sheet = document.getElementById('nx-notif-sheet');
  const overlay = document.getElementById('nx-notif-overlay');
  const btn = document.getElementById('nx-bell-btn');
  const isOpen = sheet.classList.contains('open');
  if (isOpen) {
    closeNotif();
  } else {
    sheet.classList.add('open');
    overlay.classList.add('open');
    btn.classList.add('active');
  }
}

function closeNotif() {
  const sheet = document.getElementById('nx-notif-sheet');
  const overlay = document.getElementById('nx-notif-overlay');
  const btn = document.getElementById('nx-bell-btn');
  sheet.classList.remove('open');
  overlay.classList.remove('open');
  if (btn) btn.classList.remove('active');
}

function markAllRead() {
  document.querySelectorAll('.nx-notif-item').forEach(el => {
    el.className = 'nx-notif-item';
  });
  const badge = document.querySelector('.nx-bell-badge');
  if (badge) badge.remove();
  document.querySelector('.nx-notif-header span[style]').textContent = '';
  document.querySelector('.nx-notif-title').innerHTML = 'Notificações <span style="font-size:11px;color:#888;font-family:\'Barlow\',sans-serif;font-weight:400;margin-left:4px;">tudo lido</span>';
}

function handleNotif(id, link) {
  const el = document.getElementById('notif-' + id);
  if (el) el.className = 'nx-notif-item';
  if (link) {
    closeNotif();
    setTimeout(() => { window.location.href = link; }, 200);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  document.body.appendChild(buildOverlay());
  document.body.appendChild(buildSheet());
  buildBellBadge();
});
