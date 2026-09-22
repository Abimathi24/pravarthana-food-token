# PRAVARTHANA 2026 – QR FOOD CLAIM SYSTEM

A complete production-ready web application for managing food claims during a college symposium using QR codes.

## Features
- Secure admin login dashboard.
- Generate unique, secure QR food tokens for registered participants.
- In-browser HTML5 QR scanner using the device camera.
- Atomic claims handling to prevent double scanning/race conditions.
- Real-time dashboard statistics.

## Tech Stack
- Frontend: HTML5, CSS3, Bootstrap 5, JavaScript (Vanilla/Fetch API)
- Backend: Python 3, Flask, Flask-Login
- Database: MongoDB Atlas (PyMongo)

## Local Installation

1. Clone the repository and navigate into it.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate # Mac/Linux
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   Copy `.env.example` to `.env` and fill in your MongoDB URI and Admin Email.
5. Run the application:
   ```bash
   python app.py
   ```
6. Visit `http://localhost:5000` in your browser.

## Deployment to Render

1. Create a GitHub repository and push your code.
2. Create a free MongoDB Atlas database and get the connection string.
3. On Render, create a new "Web Service" and connect your GitHub repository.
4. Set the Build Command:
   ```bash
   pip install -r requirements.txt
   ```
5. Set the Start Command:
   ```bash
   gunicorn app:app
   ```
6. Add your Environment Variables in Render's dashboard (`MONGO_URI`, `MONGO_DB_NAME`, `FLASK_SECRET_KEY`, `ADMIN_EMAIL`, `ADMIN_PASSWORD_HASH`).
7. Deploy the application.

*Note: The QR scanner requires a secure context (HTTPS), which Render provides automatically.*
