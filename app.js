const API_URL = 'https://twofactorauthenticationforloginsecuritya.onrender.com';

// Register a new user
async function register() {
    const username = document.getElementById("reg-username").value;
    const password = document.getElementById("reg-password").value;
    const email = document.getElementById("reg-email").value;

    const response = await fetch(`${API_URL}/register`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password, email })
    });

    if (response.ok) {
        alert("Registration successful! You can now log in.");
        window.location.href = "login.html";
    } else {
        const error = await response.json();
        alert(error.error);
    }
}


// Log in the user
async function login() {
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;

    const response = await fetch(`${API_URL}/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    });

    if (response.ok) {
        const data = await response.json();
        sessionStorage.setItem("username", username);
        window.location.href = "verify.html";
    } else {
        const error = await response.json();
        alert(error.error);
    }
}

// Verify OTP
async function verifyOtp() {
    const username = sessionStorage.getItem("username");
    const otp = document.getElementById("otp").value;

    const response = await fetch(`${API_URL}/verify-otp`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, otp })
    });

    if (response.ok) {
        alert("OTP verified! Login successful.");
        window.location.href = "dashboard.html";
    } else {
        const error = await response.json();
        alert(error.error);
    }
}
function logout() {
    // Clear session storage
    sessionStorage.clear();
    alert("You have been logged out.");
    window.location.href = "login.html"; // Redirect to login page
}

document.addEventListener("DOMContentLoaded", () => {
    if (window.location.pathname.endsWith("dashboard.html")) {
        const username = sessionStorage.getItem("username");
        if (!username) {
            alert("No active session found. Please log in again.");
            window.location.href = "login.html";
        }
    }
});
