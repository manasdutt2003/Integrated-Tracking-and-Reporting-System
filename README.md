# Integrated Tracking and Reporting System

A bus fleet tracker for VIT day scholars. Students can look up their route,
open the live-tracking link for their bus, subscribe to email updates and ask
an AI assistant about routes.

## Features

- **Route search** across 40 buses by route number, area or vehicle number,
  filtering as you type, with a live-tracking link where one exists
- **AI assistant** (Google Gemini) that answers from the real route table
- **Email notifications** through Gmail SMTP
- **Accounts** with hashed passwords and signed session cookies
- **Feedback form**

## Tech stack

Flask, Jinja2 templates, Tailwind CSS (CDN), Google Generative AI SDK.

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # fill in what you need
flask --app app run --debug
```

Open http://127.0.0.1:5000. Demo accounts: `user1` / `pass123` and
`admin` / `adminpass` (change them with `DEMO_USER_PASSWORD` and
`ADMIN_PASSWORD`).

Flask does not read `.env` by itself unless `python-dotenv` is installed;
either install it or export the variables in your shell.

## Configuration

| Variable | Needed for | Notes |
| --- | --- | --- |
| `FLASK_SECRET_KEY` | production | Signs sessions. If unset, a temporary key is generated at start-up, which breaks sessions across restarts and across multiple workers. |
| `GEMINI_API_KEY` | AI assistant | The chat page reports "not configured" without it |
| `EMAIL_USER`, `EMAIL_PASS` | notifications | Gmail address and an [app password](https://myaccount.google.com/apppasswords) |
| `LIVE_TRACKING_URL` | optional | Link appended to notification emails |
| `FLASK_ENV=production` | production | Marks the session cookie as HTTPS-only |

## Deploy

```bash
gunicorn app:app
```

## Project layout

| Path | Purpose |
| --- | --- |
| `app.py` | Routes, authentication, chat endpoint |
| `send_notification.py` | SMTP email helper |
| `data/buses.json` | Route, vehicle and tracking-link data served at `/api/buses` |
| `templates/`, `static/` | Pages and assets |
| `Login.side`, `Search.side` | Selenium IDE recordings from the original static prototype. They point at local `file://` paths and need re-targeting before they can run against the Flask app. |

## Limitations

- Accounts are two in-memory demo users; there is no registration or database.
- Feedback messages are logged, not stored.
- Live location comes from the fleet provider's tracking links, not from this app.

## Automation

`n8n/bus-assistant-webhook.json` is an importable [n8n](https://n8n.io) workflow that exposes the assistant as a webhook. See `n8n/README.md`.
