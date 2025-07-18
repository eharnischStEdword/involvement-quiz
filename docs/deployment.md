# Deployment Guide

## 🚀 Deployment Options

### Render.com (Recommended)

The app is optimized for Render.com and includes built-in keep-alive functionality.

#### Setup Steps

1. **Create a new Web Service**
   - Connect your GitHub repository
   - Select the main branch
   - Choose Python as the runtime

2. **Configure Environment Variables**
   ```
   DATABASE_URL=postgresql://user:password@host:port/database
   SECRET_KEY=your-secret-key-here
   ADMIN_USERNAME=your-admin-username
   ADMIN_PASSWORD=your-admin-password
   ```

3. **Add PostgreSQL Database**
   - Create a new PostgreSQL service
   - Copy the connection string to `DATABASE_URL`
   - The app will auto-migrate the database on first run

4. **Deploy Settings**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Auto-Deploy**: Enabled (recommended)

#### Render.com Features

- **Auto-deploy**: Updates automatically when you push to main
- **SSL**: Automatic HTTPS certificates
- **Custom domains**: Support for custom domain names
- **Logs**: Built-in logging and monitoring

### Fly.io

Alternative deployment option with global edge locations.

#### Setup Steps

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Create App**
   ```bash
   fly launch
   ```

3. **Add PostgreSQL**
   ```bash
   fly postgres create
   fly postgres attach <database-name>
   ```

4. **Deploy**
   ```bash
   fly deploy
   ```

### Docker Deployment

For containerized deployments, create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "main.py"]
```

## ⚙️ Environment Configuration

### Required Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | Flask session secret | `your-secret-key-here` |
| `ADMIN_USERNAME` | Admin dashboard username | `admin` |
| `ADMIN_PASSWORD` | Admin dashboard password | `secure-password` |

### Optional Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `FLASK_ENV` | Flask environment | `production` |
| `DEBUG` | Debug mode | `False` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Environment Validation

The app validates environment variables on startup:

```python
# Production validation
if DATABASE_URL:
    # Production mode - all variables required
    required_vars = ['SECRET_KEY', 'ADMIN_USERNAME', 'ADMIN_PASSWORD']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {missing_vars}")
```

## 🗄️ Database Setup

### PostgreSQL Requirements

- **Version**: PostgreSQL 12 or higher
- **Extensions**: No special extensions required
- **Connection**: SSL recommended for production

### Auto-Migration

The app automatically creates tables on startup:

```python
# In app/models.py
def init_db():
    """Initialize database tables"""
    with get_db_connection() as (conn, cur):
        # Create tables if they don't exist
        cur.execute('''
            CREATE TABLE IF NOT EXISTS ministry_submissions (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                email VARCHAR(255),
                age_group VARCHAR(50),
                gender VARCHAR(20),
                state_in_life JSONB,
                interest VARCHAR(50),
                situation JSONB,
                recommended_ministries TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(45)
            )
        ''')
```

### Database Backup

For production databases, set up regular backups:

```bash
# Render.com PostgreSQL backup
# Automatic backups are enabled by default

# Manual backup
pg_dump $DATABASE_URL > backup.sql

# Restore
psql $DATABASE_URL < backup.sql
```

## 🔒 Security Considerations

### HTTPS

- **Render.com**: Automatic HTTPS certificates
- **Fly.io**: Automatic HTTPS with Let's Encrypt
- **Custom domains**: Ensure SSL certificates are configured

### Rate Limiting

The app includes built-in rate limiting:

```python
# 20 submissions per hour per IP address
RATE_LIMIT_REQUESTS = 20
RATE_LIMIT_WINDOW = 3600  # 1 hour
```

### Input Validation

All user inputs are validated:

```python
from app.validators import validate_and_respond

validated_data, error_response = validate_and_respond(data)
if error_response:
    return error_response
```

### Admin Authentication

Admin dashboard uses HTTP Basic Auth:

```python
# Environment variables required
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
```

## 📊 Monitoring & Health Checks

### Health Check Endpoints

The app provides health check endpoints:

- `/health` - Basic health check
- `/api/health` - API health check with database connectivity
- `/api/rate-limit-info` - Rate limiting information

### Built-in Monitoring

```python
# In main.py
def keep_alive():
    """Keep-alive service to prevent sleeping"""
    while True:
        try:
            response = requests.get(f"{url}/api/health", timeout=15)
            logger.info(f"Keep-alive ping: {response.status_code}")
        except Exception as e:
            logger.error(f"Keep-alive failed: {e}")
        time.sleep(300)  # 5 minutes
```

### External Monitoring

Use the external monitoring script for additional reliability:

```bash
# Run on separate service
python scripts/monitor.py
```

## 🔧 Troubleshooting

### Common Issues

#### Database Connection Errors

```bash
# Check database connectivity
python -c "
import os
import psycopg2
conn = psycopg2.connect(os.environ['DATABASE_URL'])
print('Database connection successful')
"
```

#### Environment Variable Issues

```bash
# Check environment variables
python -c "
import os
required = ['DATABASE_URL', 'SECRET_KEY', 'ADMIN_USERNAME', 'ADMIN_PASSWORD']
for var in required:
    print(f'{var}: {bool(os.environ.get(var))}')
"
```

#### Port Issues

Ensure the app binds to the correct port:

```python
# In main.py
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

### Logs

Check application logs for errors:

```bash
# Render.com
# View logs in the Render dashboard

# Fly.io
fly logs

# Local development
tail -f app.log
```

## 🚀 Performance Optimization

### Database Optimization

- Connection pooling (already implemented)
- Index optimization for ministry lookups
- Query optimization for analytics

### Caching

- In-memory caching for ministry data
- Service worker caching for static assets
- Browser caching for CSS/JS files

### CDN

Consider using a CDN for static assets:

- Cloudflare (free tier available)
- AWS CloudFront
- Render.com CDN

## 📈 Scaling Considerations

### Horizontal Scaling

The app is stateless and can be scaled horizontally:

- Multiple instances behind a load balancer
- Shared database (PostgreSQL)
- Session storage (if needed, use Redis)

### Database Scaling

For high traffic:

- Read replicas for analytics queries
- Connection pooling optimization
- Query optimization and indexing

### Monitoring at Scale

- Application performance monitoring (APM)
- Error tracking (Sentry)
- Log aggregation (ELK stack) 