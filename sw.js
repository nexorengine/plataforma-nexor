// Atualize esta versão a cada deploy para forçar renovação do cache
const CACHE = 'nexor-med-v5-20260707';
const STATIC_ASSETS = [
  '/assets/nx.css',
  '/assets/nx-glass.css',
  '/assets/icon-192.png',
  '/assets/icon-512.png',
  '/manifest.json'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(STATIC_ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const url = e.request.url;

  // Supabase e Stripe — sempre online, nunca cache
  if (url.includes('supabase.co') || url.includes('stripe.com')) return;

  // HTML e JS — network first: sempre busca versão mais recente
  // Se offline, cai no cache como fallback
  if (e.request.destination === 'document' || url.endsWith('.js')) {
    e.respondWith(
      fetch(e.request)
        .then(res => {
          const clone = res.clone();
          caches.open(CACHE).then(c => c.put(e.request, clone));
          return res;
        })
        .catch(() => caches.match(e.request))
    );
    return;
  }

  // CSS e imagens — cache first (mudam raramente)
  e.respondWith(
    caches.match(e.request).then(cached => cached || fetch(e.request))
  );
});
