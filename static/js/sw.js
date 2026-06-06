const CACHE_NAME = 'ethernet-arch-v1';
const assets = [
  '/',
  '/static/css/styles.css',
  'https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(assets))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});
