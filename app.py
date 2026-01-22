import os
import google.generativeai as genai
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from send_notification import send_email_notification
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')  # Set a secure secret key

# Mock users with hashed passwords
users = {
    "user1": generate_password_hash("pass123"),  # Example regular user (hashed)
    "admin": generate_password_hash("adminpass")  # Admin credentials (hashed)
}

@app.route('/')
def root():
    # Redirect to the home page
    return redirect(url_for('home'))

@app.route('/home')
def home():
    # Main page that links to other parts of the website
    return render_template('home.html')

@app.route('/about')
def about():
    # Renders the About page
    return render_template('about.html')

@app.route('/services')
def services():
    # Renders the Services page
    return render_template('services.html')

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        message = request.form.get('message')
        # In a real app, save 'message' to DB or email it
        flash("Thank you for your feedback! We have received it.", "success")
        return redirect(url_for('feedback'))
    return render_template('feedback.html')

@app.route('/search')
def search():
    # Renders the Search page
    return render_template('search.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Clear any previous flash messages to avoid displaying them on the login page
    if 'login_success' in session or 'logout_message' in session:
        flash('')  # Clear any flash messages that were set in previous requests

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username exists and password matches the hashed version
        if username in users and check_password_hash(users[username], password):
            # Set user session
            session['username'] = username
            flash("Login successful!", "success")  # Success message
            return redirect(url_for('home'))  # Redirect to home page after successful login
        else:
            flash("Invalid username or password.", "error")  # Error message

    return render_template('login.html')

@app.route('/logout')
def logout():
    # Clear the session to log out
    session.pop('username', None)
    flash("You have been logged out.", "info")  # Info message on logout
    return redirect(url_for('home'))  # Redirect to home after logout

@app.route('/profile')
def profile():
    if 'username' not in session:
        flash("Please login to view profile", "error")
        return redirect(url_for('login'))
    return render_template('profile.html', username=session['username'])

@app.route('/send_notification', methods=['POST'])
def send_notification():
    # Get the email address from the form input
    recipient_email = request.form.get('email')

    # Set the email subject and body
    subject = "Bus Schedule Updates"
    body = "You have successfully subscribed to live updates for your bus schedule."

    # Call the email function
    send_email_notification(recipient_email, subject, body)

    flash("Notification sent successfully!", "success")  # Show a success message
    return redirect(url_for('home'))  # Redirect back to home page after sending the notification

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    user_message = request.json.get('message')
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        return jsonify({"response": "Error: GEMINI_API_KEY not configured."}), 500

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Context for the AI about the bus system
        context = """You are a helpful assistant for the VIT Bus Fleet Management System.
        You help students find bus routes and schedules.
        Common routes:
        - Route 2: Aynavaram
        - Route 12: Redhills
        - Route 6: Purasaiwalkam
        - Route 22: MCC
        If asked about a route not listed, politely say you don't have live info but suggested checking the 'Services' page.
        Be concise and friendly.
        """
        
        chat = model.start_chat(history=[
            {"role": "user", "parts": context},
            {"role": "model", "parts": "Understood. I am ready to assist with VIT bus inquiries."}
        ])
        
        response = chat.send_message(user_message)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"response": f"AI Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
