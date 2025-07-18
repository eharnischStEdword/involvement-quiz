# Troubleshooting Guide

## 🚨 Common Issues & Solutions

### PWA (Progressive Web App) Issues

#### "Add to Home Screen" Not Appearing

**Symptoms:**
- No install prompt on mobile devices
- "Add to Home Screen" option missing in Safari

**Solutions:**

1. **Check HTTPS Connection**
   ```bash
   # Ensure you're using HTTPS
   curl -I https://your-domain.com
   ```

2. **Verify Web Manifest**
   ```bash
   # Check if manifest is accessible
   curl https://your-domain.com/static/site.webmanifest
   ```

3. **Test PWA Setup**
   - Visit `/pwa-test` for debugging info
   - Check browser console for errors

4. **Safari-Specific Fixes**
   - Settings → Safari → Advanced → Web Inspector
   - Ensure "Add to Home Screen" is enabled
   - Clear browser cache and cookies

#### Service Worker Not Registering

**Symptoms:**
- Offline functionality not working
- Console errors about service worker

**Solutions:**

1. **Check Service Worker File**
   ```bash
   # Verify service worker exists
   curl https://your-domain.com/sw.js
   ```

2. **Clear Service Worker Cache**
   ```javascript
   // In browser console
   navigator.serviceWorker.getRegistrations().then(registrations => {
       registrations.forEach(registration => registration.unregister());
   });
   ```

3. **Hard Refresh**
   - Press `Ctrl+F5` (Windows) or `Cmd+Shift+R` (Mac)
   - Or open in incognito/private window

### Database Issues

#### Connection Errors

**Symptoms:**
- "Database connection failed" errors
- 500 errors on quiz submission

**Solutions:**

1. **Check Database URL**
   ```bash
   # Verify environment variable
   echo $DATABASE_URL
   ```

2. **Test Database Connection**
   ```bash
   python -c "
   import os
   import psycopg2
   try:
       conn = psycopg2.connect(os.environ['DATABASE_URL'])
       print('Database connection successful')
       conn.close()
   except Exception as e:
       print(f'Connection failed: {e}')
   "
   ```

3. **Check Database Status**
   ```bash
   # For Render.com PostgreSQL
   # Check the Render dashboard for database status
   ```

#### Migration Issues

**Symptoms:**
- Tables not created
- "Table does not exist" errors

**Solutions:**

1. **Force Database Initialization**
   ```python
   # In Python console
   from app.models import init_db
   init_db()
   ```

2. **Check Migration Logs**
   ```bash
   # Look for migration errors in logs
   tail -f app.log | grep -i migration
   ```

### Rate Limiting Issues

#### Too Many Requests

**Symptoms:**
- "Rate limit exceeded" errors
- 429 status codes

**Solutions:**

1. **Check Current Rate Limit**
   ```bash
   curl https://your-domain.com/api/rate-limit-info
   ```

2. **Wait for Reset**
   - Rate limit resets every hour
   - Check the `reset_time` in the response

3. **Increase Rate Limit (Development)**
   ```python
   # In app/utils.py
   RATE_LIMIT_REQUESTS = 50  # Increase for testing
   ```

### Admin Dashboard Issues

#### Can't Access Admin Dashboard

**Symptoms:**
- 401 Unauthorized errors
- Login prompt not working

**Solutions:**

1. **Check Environment Variables**
   ```bash
   # Verify admin credentials are set
   echo $ADMIN_USERNAME
   echo $ADMIN_PASSWORD
   ```

2. **Test Authentication**
   ```bash
   # Test with curl
   curl -u username:password https://your-domain.com/admin/api/submissions
   ```

3. **Clear Browser Cache**
   - Clear cookies and cache
   - Try incognito/private window

#### Admin Dashboard Not Showing New Submissions

**Symptoms:**
- Old data only
- New submissions not appearing

**Solutions:**

1. **Hard Refresh Dashboard**
   - Press `Ctrl+F5` (Windows) or `Cmd+Shift+R` (Mac)
   - Check browser console for errors

2. **Check API Endpoint**
   ```bash
   # Test admin API directly
   curl -u username:password https://your-domain.com/admin/api/submissions
   ```

3. **Verify Database Records**
   ```sql
   -- Check if submissions are being recorded
   SELECT COUNT(*) FROM ministry_submissions;
   SELECT * FROM ministry_submissions ORDER BY submitted_at DESC LIMIT 5;
   ```

### Quiz Functionality Issues

#### Quiz Not Loading

**Symptoms:**
- Blank quiz page
- Loading spinner never disappears

**Solutions:**

1. **Check JavaScript Console**
   - Open browser developer tools (F12)
   - Look for JavaScript errors

2. **Verify Static Files**
   ```bash
   # Check if static files are accessible
   curl https://your-domain.com/static/js/quiz.js
   curl https://your-domain.com/static/css/quiz.css
   ```

3. **Check Ministry Data**
   ```bash
   # Verify ministries are loaded
   curl https://your-domain.com/api/ministries
   ```

#### Quiz Submissions Failing

**Symptoms:**
- "Submit" button not working
- No confirmation after quiz completion

**Solutions:**

1. **Check API Endpoint**
   ```bash
   # Test submission endpoint
   curl -X POST https://your-domain.com/api/submit \
     -H "Content-Type: application/json" \
     -d '{"answers":{"age":"college-young-adult","gender":"male"},"states":[],"interests":["prayer"],"situation":[],"ministries":["Test"]}'
   ```

2. **Check Validation**
   - Ensure all required fields are filled
   - Check for validation errors in console

3. **Verify Rate Limiting**
   - Check if you've exceeded the rate limit
   - Wait for the limit to reset

### Performance Issues

#### Slow Page Load

**Symptoms:**
- Pages taking >5 seconds to load
- Timeout errors

**Solutions:**

1. **Check Database Performance**
   ```sql
   -- Check for slow queries
   SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;
   ```

2. **Optimize Static Assets**
   - Enable gzip compression
   - Use CDN for static files
   - Minify CSS/JS files

3. **Check External Dependencies**
   - Verify all external services are responding
   - Check for timeout issues

#### High Memory Usage

**Symptoms:**
- Application crashes
- Slow response times

**Solutions:**

1. **Check Connection Pool**
   ```python
   # Monitor connection pool usage
   from app.database import get_connection_pool
   pool = get_connection_pool()
   print(f"Pool size: {pool.minconn}-{pool.maxconn}")
   ```

2. **Optimize Database Queries**
   - Add database indexes
   - Optimize slow queries
   - Use connection pooling effectively

### Deployment Issues

#### Build Failures

**Symptoms:**
- Deployment fails on Render/Fly
- Build errors in logs

**Solutions:**

1. **Check Requirements**
   ```bash
   # Verify all dependencies are in requirements.txt
   pip freeze > requirements.txt
   ```

2. **Check Python Version**
   ```bash
   # Ensure .python-version is correct
   cat .python-version
   ```

3. **Test Locally**
   ```bash
   # Test the build process locally
   pip install -r requirements.txt
   python main.py
   ```

#### Environment Variable Issues

**Symptoms:**
- "Missing environment variables" errors
- Application won't start

**Solutions:**

1. **Verify All Required Variables**
   ```bash
   # Check environment variables
   python -c "
   import os
   required = ['DATABASE_URL', 'SECRET_KEY', 'ADMIN_USERNAME', 'ADMIN_PASSWORD']
   for var in required:
       print(f'{var}: {bool(os.environ.get(var))}')
   "
   ```

2. **Check Variable Format**
   - Ensure no extra spaces or quotes
   - Verify special characters are escaped
   - Check for typos in variable names

## 🔧 Debugging Tools

### Health Check Endpoints

```bash
# Basic health check
curl https://your-domain.com/health

# API health check with database
curl https://your-domain.com/api/health

# Rate limit information
curl https://your-domain.com/api/rate-limit-info

# Ministry data
curl https://your-domain.com/api/ministries
```

### Log Analysis

```bash
# Check application logs
tail -f app.log

# Filter for errors
grep -i error app.log

# Filter for specific issues
grep -i "database\|connection\|validation" app.log
```

### Database Debugging

```sql
-- Check table structure
\d ministry_submissions

-- Check recent submissions
SELECT * FROM ministry_submissions ORDER BY submitted_at DESC LIMIT 10;

-- Check ministry data
SELECT COUNT(*) FROM ministries;
SELECT * FROM ministries WHERE active = true LIMIT 5;
```

## 📞 Getting Help

### Before Contacting Support

1. **Check this troubleshooting guide**
2. **Review application logs**
3. **Test with minimal data**
4. **Document the exact steps to reproduce**

### Information to Provide

When reporting issues, include:

- **Error messages** (exact text)
- **Steps to reproduce** (detailed)
- **Environment** (browser, OS, device)
- **Logs** (relevant error logs)
- **Screenshots** (if applicable)

### Contact Information

For technical support:
- **Email**: eric@ericharnisch.com
- **Repository**: https://github.com/eharnischStEdword/involvement-quiz
- **Live Site**: https://involvement-quiz.onrender.com 