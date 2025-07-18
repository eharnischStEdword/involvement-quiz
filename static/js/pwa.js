// St. Edward Ministry Finder PWA Registration
// © 2024–2025 Harnisch LLC. All Rights Reserved.

class PWA {
    constructor() {
        this.swRegistration = null;
        this.isInstalled = false;
        this.init();
    }

    async init() {
        // Check if service workers are supported
        if (!('serviceWorker' in navigator)) {
            console.log('Service Worker not supported');
            return;
        }

        // Check if PWA is already installed
        this.checkInstallation();

        // Register service worker
        await this.registerServiceWorker();

        // Set up install prompt
        this.setupInstallPrompt();

        // Set up online/offline detection
        this.setupConnectionDetection();
    }

    async registerServiceWorker() {
        try {
            this.swRegistration = await navigator.serviceWorker.register('/static/sw.js', {
                scope: '/'
            });

            console.log('Service Worker registered successfully:', this.swRegistration);

            // Handle service worker updates
            this.swRegistration.addEventListener('updatefound', () => {
                const newWorker = this.swRegistration.installing;
                newWorker.addEventListener('statechange', () => {
                    if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                        this.showUpdateNotification();
                    }
                });
            });

            // Handle service worker controller change
            navigator.serviceWorker.addEventListener('controllerchange', () => {
                console.log('Service Worker controller changed');
                window.location.reload();
            });

        } catch (error) {
            console.error('Service Worker registration failed:', error);
        }
    }

    setupInstallPrompt() {
        let deferredPrompt;

        window.addEventListener('beforeinstallprompt', (e) => {
            // Prevent the mini-infobar from appearing on mobile
            e.preventDefault();
            
            // Stash the event so it can be triggered later
            deferredPrompt = e;
            
            // Show install button if not already installed
            if (!this.isInstalled) {
                this.showInstallButton();
            }
        });

        // Handle successful installation
        window.addEventListener('appinstalled', () => {
            console.log('PWA was installed');
            this.isInstalled = true;
            this.hideInstallButton();
            
            // Track installation
            if (typeof gtag !== 'undefined') {
                gtag('event', 'pwa_installed', {
                    'event_category': 'engagement',
                    'event_label': 'PWA Installation'
                });
            }
        });
    }

    showInstallButton() {
        // Create install button if it doesn't exist
        if (!document.getElementById('pwa-install-btn')) {
            const installBtn = document.createElement('button');
            installBtn.id = 'pwa-install-btn';
            installBtn.className = 'pwa-install-btn';
            installBtn.innerHTML = `
                <span class="pwa-icon">📱</span>
                <span class="pwa-text">Install App</span>
            `;
            installBtn.addEventListener('click', () => this.installPWA());
            
            // Add to page
            document.body.appendChild(installBtn);
            
            // Add styles
            this.addInstallButtonStyles();
        }
    }

    hideInstallButton() {
        const installBtn = document.getElementById('pwa-install-btn');
        if (installBtn) {
            installBtn.remove();
        }
    }

    async installPWA() {
        if (window.deferredPrompt) {
            window.deferredPrompt.prompt();
            
            const { outcome } = await window.deferredPrompt.userChoice;
            console.log(`User response to the install prompt: ${outcome}`);
            
            window.deferredPrompt = null;
        }
    }

    addInstallButtonStyles() {
        if (!document.getElementById('pwa-styles')) {
            const style = document.createElement('style');
            style.id = 'pwa-styles';
            style.textContent = `
                .pwa-install-btn {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    background: #005921;
                    color: white;
                    border: none;
                    border-radius: 50px;
                    padding: 12px 20px;
                    font-size: 14px;
                    font-weight: 600;
                    cursor: pointer;
                    box-shadow: 0 4px 12px rgba(0, 89, 33, 0.3);
                    z-index: 1000;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    transition: all 0.3s ease;
                    animation: slideIn 0.3s ease;
                }

                .pwa-install-btn:hover {
                    background: #00843D;
                    transform: translateY(-2px);
                    box-shadow: 0 6px 16px rgba(0, 89, 33, 0.4);
                }

                .pwa-icon {
                    font-size: 16px;
                }

                .pwa-text {
                    white-space: nowrap;
                }

                @keyframes slideIn {
                    from {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }

                @media (max-width: 768px) {
                    .pwa-install-btn {
                        bottom: 15px;
                        right: 15px;
                        padding: 10px 16px;
                        font-size: 13px;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }

    showUpdateNotification() {
        // Create update notification
        const notification = document.createElement('div');
        notification.className = 'pwa-update-notification';
        notification.innerHTML = `
            <div class="update-content">
                <span class="update-icon">🔄</span>
                <span class="update-text">New version available</span>
                <button class="update-btn" onclick="window.location.reload()">Update</button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Add styles
        if (!document.getElementById('pwa-update-styles')) {
            const style = document.createElement('style');
            style.id = 'pwa-update-styles';
            style.textContent = `
                .pwa-update-notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: #005921;
                    color: white;
                    border-radius: 8px;
                    padding: 12px 16px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                    z-index: 1000;
                    animation: slideDown 0.3s ease;
                }

                .update-content {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }

                .update-icon {
                    font-size: 16px;
                }

                .update-text {
                    font-size: 14px;
                    font-weight: 500;
                }

                .update-btn {
                    background: rgba(255, 255, 255, 0.2);
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 12px;
                    cursor: pointer;
                    transition: background 0.2s ease;
                }

                .update-btn:hover {
                    background: rgba(255, 255, 255, 0.3);
                }

                @keyframes slideDown {
                    from {
                        transform: translateY(-100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateY(0);
                        opacity: 1;
                    }
                }
            `;
            document.head.appendChild(style);
        }
        
        // Auto-hide after 10 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 10000);
    }

    checkInstallation() {
        // Check if running in standalone mode (installed)
        if (window.matchMedia('(display-mode: standalone)').matches || 
            window.navigator.standalone === true) {
            this.isInstalled = true;
            console.log('PWA is installed and running in standalone mode');
        }
    }

    setupConnectionDetection() {
        // Show offline indicator
        window.addEventListener('offline', () => {
            this.showOfflineIndicator();
        });

        window.addEventListener('online', () => {
            this.hideOfflineIndicator();
        });

        // Check initial connection status
        if (!navigator.onLine) {
            this.showOfflineIndicator();
        }
    }

    showOfflineIndicator() {
        if (!document.getElementById('offline-indicator')) {
            const indicator = document.createElement('div');
            indicator.id = 'offline-indicator';
            indicator.className = 'offline-indicator';
            indicator.innerHTML = `
                <span class="offline-icon">📡</span>
                <span class="offline-text">You're offline</span>
            `;
            
            document.body.appendChild(indicator);
            
            // Add styles
            if (!document.getElementById('offline-styles')) {
                const style = document.createElement('style');
                style.id = 'offline-styles';
                style.textContent = `
                    .offline-indicator {
                        position: fixed;
                        top: 0;
                        left: 0;
                        right: 0;
                        background: #ff6b35;
                        color: white;
                        text-align: center;
                        padding: 8px;
                        font-size: 14px;
                        font-weight: 500;
                        z-index: 1001;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        gap: 8px;
                    }

                    .offline-icon {
                        font-size: 16px;
                    }
                `;
                document.head.appendChild(style);
            }
        }
    }

    hideOfflineIndicator() {
        const indicator = document.getElementById('offline-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    // Method to manually trigger background sync
    async syncData() {
        if (this.swRegistration && 'sync' in window.ServiceWorkerRegistration.prototype) {
            try {
                await this.swRegistration.sync.register('quiz-submission');
                console.log('Background sync registered');
            } catch (error) {
                console.error('Background sync registration failed:', error);
            }
        }
    }
}

// Initialize PWA when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.pwa = new PWA();
});

// Also initialize immediately if DOM is already loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.pwa = new PWA();
    });
} else {
    window.pwa = new PWA();
} 