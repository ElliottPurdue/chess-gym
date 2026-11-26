// Chess Gym offline cache. Version changes whenever any app file changes, so an update is picked up on the next launch.
const V = 'gym-30f2146d86', FILES = ["./", "index.html", "manifest.webmanifest", "chess.js", "pieces.css", "puzzles.json", "themes.json", "themes2.json", "openings.json", "deviations.json", "drills.json", "study.json", "favicon.png", "icons/app-180.png", "icons/app-192.png", "icons/app-512.png"];
self.addEventListener('install', (e) => { e.waitUntil(caches.open(V).then((c) => c.addAll(FILES)).then(() => self.skipWaiting())); });
self.addEventListener('activate', (e) => { e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== V).map((k) => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', (e) => {
  const u = new URL(e.request.url);
  if (e.request.method !== 'GET' || u.origin !== location.origin) return; // GitHub sync and links go straight to the network
  // app files: network first (so updates arrive), cache when offline
  e.respondWith(fetch(e.request).then((r) => { if (r.ok) { const c = r.clone(); caches.open(V).then((cc) => cc.put(e.request, c)); } return r; }).catch(() => caches.match(e.request, { ignoreSearch: true }).then((r) => r || caches.match('index.html'))));
});
