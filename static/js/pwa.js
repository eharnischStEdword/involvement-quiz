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
        // Check if it's iOS
        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
        
        if (isIOS) {
            // For iOS, always show the install button after a delay
            if (!this.isInstalled) {
                setTimeout(() => {
                    this.showInstallButton();
                }, 3000);
            }
        } else {
            // For other platforms, use the beforeinstallprompt event
            window.addEventListener('beforeinstallprompt', (e) => {
                // Prevent the mini-infobar from appearing on mobile
                e.preventDefault();
                
                // Stash the event so it can be triggered later
                window.deferredPrompt = e;
                
                // Show install button if not already installed
                if (!this.isInstalled) {
                    // Add a small delay to avoid showing immediately on page load
                    setTimeout(() => {
                        this.showInstallButton();
                    }, 2000);
                }
            });
        }

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
            
            // Check if it's iOS
            const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
            
            if (isIOS) {
                installBtn.innerHTML = `
                    <span class="pwa-text">Save to Device</span>
                    <span class="pwa-hint">Tap Share → Add to Home Screen</span>
                    <button class="pwa-dismiss-btn" onclick="event.stopPropagation(); this.parentElement.remove(); localStorage.setItem('pwa-install-dismissed', 'true');">×</button>
                `;
                installBtn.addEventListener('click', () => this.showIOSInstructions());
            } else {
                installBtn.innerHTML = `
                    <span class="pwa-text">Save to Device</span>
                `;
                installBtn.addEventListener('click', () => this.installPWA());
            }
            
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

    showIOSInstructions() {
        // Create iOS instructions modal
        const modal = document.createElement('div');
        modal.id = 'ios-instructions-modal';
        modal.className = 'ios-instructions-modal';
        modal.innerHTML = `
            <div class="ios-instructions-content">
                <div class="ios-instructions-header">
                    <h3>💾 Save to Device</h3>
                    <button class="ios-close-btn" onclick="this.parentElement.parentElement.parentElement.remove()">×</button>
                </div>
                <div class="ios-instructions-body">
                    <div class="ios-step">
                        <span class="ios-step-number">1</span>
                        <span class="ios-step-text">Tap the <strong>Share</strong> button <span class="ios-icon">📤</span></span>
                    </div>
                    <div class="ios-step">
                        <span class="ios-step-number">2</span>
                        <span class="ios-step-text">Scroll down and tap <strong>Add to Home Screen</strong></span>
                    </div>
                    <div class="ios-step">
                        <span class="ios-step-number">3</span>
                        <span class="ios-step-text">Tap <strong>Add</strong> to confirm</span>
                    </div>
                </div>
                <div class="ios-instructions-footer">
                    <button class="ios-got-it-btn" onclick="this.parentElement.parentElement.parentElement.remove()">Got it!</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Add styles if not already added
        if (!document.getElementById('ios-instructions-styles')) {
            const style = document.createElement('style');
            style.id = 'ios-instructions-styles';
            style.textContent = `
                .ios-instructions-modal {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(0, 0, 0, 0.8);
                    z-index: 10000;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                    animation: fadeIn 0.3s ease;
                }

                .ios-instructions-content {
                    background: rgba(255, 255, 255, 0.95);
                    backdrop-filter: blur(20px);
                    -webkit-backdrop-filter: blur(20px);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    border-radius: 16px;
                    max-width: 400px;
                    width: 100%;
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
                    animation: slideUp 0.3s ease;
                }

                .ios-instructions-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 20px 20px 0;
                }

                .ios-instructions-header h3 {
                    margin: 0;
                    color: #005921;
                    font-size: 18px;
                    font-weight: 600;
                }

                .ios-close-btn {
                    background: none;
                    border: none;
                    font-size: 24px;
                    color: #666;
                    cursor: pointer;
                    padding: 0;
                    width: 30px;
                    height: 30px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }

                .ios-instructions-body {
                    padding: 20px;
                }

                .ios-step {
                    display: flex;
                    align-items: center;
                    margin-bottom: 16px;
                    gap: 12px;
                }

                .ios-step-number {
                    background: #005921;
                    color: white;
                    width: 24px;
                    height: 24px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 14px;
                    font-weight: 600;
                    flex-shrink: 0;
                }

                .ios-step-text {
                    font-size: 16px;
                    color: #333;
                    line-height: 1.4;
                }

                .ios-icon {
                    font-size: 18px;
                }

                .ios-instructions-footer {
                    padding: 0 20px 20px;
                    text-align: center;
                }

                .ios-got-it-btn {
                    background: #005921;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 24px;
                    font-size: 16px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: background 0.2s ease;
                }

                .ios-got-it-btn:hover {
                    background: #00843D;
                }

                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }

                @keyframes slideUp {
                    from {
                        transform: translateY(20px);
                        opacity: 0;
                    }
                    to {
                        transform: translateY(0);
                        opacity: 1;
                    }
                }

                @media (max-width: 480px) {
                    .ios-instructions-modal {
                        padding: 10px;
                    }
                    
                    .ios-instructions-content {
                        max-width: none;
                    }
                }
            `;
            document.head.appendChild(style);
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
                    background: rgba(0, 89, 33, 0.85);
                    backdrop-filter: blur(20px);
                    -webkit-backdrop-filter: blur(20px);
                    color: white;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 50px;
                    padding: 14px 22px;
                    font-size: 15px;
                    font-weight: 600;
                    cursor: pointer;
                    box-shadow: 0 8px 32px rgba(0, 89, 33, 0.25);
                    z-index: 1000;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 4px;
                    transition: all 0.3s ease;
                    animation: slideIn 0.4s ease;
                    font-family: 'Nunito', sans-serif;
                    min-width: 160px;
                    position: relative;
                }

                .pwa-install-btn:hover {
                    background: rgba(0, 89, 33, 0.95);
                    transform: translateY(-2px);
                    box-shadow: 0 12px 40px rgba(0, 89, 33, 0.35);
                    border-color: rgba(255, 255, 255, 0.3);
                }

                .pwa-install-btn:active {
                    transform: translateY(-1px);
                }

                .pwa-icon {
                    font-size: 18px;
                }

                .pwa-text {
                    white-space: nowrap;
                }

                .pwa-hint {
                    font-size: 11px;
                    opacity: 0.9;
                    white-space: nowrap;
                    font-weight: 400;
                }

                .pwa-dismiss-btn {
                    position: absolute;
                    top: -8px;
                    right: -8px;
                    background: rgba(255, 255, 255, 0.9);
                    color: #666;
                    border: none;
                    border-radius: 50%;
                    width: 20px;
                    height: 20px;
                    font-size: 14px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
                    transition: all 0.2s ease;
                }

                .pwa-dismiss-btn:hover {
                    background: rgba(255, 255, 255, 1);
                    color: #333;
                    transform: scale(1.1);
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
                        padding: 12px 18px;
                        font-size: 14px;
                    }
                    
                    .pwa-icon {
                        font-size: 16px;
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
        
        // For iOS, check if user has dismissed the install button before
        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
        if (isIOS) {
            const hasDismissed = localStorage.getItem('pwa-install-dismissed');
            if (hasDismissed) {
                this.isInstalled = true; // Treat as "installed" to avoid showing again
            }
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