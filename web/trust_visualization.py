"""
Trust visualization module for the Promethios College Counselor.

This module provides visualization of trust factors for college recommendations.
"""

import json
import plotly
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from flask import jsonify, render_template, request, session

class TrustVisualization:
    """Generates visualizations of trust factors."""
    
    def __init__(self, api_client=None):
        """
        Initialize the trust visualization module.
        
        Args:
            api_client: Optional API client for college data
        """
        self.api_client = api_client
    
    def generate_trust_radar_data(self, student_profile, college, journal_entries=None):
        """
        Generate radar chart data for trust factors.
        
        Args:
            student_profile: Student profile data
            college: College data
            journal_entries: Optional journal entries
            
        Returns:
            dict: Radar chart data
        """
        # Evaluate college match using API client or mock data
        if self.api_client:
            results = self.api_client.evaluate_college_match(
                student_id=student_profile.get('user_id'),
                college_id=college.get('id')
            )
        else:
            # Mock data for testing
            results = self._generate_mock_evaluation(student_profile, college)
        
        # Extract factor scores
        factors = results.get("factors", {})
        labels = []
        data = []
        
        for factor_name, factor_data in factors.items():
            labels.append(factor_name.replace("_", " ").title())
            data.append(factor_data.get("score", 0))
        
        # Create radar chart data
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=data,
            theta=labels,
            fill='toself',
            name=college.get('name', 'College'),
            line_color='rgba(54, 162, 235, 1)',
            fillcolor='rgba(54, 162, 235, 0.2)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=True
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def generate_comparison_radar_data(self, student_profile, colleges, journal_entries=None):
        """
        Generate comparison radar chart for multiple colleges.
        
        Args:
            student_profile: Student profile data
            colleges: List of college data
            journal_entries: Optional journal entries
            
        Returns:
            dict: Comparison radar chart data
        """
        # Limit to 3 colleges for readability
        colleges = colleges[:3]
        
        # Colors for different colleges
        colors = [
            {"line": 'rgba(54, 162, 235, 1)', "fill": 'rgba(54, 162, 235, 0.2)'},
            {"line": 'rgba(255, 99, 132, 1)', "fill": 'rgba(255, 99, 132, 0.2)'},
            {"line": 'rgba(75, 192, 192, 1)', "fill": 'rgba(75, 192, 192, 0.2)'}
        ]
        
        # Create figure
        fig = go.Figure()
        
        # Common labels for all colleges
        all_labels = set()
        
        # First pass to collect all factor names
        for college in colleges:
            if self.api_client:
                results = self.api_client.evaluate_college_match(
                    student_id=student_profile.get('user_id'),
                    college_id=college.get('id')
                )
            else:
                results = self._generate_mock_evaluation(student_profile, college)
            
            factors = results.get("factors", {})
            for factor_name in factors.keys():
                all_labels.add(factor_name.replace("_", " ").title())
        
        # Convert to list and sort
        labels = sorted(list(all_labels))
        
        # Second pass to add traces
        for i, college in enumerate(colleges):
            if self.api_client:
                results = self.api_client.evaluate_college_match(
                    student_id=student_profile.get('user_id'),
                    college_id=college.get('id')
                )
            else:
                results = self._generate_mock_evaluation(student_profile, college)
            
            factors = results.get("factors", {})
            
            # Create data array with same order as labels
            data = []
            for label in labels:
                factor_name = label.lower().replace(" ", "_")
                if factor_name in factors:
                    data.append(factors[factor_name].get("score", 0))
                else:
                    data.append(0)
            
            # Add trace for this college
            fig.add_trace(go.Scatterpolar(
                r=data,
                theta=labels,
                fill='toself',
                name=college.get('name', f'College {i+1}'),
                line_color=colors[i]["line"],
                fillcolor=colors[i]["fill"]
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=True
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def generate_factor_breakdown(self, student_profile, college):
        """
        Generate detailed breakdown of trust factors.
        
        Args:
            student_profile: Student profile data
            college: College data
            
        Returns:
            dict: Factor breakdown data
        """
        # Get evaluation results
        if self.api_client:
            results = self.api_client.evaluate_college_match(
                student_id=student_profile.get('user_id'),
                college_id=college.get('id')
            )
        else:
            results = self._generate_mock_evaluation(student_profile, college)
        
        # Extract factors
        factors = results.get("factors", {})
        
        # Create breakdown
        breakdown = []
        for factor_name, factor_data in factors.items():
            breakdown.append({
                "name": factor_name.replace("_", " ").title(),
                "score": factor_data.get("score", 0),
                "weight": factor_data.get("weight", 1),
                "explanation": factor_data.get("explanation", {}).get("summary", "No explanation available."),
                "details": factor_data.get("explanation", {}).get("details", [])
            })
        
        # Sort by weight (descending)
        breakdown.sort(key=lambda x: x["weight"], reverse=True)
        
        return breakdown
    
    def generate_trust_score_summary(self, student_profile, college):
        """
        Generate summary of trust score.
        
        Args:
            student_profile: Student profile data
            college: College data
            
        Returns:
            dict: Trust score summary
        """
        # Get evaluation results
        if self.api_client:
            results = self.api_client.evaluate_college_match(
                student_id=student_profile.get('user_id'),
                college_id=college.get('id')
            )
        else:
            results = self._generate_mock_evaluation(student_profile, college)
        
        # Extract overall score and category
        overall_score = results.get("overall_score", 0)
        category = results.get("category", "unknown")
        
        # Generate summary text
        if overall_score >= 80:
            summary = f"{college.get('name', 'This college')} is an excellent match for you with a trust score of {overall_score}. "
            summary += "The recommendation is highly confident based on your profile and preferences."
        elif overall_score >= 60:
            summary = f"{college.get('name', 'This college')} is a good match for you with a trust score of {overall_score}. "
            summary += "The recommendation is confident but there are some areas where the match could be improved."
        elif overall_score >= 40:
            summary = f"{college.get('name', 'This college')} is a moderate match for you with a trust score of {overall_score}. "
            summary += "Consider the factor breakdown carefully to understand the strengths and weaknesses of this match."
        else:
            summary = f"{college.get('name', 'This college')} is not a strong match for you with a trust score of {overall_score}. "
            summary += "There are significant areas where this college does not align with your profile and preferences."
        
        # Add category-specific text
        if category == "safety":
            summary += " This is considered a safety school where you have a high likelihood of acceptance."
        elif category == "target":
            summary += " This is considered a target school where you have a reasonable chance of acceptance."
        elif category == "reach":
            summary += " This is considered a reach school where acceptance may be challenging but possible."
        
        return {
            "overall_score": overall_score,
            "category": category,
            "summary": summary
        }
    
    def _generate_mock_evaluation(self, student_profile, college):
        """
        Generate mock evaluation data for testing.
        
        Args:
            student_profile: Student profile data
            college: College data
            
        Returns:
            dict: Mock evaluation results
        """
        # Generate random scores for factors
        factors = {
            "academic_match": {
                "score": np.random.randint(60, 100),
                "weight": 2.0,
                "explanation": {
                    "summary": "Your academic profile aligns well with this college's requirements.",
                    "details": [
                        f"Your GPA of {student_profile.get('gpa', '3.5')} is within the typical range for admitted students.",
                        "Your intended major is well-supported at this institution."
                    ]
                }
            },
            "financial_fit": {
                "score": np.random.randint(40, 90),
                "weight": 1.5,
                "explanation": {
                    "summary": "The college's cost aligns moderately with your budget.",
                    "details": [
                        f"Your budget is {student_profile.get('budget', '$20,000')} per year.",
                        f"The average net price is {college.get('avg_net_price', '$25,000')} per year."
                    ]
                }
            },
            "location_match": {
                "score": np.random.randint(50, 100),
                "weight": 1.0,
                "explanation": {
                    "summary": "The college's location matches your preferences.",
                    "details": [
                        f"You prefer {student_profile.get('location_preference', 'urban')} settings.",
                        f"This college is in a {college.get('setting', 'urban')} environment."
                    ]
                }
            },
            "size_fit": {
                "score": np.random.randint(60, 100),
                "weight": 0.8,
                "explanation": {
                    "summary": "The college's size aligns with your preferences.",
                    "details": [
                        f"You prefer {student_profile.get('size_preference', 'medium')} sized institutions.",
                        f"This college has {college.get('student_size', '10,000')} students."
                    ]
                }
            },
            "emotional_alignment": {
                "score": np.random.randint(70, 100),
                "weight": 1.2,
                "explanation": {
                    "summary": "Based on your journal entries, this college environment aligns with your emotional needs.",
                    "details": [
                        "Your journal entries indicate a preference for collaborative environments.",
                        "This college emphasizes community and collaboration."
                    ]
                }
            }
        }
        
        # Calculate overall score
        total_weight = sum(factor["weight"] for factor in factors.values())
        weighted_sum = sum(factor["score"] * factor["weight"] for factor in factors.values())
        overall_score = int(weighted_sum / total_weight)
        
        # Determine category
        if overall_score >= 80:
            category = "safety"
        elif overall_score >= 60:
            category = "target"
        else:
            category = "reach"
        
        return {
            "overall_score": overall_score,
            "category": category,
            "factors": factors
        }

# Flask routes for trust visualization
def register_trust_visualization_routes(app, db):
    """
    Register Flask routes for trust visualization.
    
    Args:
        app: Flask application
        db: SQLAlchemy database
    """
    from models import User, College
    from api_client import APIClient
    
    @app.route('/trust-visualization/<college_id>', methods=['GET'])
    def trust_visualization(college_id):
        """Render trust visualization page for a specific college."""
        if 'user' not in session:
            return redirect(url_for('auth.login'))
            
        user = User.query.filter_by(username=session['user']).first()
        if not user:
            session.clear()
            return redirect(url_for('auth.login'))
        
        # Get college data
        api_client = APIClient()
        college = api_client.get_college_details(college_id)
        
        if not college:
            flash('College not found.')
            return redirect(url_for('colleges'))
        
        # Initialize visualization
        visualizer = TrustVisualization(api_client)
        
        # Generate radar chart
        radar_chart = visualizer.generate_trust_radar_data(user.profile.to_dict(), college)
        
        # Generate factor breakdown
        factor_breakdown = visualizer.generate_factor_breakdown(user.profile.to_dict(), college)
        
        # Generate trust score summary
        trust_summary = visualizer.generate_trust_score_summary(user.profile.to_dict(), college)
        
        return render_template(
            'trust_visualization.html',
            user=user,
            college=college,
            radar_chart=radar_chart,
            factor_breakdown=factor_breakdown,
            trust_summary=trust_summary
        )
    
    @app.route('/api/trust-data/<college_id>', methods=['GET'])
    def trust_data(college_id):
        """API endpoint for trust data."""
        if 'user' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
            
        user = User.query.filter_by(username=session['user']).first()
        if not user:
            session.clear()
            return jsonify({'error': 'User not found'}), 401
        
        # Get college data
        api_client = APIClient()
        college = api_client.get_college_details(college_id)
        
        if not college:
            return jsonify({'error': 'College not found'}), 404
        
        # Initialize visualization
        visualizer = TrustVisualization(api_client)
        
        # Generate factor breakdown
        factor_breakdown = visualizer.generate_factor_breakdown(user.profile.to_dict(), college)
        
        # Generate trust score summary
        trust_summary = visualizer.generate_trust_score_summary(user.profile.to_dict(), college)
        
        return jsonify({
            'factor_breakdown': factor_breakdown,
            'trust_summary': trust_summary
        })
