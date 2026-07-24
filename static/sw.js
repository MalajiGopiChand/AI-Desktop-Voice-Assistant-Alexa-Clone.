// Service Worker for METIS AI Mobile Web PWA
const CACHE_NAME = 'metis-mobile-pwa-v2';
const urlsToCache = [
  '/',
  '/static/style.css',
  '/static/manifest.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(urlsToCache);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    fetch(event.request).catch(() => {
      return caches.match(event.request);
    })
  );
});

self.addEventListener('push', (event) => {
  const data = event.data ? event.data.json() : { title: 'METIS AI Mobile Alert', body: 'New notification from Metis' };
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: 'https://img.icons8.com/color/192/bot.png',
      vibrate: [200, 100, 200]
    })
  );
});
