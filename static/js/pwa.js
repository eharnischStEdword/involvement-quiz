// St. Edward Ministry Finder PWA Registration
// © 2024–2025 Harnisch LLC. All Rights Reserved.

// Global functions for iOS banner
window.showIOSInstructions = function() {
    // Create iOS instructions modal
    const modal = document.createElement('div');
    modal.id = 'ios-instructions-modal';
    modal.className = 'ios-instructions-modal';
    modal.innerHTML = `
        <div class="ios-instructions-content">
            <div class="ios-instructions-header">
                <h3>Save to Home Screen</h3>
                <button class="ios-close-btn" onclick="this.parentElement.parentElement.parentElement.remove()">×</button>
            </div>
            <div class="ios-instructions-body">
                <div class="ios-step">
                    <span class="ios-step-number">1</span>
                    <span class="ios-step-text">Tap the <strong>Share</strong> button</span>
                    <div class="ios-share-icon">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M16 5l-1.42 1.42-1.59-1.59V16h-1.98V4.83L9.42 6.42 8 5l4-4 4 4zm4 5v11c0 1.1-.9 2-2 2H6c-1.11 0-2-.9-2-2V10c0-1.11.89-2 2-2h3v2H6v11h12V10h-3V8h3c1.1 0 2 .89 2 2z"/>
                        </svg>
                    </div>
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
                border-radius: 50%;
                transition: background-color 0.2s;
            }

            .ios-close-btn:hover {
                background-color: #f0f0f0;
            }

            .ios-instructions-body {
                padding: 20px;
            }

            .ios-step {
                display: flex;
                align-items: center;
                margin-bottom: 20px;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 12px;
                border-left: 4px solid #005921;
            }

            .ios-step-number {
                background: #005921;
                color: white;
                width: 30px;
                height: 30px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                margin-right: 15px;
                flex-shrink: 0;
            }

            .ios-step-text {
                flex: 1;
                font-size: 16px;
                line-height: 1.4;
            }

            .ios-share-icon {
                margin-left: 10px;
                color: #005921;
            }

            .ios-instructions-footer {
                padding: 0 20px 20px;
                text-align: center;
            }

            .ios-got-it-btn {
                background: linear-gradient(135deg, #005921, #007a2e);
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .ios-got-it-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 89, 33, 0.3);
            }

            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }

            @keyframes slideUp {
                from { 
                    opacity: 0;
                    transform: translateY(20px);
                }
                to { 
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        `;
        document.head.appendChild(style);
    }
};



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

        // Enhanced logging for debugging
        console.log('PWA Init - User Agent:', navigator.userAgent);
        console.log('PWA Init - Standalone:', window.navigator.standalone);
        console.log('PWA Init - Display Mode:', window.matchMedia('(display-mode: standalone)').matches);

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
            console.log('Attempting to register service worker...');
            console.log('Service Worker support:', 'serviceWorker' in navigator);
            
            // Wait for page to be fully loaded before registering
            if (document.readyState !== 'complete') {
                await new Promise(resolve => {
                    window.addEventListener('load', resolve, { once: true });
                });
            }
            
            this.swRegistration = await navigator.serviceWorker.register('/sw.js', {
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
            // Don't show detailed errors to users - service worker is optional
            // Only log for debugging purposes
        }
    }

    setupInstallPrompt() {
        // Enhanced device detection
        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        const isDesktop = !isMobile;
        const isStandalone = window.navigator.standalone === true || window.matchMedia('(display-mode: standalone)').matches;
        const isInAppBrowser = /FBAN|FBAV|Instagram|Line|WhatsApp|Twitter|LinkedInApp|Snapchat|Pinterest|TikTok/.test(navigator.userAgent);
        
        console.log('PWA Setup - iOS:', isIOS, 'Mobile:', isMobile, 'Desktop:', isDesktop, 'Standalone:', isStandalone);
        
        // Don't show install prompt if already installed or in app browser
        if (isStandalone) {
            console.log('PWA is already installed');
            this.isInstalled = true;
            return;
        }
        
        if (isInAppBrowser) {
            console.log('In app browser detected - skipping install prompt');
            return;
        }
        
        // Don't show install prompt on desktop
        if (isDesktop) {
            console.log('Desktop detected - skipping install prompt');
            return;
        }
        
        if (isIOS) {
            // For iOS, show the install banner after user interaction
            // Wait for user to complete first question to show banner
            document.addEventListener('DOMContentLoaded', () => {
                // Show banner after user interaction or timeout
                let hasInteracted = false;
                
                const showBannerAfterInteraction = () => {
                    if (!hasInteracted && !this.isInstalled) {
                        hasInteracted = true;
                        setTimeout(() => {
                            this.showInstallButton();
                        }, 2000);
                    }
                };
                
                // Listen for any button clicks or interactions
                document.addEventListener('click', showBannerAfterInteraction, { once: true });
                document.addEventListener('touchstart', showBannerAfterInteraction, { once: true });
                
                // Fallback: show after 10 seconds
                setTimeout(() => {
                    if (!hasInteracted && !this.isInstalled) {
                        this.showInstallButton();
                    }
                }, 10000);
            });
        } else if (isMobile) {
            // For mobile (non-iOS), use the beforeinstallprompt event
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
        // Enhanced device detection
        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        const isDesktop = !isMobile;
        
        console.log('PWA Install Button - iOS:', isIOS, 'Mobile:', isMobile, 'Desktop:', isDesktop);
        
        if (isIOS) {
            // For iOS, show the small link under the welcome text
            const mobileSaveLink = document.getElementById('mobileSaveLink');
            if (mobileSaveLink) {
                mobileSaveLink.style.display = 'block';
                console.log('PWA: Showing iOS mobile save link');
            } else {
                console.log('PWA: mobileSaveLink not found in HTML');
            }
        } else if (isMobile && !isDesktop) {
            // For mobile (non-iOS), show the floating button
            if (!document.getElementById('pwa-install-btn')) {
                const installBtn = document.createElement('button');
                installBtn.id = 'pwa-install-btn';
                installBtn.className = 'pwa-install-btn';
                
                installBtn.innerHTML = `
                    <span class="pwa-text">Save to Device</span>
                `;
                installBtn.addEventListener('click', () => this.installPWA());
                
                // Add to page
                document.body.appendChild(installBtn);
                
                // Add styles
                this.addInstallButtonStyles();
                console.log('PWA: Showing mobile install button');
            }
        } else {
            // For desktop, don't show any install button
            console.log('PWA: Desktop detected - not showing install button');
        }
    }

    hideInstallButton() {
        const installBtn = document.getElementById('pwa-install-btn');
        if (installBtn) {
            installBtn.remove();
        }
        
        // Also hide iOS banner and link
        const mobileSaveContainer = document.getElementById('mobileSaveContainer');
        if (mobileSaveContainer) {
            mobileSaveContainer.style.display = 'none';
        }
        
        const mobileSaveLink = document.getElementById('mobileSaveLink');
        if (mobileSaveLink) {
            mobileSaveLink.style.display = 'none';
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
                    <h3>Save to Device</h3>
                    <button class="ios-close-btn" onclick="this.parentElement.parentElement.parentElement.remove()">×</button>
                </div>
                <div class="ios-instructions-body">
                    <div class="ios-step">
                        <span class="ios-step-number">1</span>
                        <span class="ios-step-text">Tap the <strong>Share</strong> button</span>
                        <div class="ios-share-icon">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M16 5l-1.42 1.42-1.59-1.59V16h-1.98V4.83L9.42 6.42 8 5l4-4 4 4zm4 5v11c0 1.1-.9 2-2 2H6c-1.11 0-2-.9-2-2V10c0-1.11.89-2 2-2h3v2H6v11h12V10h-3V8h3c1.1 0 2 .89 2 2z"/>
                            </svg>
                        </div>
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

                .ios-share-icon {
                    width: 24px;
                    height: 24px;
                    background: #007AFF;
                    border-radius: 6px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                    margin-left: auto;
                    flex-shrink: 0;
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

// Make showIOSInstructions globally accessible
window.showIOSInstructions = function() {
    if (window.pwa) {
        window.pwa.showIOSInstructions();
    }
}; 