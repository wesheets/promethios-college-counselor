"""
API integration for the web application routes.

This module updates the app.py routes to use the API client for data retrieval and processing.
"""

from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
import os
from models import db, init_db, User, UserProfile, JournalEntry
from auth import auth
from api_client import (
    get_college_recommendations, 
    analyze_journal_entry, 
    get_college_details,
    search_colleges,
    generate_report,
    get_emotional_state_history,
    get_trust_score_explanation
)

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///college_counselor.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
init_db(app)

# Register blueprints
app.register_blueprint(auth, url_prefix='/auth')

# Middleware to check if user is logged in
@app.before_request
def check_user_status():
    allowed_routes = ['index', 'static', 'auth.login', 'auth.register', 'auth.reset_password_request']
    if request.endpoint and request.endpoint not in allowed_routes and 'user' not in session:
        return redirect(url_for('auth.login'))

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
        
    user = User.query.filter_by(username=session['user']).first()
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))
        
    profile = user.profile
    
    if request.method == 'POST':
        # Update profile information
        profile.gpa = request.form.get('gpa')
        profile.graduation_year = request.form.get('graduation_year')
        profile.intended_majors = request.form.get('intended_majors')
        profile.location_preference = request.form.get('location_preference')
        profile.size_preference = request.form.get('size_preference')
        profile.setting_preference = request.form.get('setting_preference')
        
        try:
            profile.budget = int(request.form.get('budget', 0))
        except ValueError:
            profile.budget = 0
            
        db.session.commit()
        flash('Profile updated successfully!')
        
    return render_template('profile.html', user=user, profile=profile)

@app.route('/journal', methods=['GET'])
def journal():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
        
    user = User.query.filter_by(username=session['user']).first()
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))
        
    entries = JournalEntry.query.filter_by(user_id=user.id).order_by(JournalEntry.created_at.desc()).all()
    
    # Get emotional state history from API
    emotional_history = get_emotional_state_history(user.id)
    
    return render_template('journal.html', entries=entries, emotional_history=emotional_history)

@app.route('/journal/new', methods=['GET', 'POST'])
def new_journal_entry():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
        
    user = User.query.filter_by(username=session['user']).first()
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        if not content:
            flash('Journal entry content is required.')
            return render_template('journal_entry.html')
        
        # Analyze journal entry using API
        analysis = analyze_journal_entry(user.id, content)
        
        # Create journal entry with analysis results
        entry = JournalEntry(
            user_id=user.id,
            title=title,
            content=content,
            sentiment_score=analysis.get('sentiment_score', 75),
            uncertainty_score=analysis.get('uncertainty_score', 30),
            agitation_score=analysis.get('agitation_score', 20),
            emotion_summary=analysis.get('emotion_summary', "Analysis not available.")
        )
        
        db.session.add(entry)
        db.session.commit()
        
        flash('Journal entry saved successfully!')
        return redirect(url_for('journal'))
        
    return render_template('journal_entry.html')

@app.route('/journal/<entry_id>', methods=['GET'])
def view_journal_entry(entry_id):
    if 'user' not in session:
        return redirect(url_for('auth.login'))
        
    user = User.query.filter_by(username=session['user']).first()
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))
        
    entry = JournalEntry.query.filter_by(id=entry_id, user_id=user.id).first_or_404()
    
    return render_template('journal_entry_view.html', entry=entry)

@app.route('/colleges', methods=['GET'])
def colleges():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
        
    user = User.query.filter_by(username=session['user']).first()
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))
    
    # Get college recommendations from API
    profile_data = user.profile.to_dict() if user.profile else None
    recommendations = get_college_recommendations(user.id, profile_data)
    
    return render_template('colleges.html', colleges=recommendations.get('recommendations', []))

@app.route('/colleges/<college_id>', methods=['GET'])
def college_details(college_id):
    if 'user' not in session:
        return redirect(url_for('auth.login'))
        
    user = User.query.filter_by(username=session['user']).first()
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))
    
    # Get college details from API
    college = get_college_details(college_id)
    
    # Get trust score explanation from API
    trust_score = get_trust_score_explanation(college_id, user.id)
    
    return render_template('college_details.html', college=college, trust_score=trust_score)

@app.route('/colleges/search', methods=['GET', 'POST'])
def college_search():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
        
    user = User.query.filter_by(username=session['user']).first()
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))
    
    results = []
    
    if request.method == 'POST':
        query = request.form.get('query', '')
        filters = {
            'location': request.form.get('location', ''),
            'size': request.form.get('size', ''),
            'setting': request.form.get('setting', '')
        }
        
        # Remove empty filters
        filters = {k: v for k, v in filters.items() if v}
        
        # Search colleges using API
        search_results = search_colleges(query, filters)
        results = search_results.get('colleges', [])
    
    return render_template('college_search.html', results=results)

@app.route('/report', methods=['GET'])
def report():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
        
    user = User.query.filter_by(username=session['user']).first()
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))
    
    # Generate report using API
    report_data = generate_report(user.id)
    
    # If API doesn't have user name, use from database
    if 'student' in report_data and 'name' in report_data['student']:
        if not report_data['student']['name']:
            report_data['student']['name'] = user.name or user.username
    
    return render_template('report.html', report=report_data)

@app.route('/settings', methods=['GET'])
def settings():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
        
    user = User.query.filter_by(username=session['user']).first()
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))
        
    return render_template('settings.html', user=user)

# API proxy routes for frontend JavaScript
@app.route('/api-proxy/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_proxy(endpoint):
    if 'user' not in session:
        return jsonify({'error': True, 'message': 'Authentication required'}), 401
    
    user = User.query.filter_by(username=session['user']).first()
    if not user:
        session.clear()
        return jsonify({'error': True, 'message': 'User not found'}), 401
    
    from api_client import APIClient
    client = APIClient()
    
    if request.method == 'GET':
        result = client.get(endpoint, request.args.to_dict())
    elif request.method == 'POST':
        result = client.post(endpoint, request.get_json())
    elif request.method == 'PUT':
        result = client.put(endpoint, request.get_json())
    elif request.method == 'DELETE':
        result = client.delete(endpoint)
    
    if result.get('error'):
        status_code = result.get('status_code', 500)
        return jsonify(result), status_code
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
