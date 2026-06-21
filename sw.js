const CACHE = 'nexor-med-v1';
const ASSETS = [
  '/',
  '/index.html',
  '/login.html',
  '/c1-med.html',
  '/c2-med.html',
  '/c3-med.html',
  '/c4a-flashcard.html',
  '/c4b-quiz.html',
  '/c4c-scorecard.html',
  '/upgrade.html',
  '/success.html',
  '/assets/nx.css',
  '/assets/nx-glass.css',
  '/assets/auth.js',
  '/assets/catalog.js',
  '/assets/notif.js',
  '/assets/profile.js',
  '/assets/tts.js',
  '/assets/icon-192.png',
  '/assets/icon-512.png',
  '/manifest.json'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting())
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
  // Supabase e Stripe — sempre online, nunca cache
  if (e.request.url.includes('supabase.co') || e.request.url.includes('stripe.com')) return;

  e.respondWith(
    caches.match(e.request).then(cached => cached || fetch(e.request))
  );
});
