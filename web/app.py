"""
Integration of the chat interface and system insights dashboard with the main application.

This module updates the app.py file to include the new routes and features.
"""

from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
import os
import re
import sys
import traceback
from datetime import datetime

# Initialize Flask app first, before any other imports or initialization
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')

# Register health check endpoint before any other initialization
# This ensures it's available even if other parts of the app fail to initialize
@app.route('/health')
def health_check():
    # Log health check request for debugging
    print(f"Health check requested from {request.remote_addr}")
    return jsonify({
        "status": "healthy", 
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }), 200

# Diagnostic logging for startup
print(f"Starting application initialization at {datetime.utcnow().isoformat()}")
print(f"Python version: {sys.version}")
print(f"Environment variables: RENDER={os.environ.get('RENDER')}, DATABASE_URL={os.environ.get('DATABASE_URL', 'Not set')}, PORT={os.environ.get('PORT', 'Not set')}")

try:
    # Import models and other dependencies after health check is registered
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
    from emotion_visualization import EmotionVisualization
    from trust_visualization import TrustVisualization
    from college_comparison import CollegeComparisonTool
    from decision_explainer import DecisionExplainer
    from system_insights import SystemInsights

    # Register blueprints
    app.register_blueprint(auth)

    # Database configuration
    # Always use in-memory SQLite unless a valid PostgreSQL URL is provided
    # This ensures the application can start in any environment
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        # Convert postgres:// to postgresql:// for SQLAlchemy 1.4+
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        print(f"Using PostgreSQL database: {database_url}")
    else:
        # Use in-memory SQLite for all other cases to avoid file access issues
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        print(f"Using in-memory SQLite database for deployment")

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize database with error handling
    try:
        init_db(app)
        print("Database initialization completed successfully")
    except Exception as e:
        print(f"WARNING: Database initialization error: {e}")
        traceback.print_exc()
        print("Continuing application startup despite database error")
        
    # Initialize feature modules with error handling
    try:
        # Initialize feature modules
        emotion_viz = EmotionVisualization(None)
        trust_viz = TrustVisualization(None)
        comparison_tool = CollegeComparisonTool(None)
        decision_explainer = DecisionExplainer(None)
        system_insights = SystemInsights(app, db)

        # Register feature routes
        from emotion_visualization import register_emotion_visualization_routes
        from trust_visualization import register_trust_visualization_routes
        from college_comparison import register_college_comparison_routes
        from decision_explainer import register_decision_explainer_routes

        register_emotion_visualization_routes(app, db)
        register_trust_visualization_routes(app, db)
        register_college_comparison_routes(app, db)
        register_decision_explainer_routes(app, db)
        
        print("Feature modules initialized successfully")
    except Exception as e:
        print(f"WARNING: Feature module initialization error: {e}")
        traceback.print_exc()
        print("Continuing application startup with limited features")
        
except Exception as e:
    print(f"ERROR during application initialization: {e}")
    traceback.print_exc()
    print("Application will continue with limited functionality")

# Middleware to check if user is logged in
@app.before_request
def check_user_status():
    # Skip middleware for health check endpoint
    if request.path == '/health':
        return None
        
    allowed_routes = ['index', 'static', 'auth.login', 'auth.register', 'auth.reset_password_request', 'chat_interface']
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
    
    # Create emotion visualization for journal page
    visualizer = EmotionVisualization(entries)
    emotion_summary = visualizer.generate_emotion_summary()
    
    return render_template('journal.html', entries=entries, emotional_history=emotional_history, emotion_summary=emotion_summary)

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
    
    # Get journal entries for emotion visualization
    entries = JournalEntry.query.filter_by(user_id=user.id).order_by(JournalEntry.created_at.desc()).all()
    
    # Create emotion visualization for report page
    visualizer = EmotionVisualization(entries)
    emotion_summary = visualizer.generate_emotion_summary()
    
    return render_template('report.html', report=report_data, emotion_summary=emotion_summary)

@app.route('/settings', methods=['GET'])
def settings():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
        
    user = User.query.filter_by(username=session['user']).first()
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))
        
    return render_template('settings.html', user=user)

# New centralized chat interface
@app.route('/chat', methods=['GET', 'POST'])
def chat_interface():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
        
    user = User.query.filter_by(username=session['user']).first()
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))
    
    # Initialize variables
    selected_college = None
    explanation = None
    query = "How can Promethios help with my college decision?"
    colleges = []
    
    try:
        # Get college recommendations for selection
        profile_data = user.profile.to_dict() if user.profile else {}
        recommendations = get_college_recommendations(user.id, profile_data)
        colleges = recommendations.get('recommendations', [])
        
        if request.method == 'POST':
            query = request.form.get('query', '')
            college_id = request.form.get('college_id', '')
            
            if college_id:
                # Get college details
                selected_college = get_college_details(college_id)
                
                # Initialize explainer
                from api_client import APIClient
                api_client = APIClient()
                explainer = DecisionExplainer(api_client)
                
                # Generate explanation
                explanation = explainer.explain_decision(
                    query=query,
                    student_profile=user.profile.to_dict() if user.profile else {},
                    college=selected_college
                )
    except Exception as e:
        print(f"Error in chat_interface: {e}")
        flash(f"An error occurred: {str(e)}")
        explanation = f"I'm sorry, I encountered an error while processing your request. Please try again later."
    
    # Suggested questions
    suggested_questions = [
        "Why should I consider this college?",
        "What are my chances of acceptance?",
        "Is this college a good financial fit for me?",
        "How does my academic profile match this college?",
        "What are the strengths and weaknesses of this match?",
        "How does this college compare to my other options?"
    ]
    
    return render_template(
        'chat_interface.html',
        user=user,
        colleges=colleges,
        selected_college=selected_college,
        query=query,
        explanation=explanation,
        suggested_questions=suggested_questions
    )

# System Insights Dashboard
@app.route('/system-insights', methods=['GET'])
def system_insights():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
        
    user = User.query.filter_by(username=session['user']).first()
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))
    
    # Get system insights data
    try:
        from system_insights import get_insights
        insights = get_insights(user.id)
    except Exception as e:
        print(f"Error in system_insights: {e}")
        flash(f"An error occurred while loading system insights: {str(e)}")
        insights = {
            "error": True,
            "message": "Unable to load system insights at this time."
        }
    
    return render_template('system_insights.html', insights=insights, user=user)

# API proxy routes for frontend JavaScript
@app.route('/api-proxy/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_proxy(endpoint):
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.filter_by(username=session['user']).first()
    if not user:
        session.clear()
        return jsonify({'error': 'User not found'}), 401
    
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
    # Use PORT environment variable if available (for Render compatibility)
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Flask app on port {port}")
    app.run(debug=True, host='0.0.0.0', port=port)
