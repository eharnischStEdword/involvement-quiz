# St. Edward Ministry Finder

An interactive web application that helps parishioners discover ministries matching their age, interests, and life situation through a celebratory quiz experience.

🌐 **Live Application:** [https://involvement-quiz.onrender.com](https://involvement-quiz.onrender.com)

## 🌟 Overview

The St. Edward Ministry Finder is a production-ready quiz application that guides parishioners through 4-5 personalized questions to match them with relevant ministries at St. Edward Church in Nashville. The app features a celebratory user experience with confetti animations and provides anonymous analytics for parish leadership.

### Key Features

- **Interactive Quiz Flow** with smart question adaptation based on user responses
- **40+ Ministries** with direct contact links and meeting details
- **Multi-Select Support** for life situations and interests
- **Celebratory UX** with confetti animation upon completion
- **Mobile-First Design** optimized for all devices
- **Anonymous Analytics** tracking without collecting personal data
- **Optional Contact Form** for follow-up by ministry coordinators
- **Secure Admin Dashboard** with password protection and CSV export
- **Rate Limiting** protection (5 submissions per hour per IP)

## 🏗️ Technical Architecture

### Stack
- **Backend:** Flask (Python 3.11.9) with PostgreSQL database
- **Frontend:** Server-rendered templates with vanilla JavaScript
- **Hosting:** Render.com (web service + PostgreSQL)
- **Repository:** GitHub (private repository)

### Security Features
- Ministry data stored server-side (not exposed in client code)
- HTTP Basic Auth for admin dashboard
- Rate limiting for form submissions
- Input validation and sanitization
- Anonymous data collection (no PII required)

## 📁 Project Structure

```
st-edward-ministry-finder/
├── app/
│   ├── __init__.py          # App initialization
│   ├── ministries.py        # Ministry database (server-side)
│   ├── models.py            # Database models and connections
│   ├── routes.py            # Flask routes and API endpoints
│   └── utils.py             # Helper functions (auth, rate limiting)
├── templates/
│   └── index.html           # Main quiz template
├── static/
│   ├── css/
│   │   ├── styles.css       # Main CSS (imports other files)
│   │   ├── variables.css    # CSS variables and theming
│   │   ├── layout.css       # Page structure and header
│   │   ├── components.css   # Reusable UI components
│   │   ├── quiz.css         # Quiz-specific styles
│   │   ├── results.css      # Results page styles
│   │   └── animations.css   # Animations and transitions
│   └── js/
│       ├── quiz.js          # Quiz logic and flow
│       ├── confetti.js      # Celebration animation
│       └── ministries.js    # Empty (data moved server-side)
├── requirements.txt         # Python dependencies
├── .python-version         # Python 3.11.9
└── README.md              # This file
```

## 🎯 Quiz Flow

The quiz adapts based on user responses:

1. **Age Group** → Determines available ministries and question flow
2. **Gender** (optional) → For gender-specific ministries
3. **State in Life** (multi-select, skipped for youth) → Single, Married, Parent combinations
4. **Situation** (multi-select) → New to parish, returning, etc.
5. **Interests** (multi-select) → Fellowship, service, prayer, education, music, support
6. **Results** → Personalized recommendations with celebration

### Smart Features
- Youth (infant through high school) skip the state-in-life question
- Parents see separate sections for adult and children's ministries
- "New to St. Edward" situation triggers welcome ministry display
- Multi-select allows realistic combinations (e.g., "Married + Parent")

## 🚀 Deployment Guide

### Prerequisites
- Python 3.11.9
- PostgreSQL database
- GitHub account
- Render.com account

### Environment Variables

Set these in your Render web service:

```bash
DATABASE_URL=postgresql://...  # Render provides this
ADMIN_USERNAME=your_admin_user
ADMIN_PASSWORD=secure_password_here
SECRET_KEY=your-secret-key-here
```

### Deploy to Render

1. **Database Setup**
   - Create a PostgreSQL database on Render
   - Note the connection string

2. **Web Service Setup**
   - Connect your GitHub repository
   - Choose Python 3 environment
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

3. **Configure Environment**
   - Add all environment variables
   - Set instance type (free tier works)

4. **Deploy**
   - Render will auto-deploy on GitHub pushes
   - Monitor logs for any issues

## 📊 Admin Dashboard

Access the admin dashboard at `/admin` with HTTP Basic Auth credentials.

### Features
- **Real-time Statistics**: Total submissions, last 24h/7d activity
- **Visual Analytics**: Charts for ministries, demographics, interests
- **Data Export**: Download CSV for further analysis
- **Data Management**: Clear all data with safety confirmation

### Analytics Tracked
- Age group distribution
- Gender breakdown (with "show all" option)
- State in life combinations
- User situations
- Interest categories
- Most popular ministries
- Submission timestamps

## 🛠️ Local Development

### Setup

```bash
# Clone repository
git clone https://github.com/eharnischStEdward/involvement-quiz.git
cd involvement-quiz

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="your-postgres-url"
export ADMIN_USERNAME="admin"
export ADMIN_PASSWORD="password"

# Run application
python app.py
```

The app will be available at `http://localhost:5000`

## 🔧 Configuration

### Adding/Updating Ministries

Edit `app/ministries.py`:

```python
'ministry-key': {
    'name': 'Ministry Name',
    'description': 'Brief description',
    'details': 'Contact info with <a href="...">links</a>',
    'age': ['age-groups'],        # Required
    'gender': ['male', 'female'],  # Optional
    'state': ['single', 'married', 'parent'],  # Optional
    'interest': ['fellowship', 'service', etc],  # Required
    'situation': ['new-to-stedward']  # Optional
}
```

### Customizing Styles

The CSS is modular - edit individual files in `static/css/`:
- `variables.css` - Colors, spacing, typography
- `components.css` - Buttons, cards, forms
- `quiz.css` - Quiz-specific elements
- `results.css` - Results page styling

## 🐛 Recent Fixes & Updates

### July 2025 Updates
- ✅ **Multi-select state logic**: Proper "married + parent" combinations
- ✅ **Gender icons**: Font Awesome restroom icons (fa-male/fa-female)
- ✅ **CSS gradients**: Clean single-color gradients (green-to-green)
- ✅ **Welcome ministry**: Shows only when "New to St. Edward" selected
- ✅ **Code protection**: Ministry data moved server-side
- ✅ **Parent/children separation**: Clear ministry categorization

## 📈 Performance

- **Lighthouse Score**: 95+ mobile/desktop
- **Load Time**: <2 seconds on 3G
- **Database**: Optimized queries with indexes
- **Caching**: Static assets cached separately
- **Keep-Alive**: Prevents cold starts during business hours

## 🤝 Contributing

Since this is a private repository for St. Edward Church:

1. Contact the parish office for access
2. Create feature branches for new work
3. Test thoroughly before merging
4. Update documentation as needed

## 📞 Support

**Parish Office**: (615) 833-5520  
**Email**: support@stedward.org  
**Website**: [stedward.org](https://stedward.org)

---

**Built with ❤️ for the St. Edward Church community**

*"Through Love, Serve One Another" - Galatians 5:13*
