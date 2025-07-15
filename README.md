# St. Edward Ministry Finder  
© 2024-2025 Harnisch LLC  

This repository is shared with St. Edward Catholic Church & School for their exclusive use.

An interactive, mobile-first web app that helps parishioners quickly discover the best ways to get involved in the St. Edward Catholic community.

**Live site:** <https://involvement-quiz.onrender.com>

---

## Highlights

• Five-question adaptive quiz (2-3 minutes)  
• Personalised ministry recommendations for adults **and** children  
• Admin dashboard with CSV export & basic contact management  
• Privacy-first design – no mandatory log-ins, zero third-party trackers  
• Built-in safeguards: rate-limiting, HTTPS enforcement, admin auth

---

## Quick Start (Local Dev)

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

## Required Environment Variables

| Key | Purpose |
|-----|---------|
| `DATABASE_URL` | Postgres connection string (leave blank for local dev) |
| `SECRET_KEY`   | Flask session secret |
| `ADMIN_USERNAME` & `ADMIN_PASSWORD` | Basic-Auth credentials for `/admin` |

For production deploys **all** variables must be set; the app will refuse to start if defaults are detected.

---

## Deployment Notes

The project is container-ready and known to run on Render.com (free tier) and Fly.io.  A sample `Dockerfile` can be provided on request.

Key reminders:
1.  Use a Postgres add-on or external cluster.  
2.  Set the environment variables above plus any analytics endpoints you enable.  
3.  Disable Flask debug mode (`DEBUG=false`, handled automatically when `DATABASE_URL` is present).

---

## Support & Licensing

This codebase is made available for the ministry work of **St. Edward Church & School (Nashville, TN)**.  
If you wish to adapt or reuse any part of it, please reach out so we can chat about licensing options.

For feature requests, onboarding help, or licensing inquiries, contact **Eric Harnisch**  
<eric@ericharnisch.com>
