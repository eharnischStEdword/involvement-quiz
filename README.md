# St. Edward Ministry Finder

An interactive quiz application helping parishioners discover ministries that match their interests, age, and life situation at St. Edward Catholic Church.

**Live Application:** https://involvement-quiz.onrender.com

## Features

- 🎯 **Smart Quiz Flow**: 5-question adaptive quiz that skips irrelevant questions based on age
- 🎊 **Celebration UX**: Confetti animation upon quiz completion
- 📊 **Anonymous Analytics**: Track ministry interest without collecting personal data
- 📱 **Mobile Optimized**: Responsive design with 44px touch targets
- 👨‍👩‍👧‍👦 **Family Focused**: Separate recommendations for adult and children's ministries
- 🔒 **Privacy First**: Zero email collection, directs to existing parish systems

## Tech Stack

- **Backend**: Flask (Python 3.11.9)
- **Database**: PostgreSQL with JSONB columns
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Hosting**: Render.com with auto-deployment
- **Security**: Rate limiting (5 submissions/hour/IP), HTTP Basic Auth for admin

## Architecture

```
├── app.py                  # Flask application core
├── main.py                 # Production wrapper with keep-alive
├── templates/
│   ├── index.html         # Quiz interface
│   └── admin.html         # Admin dashboard
├── static/
│   ├── css/               # Modular stylesheets
│   ├── js/                # Quiz logic and confetti
│   └── js/admin.js        # Dashboard functionality
└── app/
    ├── models.py          # Database models
    ├── ministries.py      # Ministry data (52 ministries)
    └── blueprints/        # Route organization
```

## Key Features

### Quiz Logic
- Progressive questions: Age → Gender → State → Situation → Interests
- Multi-select for complex life situations (e.g., "Married + Parent")
- Database-driven ministry matching with fallback to hardcoded data

### Admin Dashboard
- View all submissions and analytics
- Export data to CSV
- Contact request management
- Real-time statistics and charts

## Development

```bash
# Clone repository
git clone https://github.com/eharnischStEdword/involvement-quiz.git

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your values

# Run locally
python app.py
```

## Environment Variables

```
DATABASE_URL=postgresql://...
ADMIN_USERNAME=your_admin_user
ADMIN_PASSWORD=secure_password
SECRET_KEY=your-secret-key
```

## Ministry Database

The application includes 52+ ministries covering:
- Sacraments and worship
- Youth and education programs
- Adult fellowship groups
- Service opportunities
- Family support ministries

Ministries are stored in PostgreSQL and loaded dynamically, with automatic migration on startup.

## Parish Integration

- **Registration**: stedwardnash.flocknote.com/register
- **Website**: stedward.org
- **Contact**: (615) 833-5520

## Contributing

This is a parish-specific application. For similar implementations at other parishes, feel free to fork and adapt.

## License

Copyright © 2025 St. Edward Catholic Church. All rights reserved.
