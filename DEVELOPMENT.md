# St. Edward Ministry Finder - Development Guide

## 📋 Table of Contents
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Environment Setup](#environment-setup)
- [Database Management](#database-management)
- [Testing](#testing)
- [PWA Setup & Troubleshooting](#pwa-setup--troubleshooting)
- [Deployment](#deployment)
- [Keep-Alive Service](#keep-alive-service)
- [Recent Improvements](#recent-improvements)

---

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone <repo-url> involvement-quiz && cd involvement-quiz
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Environment setup
cp .env.example .env  # Edit with your values

# 3. Run locally
python main.py
```

Visit `http://localhost:5000` in your browser.

---

## 📁 Project Structure

```
involvement-quiz-3/
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
│   ├── routes.py          # Legacy routes (to be removed)
│   ├── utils.py           # Utility functions
│   └── validators.py      # Input validation system
├── static/                # Static assets
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript files
│   └── icons/            # PWA icons
├── templates/             # HTML templates
├── tests/                 # Test suite
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
└── sw.js                # Service worker (PWA)
```

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
python run_tests.py

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

## 🚀 Deployment

### Render.com (Recommended)

1. **Connect Repository**: Link your GitHub repo
2. **Environment Variables**: Set all required variables
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `gunicorn main:app`

### Environment Variables for Production

```bash
DATABASE_URL=postgresql://user:pass@host:port/db
SECRET_KEY=your-secure-secret-key
ADMIN_USERNAME=admin_username
ADMIN_PASSWORD=secure_admin_password
```

### Health Checks

The app provides health check endpoints:
- `/health`: Basic health check
- `/api/health`: API health check

---

## 🔄 Keep-Alive Service

### Purpose

Prevents the app from sleeping on Render.com's free tier by making periodic requests.

### Configuration

- **Business Hours** (6 AM - 11 PM): Pings every 5 minutes
- **Off Hours**: Pings every 15 minutes
- **Multiple Endpoints**: Tries `/api/health`, `/`, `/health`

### Monitoring

```bash
# Check keep-alive logs
python monitor.py
```

### Customization

Edit the keep-alive function in `main.py` to adjust:
- Ping intervals
- Target URLs
- Time zones

---

## ✨ Recent Improvements

### 1. Input Validation System

**What**: Comprehensive data validation and sanitization
**Files**: `app/validators.py`
**Benefits**: 
- Prevents SQL injection
- Ensures data integrity
- Validates all user inputs

### 2. Error Recovery System

**What**: Robust error handling and graceful degradation
**Files**: `app/error_handlers.py`
**Benefits**:
- App doesn't crash on errors
- User-friendly error messages
- Comprehensive logging

### 3. Testing Infrastructure

**What**: Automated test suite with proper setup
**Files**: `tests/`, `run_tests.py`
**Benefits**:
- Automated testing
- Regression prevention
- Confidence in changes

### 4. Database Connection Pool

**What**: Efficient database connection management
**Files**: `app/database.py`
**Benefits**:
- Better performance
- Connection reuse
- Automatic cleanup

### 5. Application Factory Pattern

**What**: Improved application structure and testing
**Files**: `app/__init__.py`, `main.py`
**Benefits**:
- Better testing isolation
- Cleaner configuration management
- Easier deployment

### 6. Database Migration System

**What**: Proper schema management and versioning
**Files**: `app/migrations.py`
**Benefits**:
- Safe schema changes
- Version tracking
- Rollback capability

### 7. Enhanced Logging System

**What**: Structured logging with proper formatting
**Files**: `app/logging_config.py`
**Benefits**:
- Better debugging
- Performance monitoring
- Audit trails

### 8. Redis Caching System

**What**: High-performance caching with fallback
**Files**: `app/cache.py`
**Benefits**:
- Faster response times
- Reduced database load
- Graceful degradation

---

## 🔧 Quick Wins (Next Steps)

### Phase 1: Critical Stability (1-2 weeks) ✅ COMPLETED

1. ✅ **Remove duplicate `routes.py`** - Consolidate all routes into blueprints
2. ✅ **Fix database connection duplication** - Use only the connection pool
3. ⚠️ **Add proper `.env.example`** - Document all required environment variables (blocked by global ignore)
4. 🔄 **Standardize error responses** - Use the error handler system everywhere (partially done)

### Phase 2: Structure (2-3 weeks) ✅ COMPLETED

5. ✅ **Implement application factory pattern** - Better testing and configuration
6. ✅ **Add database migrations** - Proper schema management
7. ✅ **Enhance logging** - Structured logging with log levels

### Phase 3: Functionality (3-4 weeks) 🔄 IN PROGRESS

8. ✅ **Implement Redis caching** - Better performance
9. **Enhance rate limiting** - Redis-based rate limiting
10. **Add monitoring** - Application performance monitoring

### Phase 4: Advanced Features (4-6 weeks)

11. **Add comprehensive testing** - Unit, integration, and end-to-end tests
12. **Implement API versioning** - Backward compatibility
13. **Add performance monitoring** - Application metrics and alerts
14. **Security hardening** - Additional security measures

---

## 🆘 Support

### Getting Help

- **Documentation**: Check this file first
- **Issues**: Create GitHub issues for bugs
- **Questions**: Contact the development team

### Common Issues

1. **Database Connection**: Check `DATABASE_URL` and network connectivity
2. **PWA Not Working**: Verify HTTPS and service worker registration
3. **Tests Failing**: Ensure test environment is properly configured

### Development Tips

- Use `python run_tests.py` to verify your changes
- Check logs for detailed error information
- Test PWA functionality on actual mobile devices
- Use the `/pwa-test` endpoint for debugging

---

*Last updated: December 2024* 