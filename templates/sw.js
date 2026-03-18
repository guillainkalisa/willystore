const CACHE_NAME = 'willystore-cache-v1';
const ASSETS_TO_CACHE = [
    '/',
    '/static/css/style.css',
    '/static/js/main.js',
    // Fallback fonts/icons
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
    'https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js'
];

// Install Event: Cache Core Static Assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS_TO_CACHE);
        })
    );
    self.skipWaiting();
});

// Activate Event: Clean up old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cache) => {
                    if (cache !== CACHE_NAME) {
                        return caches.delete(cache);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

// Fetch Event: Stale-While-Revalidate strategy for images and dynamic content
self.addEventListener('fetch', (event) => {
    const requestUrl = new URL(event.request.url);

    // Specifically target Images (Unsplash, Media uploads, etc.) to cache them instantly
    if (event.request.destination === 'image' || requestUrl.pathname.startsWith('/media/')) {
        event.respondWith(
            caches.match(event.request).then((cachedResponse) => {
                const networkFetch = fetch(event.request).then((networkResponse) => {
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, networkResponse.clone());
                    });
                    return networkResponse;
                }).catch(() => {
                    // Fail silently for images if offline, just use cache
                });

                // Return cache immediately if available, while fetching update in BG
                return cachedResponse || networkFetch;
            })
        );
        return;
    }

    // Default Cache-First strategy for CSS/JS
    if (event.request.destination === 'style' || event.request.destination === 'script') {
        event.respondWith(
            caches.match(event.request).then((response) => {
                return response || fetch(event.request);
            })
        );
        return;
    }

    // Network-First for HTML pages to ensure cart state is always correct
    event.respondWith(
        fetch(event.request).catch(() => caches.match(event.request))
    );
});
