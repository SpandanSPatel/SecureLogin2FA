from flask import Flask, request, jsonify
import bcrypt
import pyotp
import json
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
    
USER_DATA_FILE = 'user_data.json'

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

# Load user data
user_data = load_user_data()

# Routes
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username in user_data:
        return jsonify({"error": "User already exists!"}), 400

    hashed_password = hash_password(password)
    secret_key = pyotp.random_base32()
    user_data[username] = {"password": hashed_password, "secret_key": secret_key}
    save_user_data(user_data)

    return jsonify({"message": "User registered successfully!", "secret_key": secret_key}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username not in user_data or not verify_password(password, user_data[username]['password']):
        return jsonify({"error": "Invalid username or password!"}), 401

    # Generate OTP
    secret_key = user_data[username]['secret_key']
    totp = pyotp.TOTP(secret_key)
    otp = totp.now()
    return jsonify({"message": "Login successful!"}), 200

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    username = data.get('username')
    otp = data.get('otp')

    if username not in user_data:
        return jsonify({"error": "Invalid user!"}), 401

    secret_key = user_data[username]['secret_key']
    totp = pyotp.TOTP(secret_key)
    if totp.verify(otp):
        return jsonify({"message": "OTP verified successfully!"}), 200
    return jsonify({"error": "Invalid OTP!"}), 400

if __name__ == '__main__':
    # Get the port from the environment variable, default to 5000
    port = int(os.environ.get("PORT", 5000))
    # Bind to 0.0.0.0 to make the app accessible externally
    app.run(host="0.0.0.0", port=port)
