# Architecture

A small Flask application. There is no database; the route data is a JSON file
loaded once at start-up.

## Components

| Component | Responsibility |
| --- | --- |
| `app.py` | Flask app: pages, JSON API, demo authentication, chat endpoint |
| `send_notification.py` | SMTP helper. Returns `True` or `False` and never raises to the caller |
| `data/buses.json` | Route number, area, vehicle number and optional tracking link per bus |
| `templates/`, `static/` | Jinja2 pages and assets |
| `n8n/` | Optional workflow that exposes `/api/chat` as a webhook |
| `tests/` | pytest suite using Flask's test client |

## Request flows

**Route search**: the search page fetches `/api/buses`. `?q=` filters on the
server with `search_buses` (case-insensitive substring on route number, area
and vehicle number).

**Assistant**: `POST /api/chat` validates the message (non-empty, at most 500
characters). It then builds a system prompt from the real route table
(`build_chat_context`) and calls Gemini. The Gemini SDK is imported lazily, so
the app and its tests run without it being called. Without `GEMINI_API_KEY` the
endpoint returns 503. SDK errors are logged and the browser gets a generic 502
message.

**Notifications**: `POST /send_notification` validates the address with a
simple regex, then sends through SMTP with STARTTLS and a 15 second timeout.
Failures are reported to the user as a flash message and logged in detail.

**Authentication**: two demo users are held in memory as password hashes. A
successful login clears the session and sets `username`. `login_required`
guards `/profile`.

**Health**: `GET /healthz` returns `{"status": "ok", "buses": <count>}`.

## Design decisions

- **Data validated at start-up.** `validate_buses` rejects a malformed
  `buses.json` immediately instead of failing later in a request.
- **Configuration through environment variables.** See the table in the
  README. Secrets are never in the image or the repository.
- **Assistant grounded in data.** The prompt contains the actual routes and
  tells the model to say so when it does not know, rather than guess.
- **Errors are not leaked.** Internal exception text goes to the logs only.

## Known limits

- Demo users only; no registration, no persistence.
- Feedback is logged, not stored.
- No rate limiting on login or chat. Add it (for example Flask-Limiter) before
  exposing the app publicly.
- The temporary secret key and in-memory state mean multiple gunicorn workers
  need `FLASK_SECRET_KEY` set so sessions work across them.
- Live location is provided by external tracking links, not by this app.
