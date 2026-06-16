const NOTIFS = [];

const UNREAD_COUNT = 0;

function buildSheet() {
  const sheet = document.createElement('div');
  sheet.className = 'nx-notif-sheet';
  sheet.id = 'nx-notif-sheet';

  let html = `
    <div class="nx-notif-handle"></div>
    <div class="nx-notif-header">
      <div class="nx-notif-title">Notificações <span style="font-size:11px;color:rgba(240,246,251,0.35);font-family:'Barlow',sans-serif;font-weight:300;margin-left:4px;">${UNREAD_COUNT} novas</span></div>
      <span class="nx-notif-mark" onclick="markAllRead()">marcar todas como lidas</span>
    </div>
    <div class="nx-notif-list" id="nx-notif-list">`;

  if (NOTIFS.length === 0) {
    html += `<div style="text-align:center;padding:40px 20px;color:#555;font-size:13px;font-family:'Barlow',sans-serif;font-weight:300;">Nenhuma notificação por enquanto.<br><span style="font-size:11px;color:#444;">Comece a estudar para receber atualizações.</span></div>`;
  } else {
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
  }

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
