# St. Edward Ministry Finder  
© 2024-2025 Harnisch LLC  

This repository is shared with St. Edward Catholic Church & School for their exclusive use.

An interactive, mobile-first web app that helps parishioners quickly discover the best ways to get involved in the St. Edward Catholic community.

**Live site:** <https://involvement-quiz.onrender.com>

---

## 🎯 **Project Status**

**Current State:** ✅ Production-ready with excellent core functionality  
**Last Updated:** July 2025  
**Status:** All major issues resolved, admin dashboard fully functional, ready for Phase 2 features

### **✅ Completed Features**
- **Quiz System**: 5-question adaptive flow (Age → Gender → State → Situation → Interests)
- **Ministry Matching**: Algorithm matches users to 37+ relevant ministries
- **Results Display**: Personalized recommendations with ministry details
- **Database Integration**: PostgreSQL with auto-migration
- **Production Deployment**: Running on Render.com with auto-deploy
- **PWA Features**: Service worker, offline capability, install prompts
- **Admin Dashboard**: CSV export, analytics, submission management, engagement tracking
- **Security**: Rate limiting, HTTPS, input validation, admin auth

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

| Key | Purpose | Required |
|-----|---------|----------|
| `DATABASE_URL` | Postgres connection string | Production only |
| `SECRET_KEY`   | Flask session secret | Production only |
| `ADMIN_USERNAME` & `ADMIN_PASSWORD` | Basic-Auth credentials for `/admin` | Production only |

For production deploys **all** variables must be set; the app will refuse to start if defaults are detected.

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

## 🚀 **Deployment**

The project is container-ready and known to run on Render.com (free tier) and Fly.io.

**Key reminders:**
1. Use a Postgres add-on or external cluster
2. Set all environment variables
3. Disable Flask debug mode (handled automatically when `DATABASE_URL` is present)

---

## 📁 **Project Structure**

```
involvement-quiz/
├── app/                    # Main application package
│   ├── blueprints/        # Flask blueprints (routes)
│   ├── config.py          # Configuration management
│   ├── database.py        # Database connection pool
│   ├── models.py          # Database models/schema
│   ├── ministries.py      # Ministry data
│   └── validators.py      # Input validation system
├── static/                # Static assets (CSS, JS, icons)
├── templates/             # HTML templates
├── tests/                 # Test suite
├── docs/                  # Technical documentation
├── scripts/               # Utility scripts
└── main.py               # Application entry point
```

---

## 📊 **Current Performance**

- **Page Load Time**: <2 seconds
- **API Response Time**: <500ms
- **Database Queries**: Optimized with connection pooling
- **Uptime**: High (Render.com reliability)
- **Ministries Loaded**: 37 active ministries

---

## 🔧 **Technical Stack**

### **Backend**
- **Framework**: Flask (Python)
- **Database**: PostgreSQL with connection pooling
- **Caching**: In-memory (Redis disabled for simplicity)
- **Deployment**: Render.com with auto-deploy

### **Frontend**
- **Framework**: Vanilla JavaScript
- **PWA**: Service worker, manifest, offline support
- **Styling**: CSS with responsive design

---

## 📋 **Recent Improvements**

### **✅ Resolved Issues**
- **Type Checking**: All 10 type checking issues fixed
- **Dependencies**: Missing packages (`redis`, `psutil`) installed
- **Validation**: Backend now accepts frontend data formats
- **Rate Limiting**: Increased to 20 submissions per hour
- **Admin Dashboard**: Fixed URL routing issues and JavaScript timing
- **Memory Leaks**: Fixed unbounded cache growth and monitoring data accumulation
- **PWA**: Fixed "Go Back to Interests" button functionality
- **Email Collection**: Removed PII collection for privacy compliance

### **🔧 Code Quality**
- Comprehensive input validation system
- Proper error handling and logging
- Type annotations and documentation
- Test coverage for critical functions

---

## 📞 **Support & Licensing**

This codebase is made available for the ministry work of **St. Edward Church & School (Nashville, TN)**.  
If you wish to adapt or reuse any part of it, please reach out so we can chat about licensing options.

For feature requests, onboarding help, or licensing inquiries, contact **Eric Harnisch**  
<eric@ericharnisch.com>

---

## 📚 **Additional Documentation**

- [Development Guide](docs/development.md) - Technical development details
- [Deployment Guide](docs/deployment.md) - Deployment instructions
- [Troubleshooting](docs/troubleshooting.md) - Common issues and solutions
