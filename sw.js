// St. Edward Ministry Finder Service Worker
// © 2024–2025 Harnisch LLC. All Rights Reserved.

const CACHE_NAME = 'st-edward-ministry-finder-v1.0.0';
const STATIC_CACHE = 'static-cache-v1.0.0';
const DYNAMIC_CACHE = 'dynamic-cache-v1.0.0';

// Files to cache immediately
const STATIC_FILES = [
  '/',
  '/static/css/styles.css',
  '/static/css/quiz.css',
  '/static/css/results.css',
  '/static/css/animations.css',
  '/static/css/components.css',
  '/static/css/layout.css',
  '/static/css/variables.css',
  '/static/js/quiz.js',
  '/static/js/confetti.js',
  '/static/site.webmanifest',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
  'https://cdn.jsdelivr.net/npm/chart.js'
];

// Install event - cache static files
self.addEventListener('install', event => {
  console.log('Service Worker: Installing...');
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => {
        console.log('Service Worker: Caching static files');
        return cache.addAll(STATIC_FILES);
      })
      .then(() => {
        console.log('Service Worker: Static files cached');
        return self.skipWaiting();
      })
      .catch(error => {
        console.error('Service Worker: Error caching static files:', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('Service Worker: Activating...');
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
              console.log('Service Worker: Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('Service Worker: Activated');
        return self.clients.claim();
      })
  );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Skip admin routes (don't cache admin pages)
  if (url.pathname.startsWith('/admin')) {
    return;
  }

  // Handle API requests
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleApiRequest(request));
    return;
  }

  // Handle static assets
  if (url.pathname.startsWith('/static/') || url.pathname.startsWith('https://cdn')) {
    event.respondWith(handleStaticRequest(request));
    return;
  }

  // Handle HTML pages
  if (request.headers.get('accept').includes('text/html')) {
    event.respondWith(handleHtmlRequest(request));
    return;
  }
});

// Handle API requests - network first, cache fallback
async function handleApiRequest(request) {
  try {
    // Try network first
    const networkResponse = await fetch(request);
    
    // Cache successful responses
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('Service Worker: Network failed for API request, trying cache');
    
    // Fallback to cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline response for ministry data
    if (request.url.includes('/api/get-ministries')) {
      return new Response(JSON.stringify({
        error: 'Offline mode - ministry data not available',
        offline: true
      }), {
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    throw error;
  }
}

// Handle static assets - cache first, network fallback
async function handleStaticRequest(request) {
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.log('Service Worker: Static asset not found in cache and network failed');
    throw error;
  }
}

// Handle HTML pages - network first, cache fallback
async function handleHtmlRequest(request) {
  try {
    // Try network first
    const networkResponse = await fetch(request);
    
    // Cache successful responses
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('Service Worker: Network failed for HTML request, trying cache');
    
    // Fallback to cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline page
    return caches.match('/static/offline.html');
  }
}

// Background sync for quiz submissions
self.addEventListener('sync', event => {
  if (event.tag === 'quiz-submission') {
    console.log('Service Worker: Background sync for quiz submission');
    event.waitUntil(syncQuizSubmissions());
  }
});

// Sync quiz submissions when back online
async function syncQuizSubmissions() {
  try {
    const cache = await caches.open(DYNAMIC_CACHE);
    const requests = await cache.keys();
    const quizRequests = requests.filter(req => 
      req.url.includes('/api/submit') && req.method === 'POST'
    );
    
    for (const request of quizRequests) {
      try {
        const response = await fetch(request);
        if (response.ok) {
          await cache.delete(request);
          console.log('Service Worker: Synced quiz submission');
        }
      } catch (error) {
        console.error('Service Worker: Failed to sync quiz submission:', error);
      }
    }
  } catch (error) {
    console.error('Service Worker: Error during background sync:', error);
  }
}

// Push notifications (for future use)
self.addEventListener('push', event => {
  if (event.data) {
    const data = event.data.json();
    const options = {
      body: data.body,
      icon: '/static/icons/icon-192.png',
      badge: '/static/icons/icon-72.png',
      vibrate: [100, 50, 100],
      data: {
        dateOfArrival: Date.now(),
        primaryKey: 1
      }
    };
    
    event.waitUntil(
      self.registration.showNotification(data.title, options)
    );
  }
});

// Notification click handler
self.addEventListener('notificationclick', event => {
  event.notification.close();
  
  event.waitUntil(
    clients.openWindow('/')
  );
}); 