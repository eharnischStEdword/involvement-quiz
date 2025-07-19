# Security Documentation - St. Edward Ministry Finder

## Overview

This document outlines the security measures implemented in the St. Edward Ministry Finder application to ensure data protection, user privacy, and system integrity.

## 🔒 **Security Architecture**

### **Defense in Depth**
The application implements multiple layers of security:
1. **Input Validation** - All user inputs are validated and sanitized
2. **Authentication** - Secure admin authentication with rate limiting
3. **Authorization** - Role-based access control
4. **Data Protection** - No collection of personal information
5. **Infrastructure** - HTTPS, secure headers, connection timeouts

---

## 🔐 **Authentication & Authorization**

### **Admin Authentication**
- **Method**: HTTP Basic Authentication
- **Rate Limiting**: 5 attempts per 15 minutes per IP
- **Lockout**: 1 hour lockout after 5 failed attempts
- **Session Management**: Configurable timeout (15 min - 24 hours)
- **Default Timeout**: 1 hour (3600 seconds)

### **Session Security**
```python
# Configurable via environment variable
SESSION_TIMEOUT=3600  # 1 hour in seconds

# Validation ranges
MIN_SESSION_TIMEOUT = 900   # 15 minutes
MAX_SESSION_TIMEOUT = 86400 # 24 hours
```

### **CSRF Protection**
- **Token Generation**: Cryptographically secure random tokens
- **Validation**: Required for all state-changing operations (POST, PUT, DELETE, PATCH)
- **Session Binding**: Tokens are bound to user sessions

---

## 🛡️ **Input Validation & Sanitization**

### **Request Validation**
All API endpoints validate input data using a comprehensive validation system:

```python
# Example validation for quiz submission
validated_data = {
    'age_group': 'elementary',  # Must be from allowed list
    'gender': 'male',           # Must be from allowed list
    'states': ['parent'],       # Array of valid states
    'interests': ['kids'],      # Array of valid interests
    'situation': ['new-parish'] # Array of valid situations
}
```

### **SQL Injection Protection**
- **Parameterized Queries**: All database queries use parameterized statements
- **Connection Pooling**: Secure connection management with timeouts
- **Query Timeouts**: 30-second maximum query execution time

### **XSS Protection**
- **Content Security Policy**: Strict CSP headers implemented
- **Input Sanitization**: All user inputs are sanitized before processing
- **Output Encoding**: Data is properly encoded when displayed

---

## 🔒 **Data Privacy & Protection**

### **No PII Collection**
The application is designed with privacy-first principles:
- ✅ **No email addresses collected**
- ✅ **No names collected** (all submissions are anonymous)
- ✅ **No phone numbers collected**
- ✅ **No addresses collected**
- ✅ **No personal identifiers stored**

### **Data Minimization**
Only essential data is collected for ministry matching:
- Age group (for age-appropriate recommendations)
- Gender (for gender-specific ministries)
- Life situation (parent, student, etc.)
- Interests (prayer, education, kids, etc.)
- IP address (for rate limiting only)

### **Data Retention**
- **Submissions**: Stored indefinitely for ministry insights
- **Admin Sessions**: Automatically expired based on timeout
- **Login Attempts**: Automatically cleaned up after 15 minutes
- **Cache Data**: Automatically expired after TTL

---

## 🏗️ **Infrastructure Security**

### **HTTPS Enforcement**
- **TLS/SSL**: All communications encrypted
- **HSTS**: HTTP Strict Transport Security headers
- **Secure Cookies**: All cookies marked as secure

### **Security Headers**
```python
# Content Security Policy
CSP_HEADERS = {
    'default-src': ["'self'"],
    'script-src': ["'self'", "'unsafe-inline'", "https://www.googletagmanager.com"],
    'style-src': ["'self'", "'unsafe-inline'"],
    'img-src': ["'self'", "data:", "https:"],
    'connect-src': ["'self'"],
    'frame-ancestors': ["'none'"]
}
```

### **Connection Security**
- **Database**: SSL/TLS encryption required
- **Connection Timeouts**: 10-second connection timeout
- **Query Timeouts**: 30-second query timeout
- **Connection Pooling**: Secure connection management

---

## 🔍 **Monitoring & Logging**

### **Security Logging**
All security events are logged:
- Failed login attempts
- Rate limit violations
- Session expirations
- Admin actions
- Error conditions

### **Health Monitoring**
- **Memory Usage**: Real-time monitoring with alerts
- **Response Times**: Performance tracking
- **Error Rates**: Automatic error detection
- **Cache Health**: Memory usage monitoring

### **Security Endpoints**
```bash
# Health check with security status
curl https://involvement-quiz.onrender.com/api/health

# Memory status
curl https://involvement-quiz.onrender.com/api/memory-status

# Performance metrics
curl https://involvement-quiz.onrender.com/api/metrics
```

---

## ⚙️ **Environment Security**

### **Required Environment Variables**
```bash
# Production (all required)
DATABASE_URL=postgresql://...
SECRET_KEY=your-32-character-secret-key
ADMIN_USERNAME=your-admin-username
ADMIN_PASSWORD=your-8-character-password

# Optional
SESSION_TIMEOUT=3600  # Session timeout in seconds
```

### **Security Validation**
The application validates environment variables on startup:
- **SECRET_KEY**: Minimum 32 characters
- **ADMIN_PASSWORD**: Minimum 8 characters
- **No Defaults**: Application refuses to start with default values in production

---

## 🚨 **Security Best Practices**

### **For Administrators**
1. **Strong Passwords**: Use complex passwords (minimum 8 characters)
2. **Session Management**: Log out when finished
3. **Access Control**: Limit admin access to authorized personnel
4. **Monitoring**: Regularly check security logs

### **For Developers**
1. **Input Validation**: Always validate and sanitize user inputs
2. **Error Handling**: Don't expose sensitive information in error messages
3. **Dependencies**: Keep dependencies updated
4. **Code Review**: Review all changes for security implications

### **For Deployment**
1. **Environment Variables**: Set all required environment variables
2. **HTTPS**: Ensure HTTPS is enabled
3. **Monitoring**: Set up monitoring and alerting
4. **Backups**: Regular database backups

---

## 📋 **Security Checklist**

### **Pre-Deployment**
- [ ] All environment variables set
- [ ] Strong SECRET_KEY configured (32+ characters)
- [ ] Strong ADMIN_PASSWORD configured (8+ characters)
- [ ] HTTPS enabled
- [ ] Security headers configured
- [ ] Database SSL enabled

### **Post-Deployment**
- [ ] Health checks passing
- [ ] Memory usage within limits
- [ ] Error rates acceptable
- [ ] Admin authentication working
- [ ] Rate limiting functional
- [ ] Logs being generated

### **Ongoing**
- [ ] Monitor security logs
- [ ] Check for failed login attempts
- [ ] Review performance metrics
- [ ] Update dependencies regularly
- [ ] Backup data regularly

---

## 🔧 **Security Configuration**

### **Rate Limiting**
```python
MAX_LOGIN_ATTEMPTS = 5
LOGIN_WINDOW = 900        # 15 minutes
LOCKOUT_DURATION = 3600   # 1 hour
MAX_TRACKED_IPS = 1000    # Maximum IPs to track
```

### **Session Management**
```python
DEFAULT_SESSION_TIMEOUT = 3600  # 1 hour
MAX_SESSION_TIMEOUT = 86400     # 24 hours
MIN_SESSION_TIMEOUT = 900       # 15 minutes
```

### **Cache Security**
```python
MAX_CACHE_SIZE = 500      # Maximum cache entries
MAX_MEMORY_MB = 50        # Maximum cache memory
CLEANUP_INTERVAL = 60     # Cleanup every 60 seconds
```

---

## 📞 **Security Contact**

For security issues or questions:
- **Email**: eric@ericharnisch.com
- **Response Time**: Within 24 hours
- **Disclosure**: Please report security issues privately

---

## 📄 **Security Policy**

This application follows security best practices and is designed to protect user privacy and data integrity. All security measures are regularly reviewed and updated as needed.

**Last Updated**: July 2025  
**Version**: 1.0 