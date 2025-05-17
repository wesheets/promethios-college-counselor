"""
College Counselor Web Application - Main Flask App

This is the main entry point for the College Counselor web application.
It handles routing, template rendering, and API communication.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import os
import requests
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuration
API_URL = os.environ.get('API_URL', 'http://localhost:5000')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')

# Mock user data for demo purposes
USERS = {
    'student': {'password': 'password', 'role': 'student', 'name': 'John Smith'},
    'counselor': {'password': 'password', 'role': 'counselor', 'name': 'Dr. Jane Doe'},
    'admin': {'password': 'password', 'role': 'admin', 'name': 'Admin User'}
}

# Routes
@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in USERS and USERS[username]['password'] == password:
            session['user'] = username
            session['role'] = USERS[username]['role']
            session['name'] = USERS[username]['name']
            return redirect(url_for('profile'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Handle user logout."""
    session.clear()
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    """Render the user profile page."""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    return render_template('profile.html')

@app.route('/journal')
def journal():
    """Render the journal page."""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # In a real app, we would fetch journal entries from the API
    mock_entries = [
        {
            'id': 1,
            'date': '2025-05-10',
            'title': 'College Application Anxiety',
            'content': 'I\'m feeling overwhelmed by all the college applications...',
            'emotion': 'anxious'
        },
        {
            'id': 2,
            'date': '2025-05-12',
            'title': 'Campus Visit',
            'content': 'Visited State University today and loved the campus...',
            'emotion': 'excited'
        }
    ]
    
    return render_template('journal.html', entries=mock_entries)

@app.route('/colleges')
def colleges():
    """Render the colleges page."""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # In a real app, we would fetch college data from the API
    mock_colleges = [
        {
            'id': 1,
            'name': 'Ivy University',
            'location': 'Massachusetts',
            'trust_score': 85,
            'category': 'Reach'
        },
        {
            'id': 2,
            'name': 'State University',
            'location': 'California',
            'trust_score': 92,
            'category': 'Target'
        },
        {
            'id': 3,
            'name': 'Liberal Arts College',
            'location': 'Vermont',
            'trust_score': 78,
            'category': 'Target'
        }
    ]
    
    return render_template('colleges.html', colleges=mock_colleges)

@app.route('/report')
def report():
    """Render the comprehensive report page."""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    return render_template('report.html')

@app.route('/settings')
def settings():
    """Render the settings page."""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    return render_template('settings.html')

@app.route('/health')
def health():
    """Health check endpoint for Render."""
    return jsonify({'status': 'healthy', 'environment': ENVIRONMENT})

@app.route('/api-proxy/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_proxy(endpoint):
    """Proxy requests to the API service."""
    if request.method == 'GET':
        response = requests.get(f"{API_URL}/{endpoint}")
    elif request.method == 'POST':
        response = requests.post(f"{API_URL}/{endpoint}", json=request.json)
    elif request.method == 'PUT':
        response = requests.put(f"{API_URL}/{endpoint}", json=request.json)
    elif request.method == 'DELETE':
        response = requests.delete(f"{API_URL}/{endpoint}")
    
    return jsonify(response.json()), response.status_code

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    logger.error(f"Server error: {e}")
    return render_template('500.html'), 500

if __name__ == '__main__':
    # This is used when running locally
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=ENVIRONMENT == 'development')
