"""
College comparison tool for the Promethios College Counselor.

This module provides interactive comparison of multiple colleges.
"""

import json
import plotly
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from flask import jsonify, render_template, request, session, redirect, url_for, flash
from trust_visualization import TrustVisualization

class CollegeComparisonTool:
    """Provides interactive college comparison functionality."""
    
    def __init__(self, api_client=None, trust_visualization=None):
        """
        Initialize the college comparison tool.
        
        Args:
            api_client: Optional API client for college data
            trust_visualization: Optional trust visualization instance
        """
        self.api_client = api_client
        self.trust_visualization = trust_visualization or TrustVisualization(api_client)
    
    def generate_comparison_data(self, student_profile, college_ids):
        """
        Generate comparison data for selected colleges.
        
        Args:
            student_profile: Student profile data
            college_ids: List of college IDs to compare
            
        Returns:
            dict: Comparison data
        """
        # Get college data
        colleges = []
        for college_id in college_ids:
            if self.api_client:
                college = self.api_client.get_college_details(college_id)
            else:
                # Mock data for testing
                college = self._generate_mock_college(college_id)
                
            if college:
                colleges.append(college)
        
        # Generate comparison data
        comparison = {
            "colleges": colleges,
            "trust_scores": [],
            "radar_chart": self.trust_visualization.generate_comparison_radar_data(
                student_profile=student_profile,
                colleges=colleges
            ),
            "cost_analysis": self._generate_cost_analysis(student_profile, colleges),
            "feature_comparison": self._generate_feature_comparison(colleges)
        }
        
        # Get trust scores
        for college in colleges:
            if self.api_client:
                results = self.api_client.evaluate_college_match(
                    student_id=student_profile.get('user_id'),
                    college_id=college.get('id')
                )
            else:
                results = self._generate_mock_evaluation(student_profile, college)
                
            comparison["trust_scores"].append({
                "college_id": college.get("id"),
                "overall_score": results.get("overall_score", 0),
                "category": results.get("category", "unknown")
            })
        
        return comparison
    
    def _generate_cost_analysis(self, student_profile, colleges):
        """
        Generate cost analysis for colleges.
        
        Args:
            student_profile: Student profile data
            colleges: List of college data
            
        Returns:
            dict: Cost analysis data
        """
        # Get budget from profile
        budget = student_profile.get("budget", 20000)
        
        # Create analysis
        analysis = []
        for college in colleges:
            net_price = college.get("avg_net_price", 0)
            difference = net_price - budget
            
            analysis.append({
                "college_id": college.get("id"),
                "college_name": college.get("name"),
                "net_price": net_price,
                "budget": budget,
                "difference": difference,
                "affordable": difference <= 0,
                "affordability_score": max(0, min(100, 100 - (difference / 1000) if difference > 0 else 100))
            })
        
        return analysis
    
    def _generate_feature_comparison(self, colleges):
        """
        Generate feature comparison table.
        
        Args:
            colleges: List of college data
            
        Returns:
            dict: Feature comparison data
        """
        # Define features to compare
        features = [
            {"key": "admission_rate", "label": "Admission Rate", "format": "percentage"},
            {"key": "student_size", "label": "Student Population", "format": "number"},
            {"key": "average_gpa", "label": "Average GPA", "format": "decimal"},
            {"key": "tuition_in_state", "label": "In-State Tuition", "format": "currency"},
            {"key": "tuition_out_of_state", "label": "Out-of-State Tuition", "format": "currency"},
            {"key": "graduation_rate", "label": "Graduation Rate", "format": "percentage"},
            {"key": "student_faculty_ratio", "label": "Student-Faculty Ratio", "format": "ratio"}
        ]
        
        # Extract feature values
        comparison = []
        for feature in features:
            row = {
                "feature": feature["label"],
                "format": feature["format"],
                "values": []
            }
            
            for college in colleges:
                row["values"].append(college.get(feature["key"], None))
            
            comparison.append(row)
        
        return comparison
    
    def generate_comparison_bar_chart(self, cost_analysis):
        """
        Generate bar chart for cost comparison.
        
        Args:
            cost_analysis: Cost analysis data
            
        Returns:
            str: JSON string of plotly figure
        """
        # Extract data
        colleges = [item["college_name"] for item in cost_analysis]
        net_prices = [item["net_price"] for item in cost_analysis]
        budget = cost_analysis[0]["budget"] if cost_analysis else 0
        
        # Create figure
        fig = go.Figure()
        
        # Add bars for net prices
        fig.add_trace(go.Bar(
            x=colleges,
            y=net_prices,
            name='Net Price',
            marker_color='rgba(54, 162, 235, 0.8)'
        ))
        
        # Add line for budget
        fig.add_trace(go.Scatter(
            x=colleges,
            y=[budget] * len(colleges),
            mode='lines',
            name='Your Budget',
            line=dict(color='rgba(255, 99, 132, 1)', width=2, dash='dash')
        ))
        
        # Update layout
        fig.update_layout(
            title='Cost Comparison',
            xaxis_title='College',
            yaxis_title='Annual Cost ($)',
            barmode='group',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def generate_admission_chart(self, colleges):
        """
        Generate chart for admission statistics.
        
        Args:
            colleges: List of college data
            
        Returns:
            str: JSON string of plotly figure
        """
        # Extract data
        names = [college.get("name", f"College {i+1}") for i, college in enumerate(colleges)]
        admission_rates = [college.get("admission_rate", 0) for college in colleges]
        
        # Create figure
        fig = go.Figure()
        
        # Add bars for admission rates
        fig.add_trace(go.Bar(
            x=names,
            y=admission_rates,
            name='Admission Rate',
            marker_color='rgba(75, 192, 192, 0.8)'
        ))
        
        # Update layout
        fig.update_layout(
            title='Admission Rate Comparison',
            xaxis_title='College',
            yaxis_title='Admission Rate (%)',
            yaxis=dict(range=[0, 100])
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def _generate_mock_college(self, college_id):
        """
        Generate mock college data for testing.
        
        Args:
            college_id: College ID
            
        Returns:
            dict: Mock college data
        """
        # Generate random college data
        names = [
            "Evergreen State University",
            "Oakridge College",
            "Riverside Institute of Technology",
            "Meadowbrook Liberal Arts College",
            "Atlantic Coast University"
        ]
        
        settings = ["urban", "suburban", "rural"]
        
        return {
            "id": college_id,
            "name": names[int(college_id) % len(names)],
            "location": f"City {college_id}, State",
            "setting": settings[int(college_id) % len(settings)],
            "student_size": np.random.randint(1000, 30000),
            "admission_rate": np.random.randint(10, 90),
            "average_gpa": round(np.random.uniform(3.0, 4.0), 2),
            "tuition_in_state": np.random.randint(8000, 25000),
            "tuition_out_of_state": np.random.randint(25000, 50000),
            "avg_net_price": np.random.randint(15000, 35000),
            "graduation_rate": np.random.randint(60, 95),
            "student_faculty_ratio": f"{np.random.randint(6, 20)}:1"
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
                "weight": 2.0
            },
            "financial_fit": {
                "score": np.random.randint(40, 90),
                "weight": 1.5
            },
            "location_match": {
                "score": np.random.randint(50, 100),
                "weight": 1.0
            },
            "size_fit": {
                "score": np.random.randint(60, 100),
                "weight": 0.8
            },
            "emotional_alignment": {
                "score": np.random.randint(70, 100),
                "weight": 1.2
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

# Flask routes for college comparison
def register_college_comparison_routes(app, db):
    """
    Register Flask routes for college comparison.
    
    Args:
        app: Flask application
        db: SQLAlchemy database
    """
    from models import User, College
    from api_client import APIClient
    from trust_visualization import TrustVisualization
    
    @app.route('/college-comparison', methods=['GET', 'POST'])
    def college_comparison():
        """Render college comparison page."""
        if 'user' not in session:
            return redirect(url_for('auth.login'))
            
        user = User.query.filter_by(username=session['user']).first()
        if not user:
            session.clear()
            return redirect(url_for('auth.login'))
        
        # Initialize API client
        api_client = APIClient()
        
        # Initialize comparison tool
        trust_viz = TrustVisualization(api_client)
        comparison_tool = CollegeComparisonTool(api_client, trust_viz)
        
        # Get selected college IDs from form or session
        selected_ids = []
        
        if request.method == 'POST':
            # Get selected colleges from form
            selected_ids = request.form.getlist('college_ids')
            session['comparison_colleges'] = selected_ids
        elif 'comparison_colleges' in session:
            # Get selected colleges from session
            selected_ids = session['comparison_colleges']
        
        # Validate selected colleges (limit to 3)
        if len(selected_ids) > 3:
            selected_ids = selected_ids[:3]
            flash('Maximum of 3 colleges can be compared at once.')
        
        # Get comparison data if colleges are selected
        comparison_data = None
        cost_chart = None
        admission_chart = None
        
        if selected_ids:
            comparison_data = comparison_tool.generate_comparison_data(
                student_profile=user.profile.to_dict(),
                college_ids=selected_ids
            )
            
            # Generate charts
            cost_chart = comparison_tool.generate_comparison_bar_chart(
                comparison_data['cost_analysis']
            )
            
            admission_chart = comparison_tool.generate_admission_chart(
                comparison_data['colleges']
            )
        
        # Get all colleges for selection
        all_colleges = api_client.get_college_recommendations(user.id)
        
        return render_template(
            'college_comparison.html',
            user=user,
            all_colleges=all_colleges.get('recommendations', []),
            selected_ids=selected_ids,
            comparison_data=comparison_data,
            cost_chart=cost_chart,
            admission_chart=admission_chart
        )
    
    @app.route('/api/comparison-data', methods=['POST'])
    def comparison_data():
        """API endpoint for comparison data."""
        if 'user' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
            
        user = User.query.filter_by(username=session['user']).first()
        if not user:
            session.clear()
            return jsonify({'error': 'User not found'}), 401
        
        # Get college IDs from request
        data = request.get_json()
        college_ids = data.get('college_ids', [])
        
        if not college_ids:
            return jsonify({'error': 'No colleges selected'}), 400
        
        # Limit to 3 colleges
        if len(college_ids) > 3:
            college_ids = college_ids[:3]
        
        # Initialize API client
        api_client = APIClient()
        
        # Initialize comparison tool
        trust_viz = TrustVisualization(api_client)
        comparison_tool = CollegeComparisonTool(api_client, trust_viz)
        
        # Generate comparison data
        comparison_data = comparison_tool.generate_comparison_data(
            student_profile=user.profile.to_dict(),
            college_ids=college_ids
        )
        
        return jsonify(comparison_data)
