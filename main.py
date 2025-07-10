# Configure Talisman for HTTPS with proper CSP settings
if os.environ.get('DATABASE_URL'):  # Production
    csp = {
        'default-src': "'self'",
        'script-src': [
            "'self'",
            "'unsafe-inline'",  # Allow inline scripts for event handlers
            "'unsafe-eval'",    # Allow eval for Chart.js
            'https://cdn.jsdelivr.net',
            'https://cdnjs.cloudflare.com',
            'https://www.googletagmanager.com',
            'https://www.google-analytics.com'
        ],
        'style-src': [
            "'self'",
            "'unsafe-inline'",  # Allow inline styles if absolutely needed
            'https://cdnjs.cloudflare.com',
            'https://fonts.googleapis.com'
        ],
        'font-src': [
            "'self'",
            'https://cdnjs.cloudflare.com',
            'https://fonts.gstatic.com'
        ],
        'img-src': [
            "'self'",
            'data:',
            'https:',
            'http:'
        ],
        'connect-src': [
            "'self'",
            'https://www.google-analytics.com'
        ]
    }
    Talisman(app, 
             force_https=True, 
             strict_transport_security=True,
             content_security_policy=csp,
             content_security_policy_nonce_in=['script-src'])  # CHANGED: Only nonce for scripts
