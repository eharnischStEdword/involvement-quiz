# St. Edward Ministry Finder

Interactive quiz application for ministry discovery at St. Edward Church.

**Live URL:** https://involvement-quiz.onrender.com

## Technical Stack

- Backend: Flask (Python 3.11.9)
- Database: PostgreSQL
- Frontend: HTML/CSS/JavaScript
- Hosting: Render.com

## Features

- 5-question adaptive quiz flow
- 40+ ministries with contact information
- Anonymous analytics tracking
- Admin dashboard with CSV export
- Rate limiting (5 submissions/hour/IP)

## Project Structure

```
app/
├── ministries.py    # Ministry data
├── models.py        # Database models
├── routes.py        # Flask routes
└── utils.py         # Helper functions

templates/
└── index.html       # Main template

static/
├── css/            # Modular stylesheets
└── js/             # Quiz logic
```

## Environment Variables

```
DATABASE_URL=postgresql://...
ADMIN_USERNAME=admin_user
ADMIN_PASSWORD=secure_password
SECRET_KEY=your-secret-key
```

## Deployment

1. Create PostgreSQL database on Render
2. Create web service on Render
3. Set environment variables
4. Deploy from GitHub repository

Build Command: `pip install -r requirements.txt`  
Start Command: `gunicorn app:app`

## Local Development

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Admin Access

Dashboard: `/admin` (HTTP Basic Auth)

## Ministry Configuration

Edit `app/ministries.py` to add/update ministries.

## Support

Parish Office: (615) 833-5520  
Email: support@stedward.org
