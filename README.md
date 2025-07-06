# St. Edward Ministry Finder

An interactive web application to help parishioners find ministries that match their age, interests, and life situation.

## Features

- Interactive quiz with 4 questions
- Comprehensive ministry database
- Email capture for follow-up
- Admin dashboard to view submissions
- PostgreSQL database integration
- Responsive design

## Files Structure

```
st-edward-ministry-finder/
├── app.py              # Flask backend
├── index.html          # Frontend quiz
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Deployment on Render.com

### 1. Set up PostgreSQL Database

1. Go to [Render.com](https://render.com) and create an account
2. Click "New +" → "PostgreSQL"
3. Choose a name (e.g., "st-edward-ministries-db")
4. Select the free tier
5. Click "Create Database"
6. Copy the "External Database URL" from the database dashboard

### 2. Deploy the Web Service

1. Push your code to a GitHub repository
2. On Render, click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `st-edward-ministry-finder`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free tier

### 3. Set Environment Variables

In your web service settings, add these environment variables:

- **DATABASE_URL**: (paste the External Database URL from step 1)

### 4. Deploy

Click "Create Web Service" and wait for deployment to complete.

## Local Development

### Prerequisites

- Python 3.8+
- PostgreSQL (optional for local testing)

### Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd st-edward-ministry-finder
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
export DATABASE_URL="your-database-url-here"
```

5. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Features

### Quiz Flow
- Age group selection
- Gender (optional)
- State in life (optional)
- Interests

### Ministry Matching
The system matches users to ministries based on:
- Age appropriateness
- Gender-specific programs (when applicable)
- Life situation compatibility
- Interest alignment

### Admin Dashboard
Access `/admin` to view all submissions (consider adding authentication for production)

### API Endpoints

- `GET /` - Serves the main quiz interface
- `POST /api/submit` - Submits quiz results and email
- `GET /api/submissions` - Returns all submissions (admin)
- `GET /admin` - Admin dashboard

## Customization

### Adding New Ministries

Edit the `ministries` object in `index.html` to add new ministries:

```javascript
'new-ministry': {
    name: 'Ministry Name',
    description: 'Short description',
    details: 'Meeting times and details',
    age: ['age-groups-that-can-participate'],
    gender: ['male', 'female'], // optional
    state: ['single', 'married', 'parent'], // optional
    interest: ['relevant-interests']
}
```

### Email Integration

To automatically send emails to users and/or parish staff, add email functionality to the `/api/submit` endpoint in `app.py`. Consider using services like SendGrid, AWS SES, or similar.

## Security Considerations

- Add authentication for the admin dashboard
- Implement rate limiting for form submissions
- Add CSRF protection
- Validate and sanitize all user inputs
- Use HTTPS in production (Render provides this automatically)

## Support

For questions about the application, contact the parish office at (615) 833-5520 or email support@stedward.org.
