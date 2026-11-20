# Integrated Tracking and Reporting System

A bus fleet tracker for VIT day scholars. Students can look up their route,
open the live-tracking link for their bus, subscribe to email updates and ask
an AI assistant about routes.

## Features

- **Route search** across 40 buses by route number, area or vehicle number,
  filtering as you type, with a live-tracking link where one exists. The same
  filter is available from the API: `/api/buses?q=redhills`
- **AI assistant** (Google Gemini) that answers from the real route table
- **Email notifications** through Gmail SMTP
- **Accounts** with hashed passwords and signed session cookies
- **Feedback form**
- **Health check** at `/healthz`

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

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

The tests use Flask's test client and stub out Gemini, so they need no network
access or API keys.

## Configuration

| Variable | Needed for | Notes |
| --- | --- | --- |
| `FLASK_SECRET_KEY` | production | Signs sessions. If unset, a temporary key is generated at start-up, which breaks sessions across restarts and across multiple workers. |
| `GEMINI_API_KEY` | AI assistant | The chat page reports "not configured" without it |
| `GEMINI_MODEL` | optional | Defaults to `gemini-2.5-flash` |
| `EMAIL_USER`, `EMAIL_PASS` | notifications | Gmail address and an [app password](https://myaccount.google.com/apppasswords) |
| `LIVE_TRACKING_URL` | optional | Link appended to notification emails |
| `SMTP_HOST`, `SMTP_PORT` | optional | Default to `smtp.gmail.com` and `587` |
| `LOG_LEVEL` | optional | Python log level, defaults to `INFO` |
| `FLASK_ENV=production` | production | Marks the session cookie as HTTPS-only |

## Deploy

```bash
gunicorn app:app
```

### Docker

```bash
docker build -t bus-tracker .
docker run --rm -p 8000:8000 \
  -e FLASK_SECRET_KEY=change-me \
  -e GEMINI_API_KEY=your-key \
  bus-tracker
```

The image sets `FLASK_ENV=production`, so the session cookie is HTTPS-only.
When trying it over plain HTTP, add `-e FLASK_ENV=development` or log in will
not stick. Check that it is up with `curl localhost:8000/healthz`.

## Project layout

| Path | Purpose |
| --- | --- |
| `app.py` | Routes, authentication, chat endpoint |
| `send_notification.py` | SMTP email helper |
| `data/buses.json` | Route, vehicle and tracking-link data served at `/api/buses` |
| `templates/`, `static/` | Pages and assets |
| `tests/` | pytest suite |
| `Dockerfile` | Container image running gunicorn |
| `docs/ARCHITECTURE.md` | Components, request flows and design notes |
| `Login.side`, `Search.side` | Selenium IDE recordings from the original static prototype. They point at local `file://` paths and need re-targeting before they can run against the Flask app. |

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for how the pieces fit together.

## Limitations

- Accounts are two in-memory demo users; there is no registration or database.
- Feedback messages are logged, not stored.
- There is no rate limiting on login or chat.
- Live location comes from the fleet provider's tracking links, not from this app.

## Automation

`n8n/bus-assistant-webhook.json` is an importable [n8n](https://n8n.io) workflow that exposes the assistant as a webhook. See `n8n/README.md`.
