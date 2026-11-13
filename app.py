"""VIT bus fleet tracker: route search, live-tracking links, email
notifications and a Gemini-powered assistant."""

from __future__ import annotations

import json
import logging
import os
import re
import secrets
from functools import wraps
from pathlib import Path

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from send_notification import send_email_notification

BASE_DIR = Path(__file__).resolve().parent
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MAX_CHAT_MESSAGE_LENGTH = 500
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Sessions are signed with this key. Without FLASK_SECRET_KEY a random key is
# generated, which is safe but logs everyone out on restart.
app.secret_key = os.getenv("FLASK_SECRET_KEY") or secrets.token_hex(32)
if not os.getenv("FLASK_SECRET_KEY"):
    logger.warning("FLASK_SECRET_KEY is not set; using a temporary key.")

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.getenv("FLASK_ENV") == "production",
)


def load_buses() -> list[dict]:
    with open(BASE_DIR / "data" / "buses.json", encoding="utf-8") as handle:
        return json.load(handle)


def load_users() -> dict[str, str]:
    """Demo accounts. Override the passwords with environment variables."""
    return {
        "user1": generate_password_hash(os.getenv("DEMO_USER_PASSWORD", "pass123")),
        "admin": generate_password_hash(os.getenv("ADMIN_PASSWORD", "adminpass")),
    }


BUSES = load_buses()
USERS = load_users()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "username" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def build_chat_context() -> str:
    """Give the assistant the real route table so it does not have to guess."""
    lines = [
        f"- Route {bus['route_number']}: {bus['route']} (vehicle {bus['vehicle_number']})"
        for bus in BUSES
    ]
    return (
        "You are a helpful assistant for the VIT Bus Fleet Management System. "
        "You help students find bus routes. Routes with a letter suffix (2A, 3A) "
        "are the second bus on the same route.\n"
        "Known routes:\n" + "\n".join(lines) + "\n"
        "If asked about a route that is not listed, say you do not have it and "
        "suggest the Search page. You do not know live locations or timings; "
        "point users to the live-tracking link on the Search page for those. "
        "Be concise and friendly."
    )


@app.route("/")
def root():
    return redirect(url_for("home"))


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/services")
def services():
    return render_template("services.html")


@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if request.method == "POST":
        message = (request.form.get("message") or "").strip()
        if not message:
            flash("Please write a message before submitting.", "error")
        else:
            # Feedback is only logged. Wire this up to a database or mailbox
            # before relying on it.
            logger.info("Feedback received (%d characters)", len(message))
            flash("Thank you for your feedback! We have received it.", "success")
        return redirect(url_for("feedback"))
    return render_template("feedback.html")


@app.route("/search")
def search():
    return render_template("search.html")


@app.route("/api/buses")
def buses_api():
    return jsonify(BUSES)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        stored_hash = USERS.get(username)
        if stored_hash and check_password_hash(stored_hash, password):
            session.clear()
            session["username"] = username
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        flash("Invalid username or password.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", username=session["username"])


@app.route("/send_notification", methods=["POST"])
def send_notification():
    recipient = (request.form.get("email") or "").strip()
    if not EMAIL_PATTERN.match(recipient):
        flash("Please enter a valid email address.", "error")
        return redirect(url_for("home"))

    sent = send_email_notification(
        recipient,
        "Bus Schedule Updates",
        "You have successfully subscribed to live updates for your bus schedule.",
    )
    if sent:
        flash("Notification sent successfully!", "success")
    else:
        flash("We could not send the email right now. Please try again later.", "error")
    return redirect(url_for("home"))


@app.route("/chat")
def chat():
    return render_template("chat.html")


@app.route("/api/chat", methods=["POST"])
def chat_api():
    payload = request.get_json(silent=True) or {}
    user_message = str(payload.get("message") or "").strip()
    if not user_message:
        return jsonify({"response": "Please type a question."}), 400
    if len(user_message) > MAX_CHAT_MESSAGE_LENGTH:
        return jsonify({"response": "That message is too long. Please shorten it."}), 400

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return jsonify({"response": "The assistant is not configured yet."}), 503

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(GEMINI_MODEL, system_instruction=build_chat_context())
        response = model.generate_content(user_message)
        return jsonify({"response": response.text})
    except Exception:
        # Log the detail, but do not send internal error text to the browser.
        logger.exception("Chat request failed")
        return jsonify({"response": "Sorry, the assistant is unavailable right now."}), 502


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG") == "1")
