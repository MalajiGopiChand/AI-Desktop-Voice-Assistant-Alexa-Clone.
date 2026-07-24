// Service Worker for METIS AI OS Mobile PWA & Background Sync
const CACHE_NAME = 'metis-ai-v1';
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

// Background Push & Notification Listener
self.addEventListener('push', (event) => {
  const data = event.data ? event.data.json() : { title: 'Metis AI Alert', body: 'New notification' };
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: 'https://img.icons8.com/color/192/bot.png',
      vibrate: [200, 100, 200]
    })
  );
});
