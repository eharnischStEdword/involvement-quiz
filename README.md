# St. Edward Ministry Finder  
© 2024-2025 Harnisch LLC  

This repository is shared with St. Edward Catholic Church & School for their exclusive use.

An interactive, mobile-first web app that helps parishioners quickly discover the best ways to get involved in the St. Edward Catholic community.

**Live site:** <https://involvement-quiz.onrender.com>

---

## 🎯 **Project Status**

**Current State:** ✅ Production-ready with excellent core functionality  
**Last Updated:** July 2025  
**Status:** All major issues resolved, memory leaks fixed, security enhanced, ready for Phase 2 features

### **✅ Completed Features**
- **Quiz System**: 5-question adaptive flow (Age → Gender → State → Situation → Interests)
- **Ministry Matching**: Algorithm matches users to 37+ relevant ministries
- **Results Display**: Personalized recommendations with ministry details
- **Database Integration**: PostgreSQL with auto-migration and connection pooling
- **Production Deployment**: Running on Render.com with auto-deploy
- **PWA Features**: Service worker, offline capability, install prompts
- **Admin Dashboard**: CSV export, analytics, submission management, engagement tracking
- **Security**: Rate limiting, HTTPS, input validation, admin auth, session management
- **Performance**: Memory leak fixes, efficient caching, optimized monitoring system
- **Monitoring**: Health checks, memory tracking, performance metrics, remote monitoring
- **CPU Optimization**: Reduced monitoring overhead, optimized keep-alive service

### **🚀 Next Phase Goals**
- Enhanced analytics and tracking
- Advanced admin interface features
- Performance optimizations

---

## 🚀 **Quick Start (Local Dev)**

```bash
# 1 – Clone (read-only)
$ git clone <private-repo-URL> involvement-quiz && cd involvement-quiz

# 2 – Python env / dependencies (Python 3.11+)
$ python -m venv .venv && source .venv/bin/activate
$ pip install -r requirements.txt

# 3 – Environment
$ cp .env.example .env   # then edit values (see below)

# 4 – Run
$ python main.py
```
Visit <http://localhost:5000> in your browser.

---

## ⚙️ **Environment Variables**

| Key | Purpose | Required | Default |
|-----|---------|----------|---------|
| `DATABASE_URL` | Postgres connection string | Production only | - |
| `SECRET_KEY`   | Flask session secret (min 32 chars) | Production only | - |
| `ADMIN_USERNAME` | Basic-Auth username for `/admin` | Production only | - |
| `ADMIN_PASSWORD` | Basic-Auth password (min 8 chars) | Production only | - |
| `SESSION_TIMEOUT` | Admin session timeout in seconds | No | 3600 (1 hour) |

**Security Notes:**
- All production variables must be set; app will refuse to start if defaults are detected
- SECRET_KEY must be at least 32 characters long
- ADMIN_PASSWORD must be at least 8 characters long
- SESSION_TIMEOUT range: 900s (15 min) to 86400s (24 hours)

---

## 🗄️ **Database Management**

The app uses PostgreSQL with connection pooling and auto-migration:

```python
# Get a connection from the pool
with get_db_connection() as (conn, cur):
    cur.execute("SELECT * FROM ministries")
    results = cur.fetchall()
```

Database schema is managed in `app/models.py` and auto-creates tables on startup.

---

## 🧪 **Testing**

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test files
python -m pytest tests/test_validators.py -v
python -m pytest tests/test_api.py -v

# Run with coverage
python -m pytest --cov=app tests/
```

---

## 📱 **PWA Features**

- **Service Worker**: Offline functionality and caching
- **Web Manifest**: App metadata and install prompts
- **Install Prompts**: Automatic "Add to Home Screen" prompts
- **Offline Support**: Cached resources for offline use

### **Troubleshooting PWA**
- Visit `/pwa-test` for debugging info
- Ensure HTTPS connection (required)
- Clear browser cache if issues persist

---

## 🔒 **Security Features**

### **Authentication & Authorization**
- **Admin Auth**: Basic authentication with rate limiting
- **Session Management**: Configurable session timeouts
- **CSRF Protection**: Token-based protection for state-changing operations
- **Rate Limiting**: Login attempt tracking with automatic cleanup

### **Input Validation & Sanitization**
- **Request Validation**: Comprehensive input validation
- **SQL Injection Protection**: Parameterized queries
- **XSS Protection**: Content Security Policy headers
- **Data Sanitization**: All user inputs are validated and sanitized

### **Privacy Protection**
- **No PII Collection**: Application does not collect email addresses or personal information
- **Anonymous Submissions**: All quiz submissions are anonymous
- **Minimal Data**: Only collects necessary data for ministry matching

---

## 📊 **Monitoring & Performance**

### **Health Checks**
```bash
# Basic health check
curl https://involvement-quiz.onrender.com/api/health

# Memory status
curl https://involvement-quiz.onrender.com/api/memory-status

# Performance metrics
curl https://involvement-quiz.onrender.com/api/metrics
```

### **Memory Monitoring**
```bash
# Monitor memory usage remotely
python scripts/memory_monitor.py --interval 30 --duration 3600

# Monitor indefinitely with default 60-second intervals
python scripts/memory_monitor.py

# Monitor a different URL
python scripts/memory_monitor.py --url https://your-app.onrender.com
```

### **Performance Metrics**
- **Memory Usage**: Typically 100-500MB (down from 2GB+)
- **CPU Usage**: Optimized from 90-100% to normal levels
- **Response Times**: < 200ms average
- **Cache Efficiency**: 50MB limit with automatic cleanup
- **Database Connections**: Pooled with timeouts
- **Monitoring Overhead**: Reduced by ~80% through optimized intervals

---

## 🛠️ **Development Tools**

### **Memory Monitoring Script**
```bash
# Monitor for 1 hour with 30-second intervals
python scripts/memory_monitor.py --interval 30 --duration 3600

# Monitor indefinitely with default 60-second intervals
python scripts/memory_monitor.py

# Monitor a different URL
python scripts/memory_monitor.py --url https://your-app.onrender.com
```

**Features:**
- Remote monitoring via API endpoints
- Statistical analysis and memory growth detection
- Automatic data logging to JSON files
- Real-time alerts for potential memory issues

### **Database Debugging**
```bash
# Check database status
curl https://involvement-quiz.onrender.com/api/debug/submissions

# Check ministry data
curl https://involvement-quiz.onrender.com/api/debug/mass
```

---

## 📚 **Documentation**

- **[Memory Leak Fixes](docs/memory-leak-fixes.md)**: Comprehensive guide to memory optimization
- **[Deployment Guide](docs/deployment.md)**: Production deployment instructions
- **[Development Guide](docs/development.md)**: Local development setup
- **[Troubleshooting](docs/troubleshooting.md)**: Common issues and solutions

---

## 🔧 **Architecture**

### **Flask Blueprint Structure**
```
app/
├── __init__.py          # App factory
├── config.py           # Configuration management
├── database.py         # Database connection pooling
├── cache.py           # Memory-efficient caching
├── monitoring.py      # Performance monitoring
├── auth.py            # Authentication & security
├── models.py          # Database models
├── validators.py      # Input validation
├── utils.py           # Utility functions
└── blueprints/
    ├── public.py      # Public routes
    ├── api.py         # API endpoints
    ├── admin.py       # Admin dashboard
    └── ministry_admin.py # Ministry management
```

### **Key Design Principles**
- **Separation of Concerns**: Clear module boundaries
- **Security First**: Comprehensive input validation and authentication
- **Performance**: Memory-efficient caching, connection pooling, and optimized monitoring
- **Monitoring**: Real-time performance and health tracking with minimal overhead
- **Privacy**: No collection of personal information
- **Resource Efficiency**: Optimized CPU usage and background service management

---

## 📄 **License**

© 2024-2025 Harnisch LLC. All Rights Reserved.  
Licensed exclusively for use by St. Edward Church & School (Nashville, TN).  
Unauthorized use, distribution, or modification is prohibited.
