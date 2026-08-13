// Minimal Service Worker to satisfy PWA installation requirements
// without caching dynamic page requests which rely on server side databases.

const CACHE_NAME = 'ici-generator-cache-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/static/css/style.css',
  '/static/css/dashboard.css',
  '/static/js/main.js',
  '/static/js/charts.js',
  '/static/js/upload.js',
  '/static/images/icon-192.png',
  '/static/images/icon-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        // Cache core static assets
        return cache.addAll(ASSETS_TO_CACHE);
      })
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cache => {
          if (cache !== CACHE_NAME) {
            return caches.delete(cache);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  // Only intercept HTTP requests (avoid chrome-extension:// etc.)
  if (!event.request.url.startsWith(self.location.origin)) {
    return;
  }
  
  // Use a Network-First fallback to Cache strategy for asset requests,
  // letting dynamic routes (like uploads or history logs) fail gracefully
  // rather than serving stale HTML.
  event.respondWith(
    fetch(event.request)
      .catch(() => {
        return caches.match(event.request);
      })
  );
});
