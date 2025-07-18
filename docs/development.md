# Development Guide

## 📋 Table of Contents
- [Environment Setup](#environment-setup)
- [Project Structure](#project-structure)
- [Database Management](#database-management)
- [Testing](#testing)
- [PWA Setup & Troubleshooting](#pwa-setup--troubleshooting)
- [Keep-Alive Service](#keep-alive-service)

---

## ⚙️ Environment Setup

### Required Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Production only |
| `SECRET_KEY` | Flask session secret | Production only |
| `ADMIN_USERNAME` | Admin dashboard username | Production only |
| `ADMIN_PASSWORD` | Admin dashboard password | Production only |

### Development vs Production

- **Development**: Uses local SQLite, minimal env vars required
- **Production**: Requires all env vars, uses PostgreSQL

### Environment Validation

The app validates environment variables on startup:
- Checks for required variables in production
- Prevents use of default values in production
- Provides clear error messages for missing config

---

## 📁 Project Structure

```
involvement-quiz/
├── app/                    # Main application package
│   ├── blueprints/        # Flask blueprints (routes)
│   │   ├── admin.py       # Admin dashboard routes
│   │   ├── api.py         # API endpoints
│   │   ├── ministry_admin.py  # Ministry management
│   │   └── public.py      # Public pages
│   ├── config.py          # Configuration management
│   ├── database.py        # Database connection pool
│   ├── error_handlers.py  # Error handling system
│   ├── models.py          # Database models/schema
│   ├── ministries.py      # Ministry data
│   ├── utils.py           # Utility functions
│   └── validators.py      # Input validation system
├── static/                # Static assets
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript files
│   └── icons/            # PWA icons
├── templates/             # HTML templates
├── tests/                 # Test suite
├── docs/                  # Technical documentation
├── scripts/               # Utility scripts
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
└── sw.js                # Service worker (PWA)
```

---

## 🗄️ Database Management

### Connection Pool

The app uses a PostgreSQL connection pool for better performance:

```python
# Get a connection from the pool
with get_db_connection() as (conn, cur):
    cur.execute("SELECT * FROM ministries")
    results = cur.fetchall()
```

### Schema Management

Database schema is managed in `app/models.py`:
- Auto-creates tables on startup
- Handles schema migrations safely
- Supports both development and production databases

### Key Tables

- `ministry_submissions`: User quiz responses
- `ministries`: Ministry data and configuration

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test files
python -m pytest tests/test_validators.py -v
python -m pytest tests/test_api.py -v

# Run with coverage
python -m pytest --cov=app tests/
```

### Test Structure

- `tests/test_validators.py`: Input validation tests
- `tests/test_api.py`: API endpoint tests
- `tests/conftest.py`: Test configuration and fixtures

### Test Environment

Tests run in isolation with:
- Mock database connections
- Test-specific environment variables
- No external dependencies

---

## 📱 PWA Setup & Troubleshooting

### PWA Features

- **Service Worker**: `/sw.js` for offline functionality
- **Web Manifest**: `/static/site.webmanifest` for app metadata
- **Install Prompts**: Automatic "Add to Home Screen" prompts
- **Offline Support**: Cached resources for offline use

### Installation Prompts

The app shows install prompts for:
- **Chrome/Edge**: Browser install button
- **Safari**: "Add to Home Screen" instructions
- **Mobile**: Native install prompts

### Troubleshooting PWA Issues

#### "Add to Home Screen" Not Appearing

1. **Check Safari Settings**:
   - Settings → Safari → Advanced → Web Inspector
   - Ensure "Add to Home Screen" is enabled

2. **Verify PWA Requirements**:
   - HTTPS connection (required)
   - Valid web manifest
   - Service worker registered

3. **Test PWA Setup**:
   - Visit `/pwa-test` for debugging info
   - Check browser console for errors

#### Service Worker Issues

```javascript
// Check service worker registration
navigator.serviceWorker.getRegistrations().then(registrations => {
    console.log('Service Workers:', registrations);
});
```

#### Common Fixes

- Clear browser cache and cookies
- Hard refresh (Ctrl+F5 / Cmd+Shift+R)
- Check for HTTPS requirements
- Verify manifest file is accessible

---

## 🔄 Keep-Alive Service

The app includes a built-in keep-alive service to prevent Render.com from sleeping:

```python
# In main.py
def keep_alive():
    """Enhanced keep-alive service to prevent Render from sleeping"""
    # Pings the service every 5-15 minutes depending on time of day
```

### External Monitoring

For additional monitoring, use the external script in `scripts/monitor.py`:

```bash
python scripts/monitor.py
```

This script can run on a separate service (Raspberry Pi, VPS, or cloud function) to keep your Render.com service active.

---

## 🔧 Development Workflow

### Code Quality

- **Type Checking**: Use mypy for type checking
- **Linting**: Follow PEP 8 style guidelines
- **Testing**: Maintain test coverage for critical functions
- **Documentation**: Keep docstrings and comments up to date

### Error Handling

The app uses a comprehensive error handling system:

```python
from app.error_handlers import create_error_response, ValidationError

try:
    # Your code here
    pass
except ValidationError as e:
    error_response, status_code = create_error_response(e)
    return jsonify(error_response), status_code
```

### Logging

Structured logging is configured in `app/logging_config.py`:

```python
import logging
logger = logging.getLogger(__name__)
logger.info("Your log message")
```

---

## 🚀 Performance Optimization

### Database Optimization

- Connection pooling for better performance
- Prepared statements for repeated queries
- Index optimization for ministry lookups

### Frontend Optimization

- Service worker caching for static assets
- Lazy loading for non-critical resources
- Minified CSS and JavaScript in production

### Monitoring

- Health check endpoints for monitoring
- Performance metrics collection
- Error tracking and alerting 