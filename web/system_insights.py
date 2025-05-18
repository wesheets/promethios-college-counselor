"""
System insights dashboard implementation for Promethios College Counselor.

This module provides routes and functionality for the investor-facing system insights dashboard.
"""

from flask import Blueprint, render_template, jsonify, request, session
from models import db, User, JournalEntry
import json
import random
from datetime import datetime, timedelta
import pandas as pd
import plotly
import plotly.graph_objects as go

def register_system_insights_routes(app, db):
    """Register system insights routes with the Flask app."""
    
    @app.route('/system-insights')
    def system_insights():
        """Render the system insights dashboard."""
        if 'user' not in session:
            return redirect(url_for('auth.login'))
            
        user = User.query.filter_by(username=session['user']).first()
        if not user:
            session.clear()
            return redirect(url_for('auth.login'))
        
        # Get emotional telemetry data
        emotion_data = get_emotion_telemetry(user.id)
        
        # Get trust factor calculation logs
        trust_factor_logs = get_trust_factor_logs(user.id)
        
        # Get decision justification logs
        decision_logs = get_decision_justification_logs(user.id)
        
        # Get governance core activity logs
        governance_logs = get_governance_activity_logs()
        
        return render_template(
            'system_insights.html',
            user=user,
            emotion_data=emotion_data,
            trust_factor_logs=trust_factor_logs,
            decision_logs=decision_logs,
            governance_logs=governance_logs
        )
    
    @app.route('/api/system-insights/emotion-telemetry')
    def api_emotion_telemetry():
        """API endpoint for emotion telemetry data."""
        if 'user' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user = User.query.filter_by(username=session['user']).first()
        if not user:
            return jsonify({'error': 'User not found'}), 401
        
        days = request.args.get('days', 30, type=int)
        emotion_data = get_emotion_telemetry(user.id, days=days)
        
        return jsonify(emotion_data)
    
    @app.route('/api/system-insights/trust-factors')
    def api_trust_factors():
        """API endpoint for trust factor data."""
        if 'user' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user = User.query.filter_by(username=session['user']).first()
        if not user:
            return jsonify({'error': 'User not found'}), 401
        
        college_id = request.args.get('college_id')
        trust_factor_logs = get_trust_factor_logs(user.id, college_id=college_id)
        
        return jsonify(trust_factor_logs)
    
    @app.route('/api/system-insights/decision-logs')
    def api_decision_logs():
        """API endpoint for decision justification logs."""
        if 'user' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user = User.query.filter_by(username=session['user']).first()
        if not user:
            return jsonify({'error': 'User not found'}), 401
        
        college_id = request.args.get('college_id')
        decision_logs = get_decision_justification_logs(user.id, college_id=college_id)
        
        return jsonify(decision_logs)
    
    @app.route('/api/system-insights/governance-logs')
    def api_governance_logs():
        """API endpoint for governance core activity logs."""
        if 'user' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        governance_logs = get_governance_activity_logs()
        
        return jsonify(governance_logs)

def get_emotion_telemetry(user_id, days=30):
    """Get emotion telemetry data for a user.
    
    In a production environment, this would retrieve actual telemetry data.
    For demo purposes, we generate synthetic data.
    """
    # Get journal entries for the user
    entries = JournalEntry.query.filter_by(user_id=user_id).order_by(JournalEntry.created_at.desc()).all()
    
    # If we have journal entries, use their data
    if entries:
        dates = []
        sentiment_scores = []
        uncertainty_scores = []
        agitation_scores = []
        
        for entry in entries:
            dates.append(entry.created_at.strftime('%Y-%m-%d'))
            sentiment_scores.append(entry.sentiment_score or random.randint(60, 85))
            uncertainty_scores.append(entry.uncertainty_score or random.randint(20, 50))
            agitation_scores.append(entry.agitation_score or random.randint(15, 40))
        
        # Generate telemetry logs
        logs = []
        for i, entry in enumerate(entries[:3]):
            log = {
                "event_type": "emotion_telemetry",
                "user_id": user_id,
                "sentiment_score": sentiment_scores[i],
                "uncertainty_score": uncertainty_scores[i],
                "agitation_score": agitation_scores[i],
                "journal_id": f"j-{random.randint(9000, 9999)}",
                "timestamp": entry.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                "emotion_summary": entry.emotion_summary or "Analysis not available.",
                "confidence": round(random.uniform(0.85, 0.95), 2)
            }
            logs.append(log)
    else:
        # Generate synthetic data if no journal entries exist
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Generate dates at regular intervals
        date_range = pd.date_range(start=start_date, end=end_date, periods=6)
        dates = [date.strftime('%Y-%m-%d') for date in date_range]
        
        # Generate synthetic emotion scores
        # Start with moderate scores and show improvement over time
        sentiment_scores = [65, 70, 68, 75, 82, 78]
        uncertainty_scores = [55, 48, 42, 35, 28, 42]
        agitation_scores = [40, 35, 30, 25, 15, 23]
        
        # Generate synthetic telemetry logs
        logs = []
        for i in range(3):
            log = {
                "event_type": "emotion_telemetry",
                "user_id": user_id,
                "sentiment_score": sentiment_scores[-(i+1)],
                "uncertainty_score": uncertainty_scores[-(i+1)],
                "agitation_score": agitation_scores[-(i+1)],
                "journal_id": f"j-{random.randint(9000, 9999)}",
                "timestamp": (end_date - timedelta(days=i*2)).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                "emotion_summary": get_synthetic_emotion_summary(sentiment_scores[-(i+1)], uncertainty_scores[-(i+1)]),
                "confidence": round(random.uniform(0.85, 0.95), 2)
            }
            logs.append(log)
    
    # Calculate averages
    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
    avg_uncertainty = sum(uncertainty_scores) / len(uncertainty_scores)
    avg_agitation = sum(agitation_scores) / len(agitation_scores)
    
    # Calculate volatility (standard deviation)
    sentiment_volatility = (sum([(s - avg_sentiment)**2 for s in sentiment_scores]) / len(sentiment_scores))**0.5
    
    return {
        'dates': dates,
        'sentiment': sentiment_scores,
        'uncertainty': uncertainty_scores,
        'agitation': agitation_scores,
        'averages': {
            'sentiment': round(avg_sentiment, 1),
            'uncertainty': round(avg_uncertainty, 1),
            'agitation': round(avg_agitation, 1),
            'volatility': round(sentiment_volatility, 1)
        },
        'logs': logs
    }

def get_trust_factor_logs(user_id, college_id=None):
    """Get trust factor calculation logs for a user.
    
    In a production environment, this would retrieve actual logs.
    For demo purposes, we generate synthetic data.
    """
    # Generate synthetic trust factor data
    factors = {
        "academic_alignment": {"score": 85, "weight": 0.30, "justification": "GPA of 3.8 is above the college's average of 3.6, SAT score is within the middle 50% range"},
        "financial_fit": {"score": 72, "weight": 0.25, "justification": "Net price is 15% below student's specified budget, but limited merit scholarships available"},
        "location_match": {"score": 90, "weight": 0.15, "justification": "College is in student's preferred region (West Coast) and within 100 miles of specified location preference"},
        "size_preference": {"score": 65, "weight": 0.10, "justification": "College size (15,000) is larger than student's preferred size range (5,000-10,000)"},
        "setting_match": {"score": 80, "weight": 0.10, "justification": "Urban setting matches student's preference"},
        "emotional_alignment": {"score": 78, "weight": 0.10, "justification": "Journal entries indicate positive sentiment toward similar institutions"}
    }
    
    # Calculate total score
    total_score = sum([factor["score"] * factor["weight"] for factor in factors.values()])
    
    # Determine category
    if total_score >= 80:
        category = "safety"
    elif total_score >= 60:
        category = "target"
    else:
        category = "reach"
    
    # Create log entry
    log = {
        "event_type": "trust_factor_calculation",
        "user_id": user_id,
        "college_id": college_id or f"c-{random.randint(1000, 9999)}",
        "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        "factors": factors,
        "total_score": round(total_score, 1),
        "category": category,
        "confidence": round(random.uniform(0.85, 0.95), 2)
    }
    
    return {
        'factors': factors,
        'total_score': round(total_score, 1),
        'category': category,
        'logs': [log]
    }

def get_decision_justification_logs(user_id, college_id=None):
    """Get decision justification logs for a user.
    
    In a production environment, this would retrieve actual logs.
    For demo purposes, we generate synthetic data.
    """
    # Generate synthetic decision logs
    logs = []
    
    # Target school recommendation
    target_log = {
        "event_type": "decision_justification",
        "user_id": user_id,
        "college_id": college_id or f"c-{random.randint(1000, 9999)}",
        "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        "decision_type": "recommendation",
        "justification": "College was recommended as a target school based on trust score of 79.3. Academic profile shows strong alignment with admission requirements. Financial considerations are within budget constraints. Location and setting preferences are well-matched. Student's emotional state indicates positive sentiment toward similar institutions with moderate uncertainty about academic rigor, which this institution addresses through strong support programs.",
        "factors_considered": ["academic_profile", "financial_constraints", "location_preferences", "emotional_state"],
        "alternatives_considered": [f"c-{random.randint(1000, 9999)}", f"c-{random.randint(1000, 9999)}"],
        "confidence": round(random.uniform(0.85, 0.95), 2),
        "recommendation_strength": "strong"
    }
    logs.append(target_log)
    
    # Safety school recommendation
    safety_log = {
        "event_type": "decision_justification",
        "user_id": user_id,
        "college_id": f"c-{random.randint(1000, 9999)}",
        "timestamp": (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        "decision_type": "recommendation",
        "justification": "College was recommended as a safety school based on trust score of 85.7. Academic profile significantly exceeds admission requirements. Financial aid package is generous relative to budget. Location is within preferred region but further from ideal location. Setting matches preferences. Student's emotional state shows low uncertainty about admission chances, making this a confidence-building option in the overall portfolio.",
        "factors_considered": ["academic_profile", "financial_aid", "location_distance", "emotional_confidence"],
        "alternatives_considered": [f"c-{random.randint(1000, 9999)}", f"c-{random.randint(1000, 9999)}"],
        "confidence": round(random.uniform(0.85, 0.95), 2),
        "recommendation_strength": "moderate"
    }
    logs.append(safety_log)
    
    return {'logs': logs}

def get_governance_activity_logs():
    """Get governance core activity logs.
    
    In a production environment, this would retrieve actual logs.
    For demo purposes, we generate synthetic data.
    """
    # Generate synthetic governance logs
    logs = []
    
    # Recommendation review
    recommendation_review = {
        "event_type": "governance_activity",
        "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        "activity_type": "recommendation_review",
        "user_id": f"u-{random.randint(1000, 9999)}",
        "description": "Reviewing college recommendations for potential bias in financial fit calculations. Detected slight overemphasis on merit scholarships vs. need-based aid. Applied correction factor of 0.92 to financial fit scores for colleges with high merit focus.",
        "governance_rule": "financial_equity_rule_3.2",
        "correction_applied": True,
        "impact_assessment": "Moderate impact on 3 colleges in recommendation set, changing 1 college from 'target' to 'reach' category.",
        "confidence": round(random.uniform(0.85, 0.95), 2)
    }
    logs.append(recommendation_review)
    
    # Emotional analysis audit
    emotional_audit = {
        "event_type": "governance_activity",
        "timestamp": (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        "activity_type": "emotional_analysis_audit",
        "user_id": f"u-{random.randint(1000, 9999)}",
        "description": "Auditing emotional analysis of journal entries for consistency and accuracy. Detected potential underestimation of uncertainty in entries mentioning financial concerns. Applied recalibration to uncertainty scores for financial-themed entries.",
        "governance_rule": "emotional_consistency_rule_2.7",
        "correction_applied": True,
        "impact_assessment": "Minor impact on emotional trend analysis, slightly increasing uncertainty trend line.",
        "confidence": round(random.uniform(0.85, 0.95), 2)
    }
    logs.append(emotional_audit)
    
    # Explanation verification
    explanation_verification = {
        "event_type": "governance_activity",
        "timestamp": (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        "activity_type": "explanation_verification",
        "user_id": f"u-{random.randint(1000, 9999)}",
        "description": "Verifying accuracy of explanations provided for college recommendations. Detected minor inconsistency between trust factor calculation and explanation for location preference. Updated explanation template to more accurately reflect distance calculations.",
        "governance_rule": "explanation_accuracy_rule_4.1",
        "correction_applied": True,
        "impact_assessment": "Minimal impact on user experience, improved explanation accuracy by approximately 7%.",
        "confidence": round(random.uniform(0.85, 0.95), 2)
    }
    logs.append(explanation_verification)
    
    return {'logs': logs}

def get_synthetic_emotion_summary(sentiment, uncertainty):
    """Generate a synthetic emotion summary based on sentiment and uncertainty scores."""
    if sentiment >= 80:
        sentiment_text = "very positive"
    elif sentiment >= 70:
        sentiment_text = "positive"
    elif sentiment >= 50:
        sentiment_text = "moderately positive"
    elif sentiment >= 30:
        sentiment_text = "neutral to slightly negative"
    else:
        sentiment_text = "negative"
    
    if uncertainty >= 70:
        uncertainty_text = "high uncertainty"
    elif uncertainty >= 40:
        uncertainty_text = "moderate uncertainty"
    else:
        uncertainty_text = "low uncertainty"
    
    topics = ["college choices", "financial aid", "academic requirements", "campus life", "location preferences"]
    topic = random.choice(topics)
    
    return f"{sentiment_text} sentiment with {uncertainty_text} about {topic}"

class SystemInsights:
    """System insights dashboard for Promethios College Counselor."""
    
    def __init__(self, app, db):
        """Initialize the system insights dashboard."""
        register_system_insights_routes(app, db)
