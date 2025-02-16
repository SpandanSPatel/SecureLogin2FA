from flask import Flask, request, jsonify
import bcrypt
import json
import os
from flask_cors import CORS
from email.message import EmailMessage
import smtplib
import ssl
import random

app = Flask(__name__)
CORS(app)

USER_DATA_FILE = 'user_data.json'

# Email configuration
EMAIL_SENDER = 'secure2faotpbot@gmail.com'
EMAIL_PASSWORD = 'uksm hvgd ojzp juov'

# Helper functions
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    return {}

def save_user_data(data):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(data, file)

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def send_email(receiver_email, subject, otp):
    em = EmailMessage()
    em['From'] = EMAIL_SENDER
    em['To'] = receiver_email
    em['Subject'] = subject

    # HTML content for the email
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f9f9f9;
            }}
            .email-container {{
                max-width: 600px;
                margin: 20px auto;
                padding: 20px;
                background-color: #ffffff;
                border: 1px solid #dddddd;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }}
            .email-header {{
                text-align: center;
                padding-bottom: 20px;
            }}
            .otp {{
                font-size: 24px;
                font-weight: bold;
                color: #007bff;
                text-align: center;
                margin: 20px 0;
            }}
            .email-footer {{
                text-align: center;
                font-size: 14px;
                color: #777777;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="email-header">
                <h1>Your OTP Code</h1>
                <p>Please use the following OTP to complete your login:</p>
            </div>
            <div class="otp">{otp}</div>
            <p style="text-align: center;">If you did not request this, please ignore this email.</p>
            <div class="email-footer">
                <p>&copy; 2025 SecureLogin. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    em.set_content(f"Your OTP is: {otp}", subtype="plain")
    em.add_alternative(html_content, subtype="html")  # Add HTML content

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.sendmail(EMAIL_SENDER, receiver_email, em.as_string())


# Load user data
user_data = load_user_data()

# Routes
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if username in user_data:
        return jsonify({"error": "User already exists!"}), 400

    hashed_password = hash_password(password)
    user_data[username] = {"password": hashed_password, "email": email}
    save_user_data(user_data)

    return jsonify({"message": "User registered successfully!"}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username not in user_data or not verify_password(password, user_data[username]['password']):
        return jsonify({"error": "Invalid username or password!"}), 401

    # Generate OTP
    otp = random.randint(100000, 999999)
    user_data[username]['otp'] = otp
    save_user_data(user_data)

    # Send OTP via email
    email = user_data[username]['email']
    send_email(email, "Your OTP Code", f"Your OTP is: {otp}")

    return jsonify({"message": "Login successful! OTP sent to your email."}), 200

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    username = data.get('username')
    otp = int(data.get('otp'))

    if username not in user_data or user_data[username].get('otp') != otp:
        return jsonify({"error": "Invalid OTP!"}), 400

    # Clear OTP after verification
    user_data[username]['otp'] = None
    save_user_data(user_data)

    return jsonify({"message": "OTP verified successfully!"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
