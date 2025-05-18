"""
Conversational Decision Explainer for the Promethios College Counselor.

This module provides natural language explanations for college recommendations.
"""

import os
import json
import requests
from flask import jsonify, render_template, request, session, redirect, url_for, flash

class DecisionExplainer:
    """Provides conversational explanations for college recommendations."""
    
    def __init__(self, api_client=None, openai_api_key=None):
        """
        Initialize the decision explainer.
        
        Args:
            api_client: Optional API client for college data
            openai_api_key: OpenAI API key for generating explanations
        """
        self.api_client = api_client
        self.openai_api_key = openai_api_key or os.environ.get('OPENAI_API_KEY')
    
    def explain_decision(self, query, student_profile, college):
        """
        Generate a natural language explanation for a decision.
        
        Args:
            query: Question about the decision
            student_profile: Student profile data
            college: College data
            
        Returns:
            str: Natural language explanation
        """
        # Evaluate college match
        if self.api_client:
            results = self.api_client.evaluate_college_match(
                student_id=student_profile.get('user_id'),
                college_id=college.get('id')
            )
        else:
            # Mock data for testing
            results = self._generate_mock_evaluation(student_profile, college)
        
        # Create context for explanation
        context = self._create_explanation_context(results, student_profile, college)
        
        # Generate explanation
        if self.openai_api_key:
            explanation = self._generate_openai_response(query, context)
        else:
            explanation = self._generate_fallback_explanation(query, context)
        
        return explanation
    
    def explain_comparison(self, query, student_profile, colleges):
        """
        Generate a natural language explanation comparing colleges.
        
        Args:
            query: Question about the comparison
            student_profile: Student profile data
            colleges: List of college data
            
        Returns:
            str: Natural language explanation
        """
        # Evaluate each college
        results = []
        for college in colleges:
            if self.api_client:
                result = self.api_client.evaluate_college_match(
                    student_id=student_profile.get('user_id'),
                    college_id=college.get('id')
                )
            else:
                result = self._generate_mock_evaluation(student_profile, college)
                
            results.append({
                "college": college,
                "evaluation": result
            })
        
        # Create context for explanation
        context = self._create_comparison_context(results, student_profile)
        
        # Generate explanation
        if self.openai_api_key:
            explanation = self._generate_openai_response(query, context)
        else:
            explanation = self._generate_fallback_comparison(query, context, results)
        
        return explanation
    
    def _create_explanation_context(self, results, student_profile, college):
        """
        Create context for single college explanation.
        
        Args:
            results: Evaluation results
            student_profile: Student profile data
            college: College data
            
        Returns:
            str: Context for explanation
        """
        context = f"College: {college.get('name', 'Unknown')}\n"
        context += f"Trust score: {results.get('overall_score', 0)}\n"
        context += f"Category: {results.get('category', 'unknown')}\n\n"
        
        context += "Student profile:\n"
        context += f"- GPA: {student_profile.get('gpa', 'Unknown')}\n"
        context += f"- Intended majors: {student_profile.get('intended_majors', 'Unknown')}\n"
        context += f"- Location preference: {student_profile.get('location_preference', 'Unknown')}\n"
        context += f"- Budget: {student_profile.get('budget', 'Unknown')}\n\n"
        
        context += "Trust factors:\n"
        for factor_name, factor_data in results.get("factors", {}).items():
            context += f"- {factor_name}: {factor_data.get('score', 0)}\n"
            if "explanation" in factor_data and "summary" in factor_data["explanation"]:
                context += f"  Summary: {factor_data['explanation']['summary']}\n"
        
        return context
    
    def _create_comparison_context(self, results, student_profile):
        """
        Create context for college comparison explanation.
        
        Args:
            results: List of evaluation results with colleges
            student_profile: Student profile data
            
        Returns:
            str: Context for explanation
        """
        context = "Student profile:\n"
        context += f"- GPA: {student_profile.get('gpa', 'Unknown')}\n"
        context += f"- Intended majors: {student_profile.get('intended_majors', 'Unknown')}\n"
        context += f"- Location preference: {student_profile.get('location_preference', 'Unknown')}\n"
        context += f"- Budget: {student_profile.get('budget', 'Unknown')}\n\n"
        
        context += "Colleges being compared:\n"
        for result in results:
            college = result["college"]
            evaluation = result["evaluation"]
            
            context += f"\n{college.get('name', 'Unknown')}:\n"
            context += f"- Trust score: {evaluation.get('overall_score', 0)}\n"
            context += f"- Category: {evaluation.get('category', 'unknown')}\n"
            context += "- Key factors:\n"
            
            # Add top 3 factors by weight
            factors = evaluation.get("factors", {})
            sorted_factors = sorted(
                [(name, data) for name, data in factors.items()],
                key=lambda x: x[1].get("weight", 0),
                reverse=True
            )
            
            for factor_name, factor_data in sorted_factors[:3]:
                context += f"  - {factor_name}: {factor_data.get('score', 0)}\n"
                if "explanation" in factor_data and "summary" in factor_data["explanation"]:
                    context += f"    Summary: {factor_data['explanation']['summary']}\n"
        
        return context
    
    def _generate_openai_response(self, query, context):
        """
        Generate response using OpenAI API.
        
        Args:
            query: User question
            context: Context for the explanation
            
        Returns:
            str: Generated explanation
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_api_key}"
            }
            
            data = {
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": "You are a helpful college counselor assistant that explains college recommendations. Your explanations should be clear, informative, and personalized to the student's profile. Use the context provided to give accurate explanations."},
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                # Fallback if API call fails
                return self._generate_fallback_explanation(query, context)
                
        except Exception as e:
            # Fallback if exception occurs
            return self._generate_fallback_explanation(query, context)
    
    def _generate_fallback_explanation(self, query, context):
        """
        Generate fallback explanation when OpenAI API is unavailable.
        
        Args:
            query: User question
            context: Context for the explanation
            
        Returns:
            str: Fallback explanation
        """
        # Extract college name and trust score from context
        lines = context.split('\n')
        college_name = lines[0].replace('College: ', '') if lines and 'College: ' in lines[0] else 'this college'
        trust_score = lines[1].replace('Trust score: ', '') if len(lines) > 1 and 'Trust score: ' in lines[1] else '0'
        category = lines[2].replace('Category: ', '') if len(lines) > 2 and 'Category: ' in lines[2] else 'unknown'
        
        # Generate explanation based on query keywords
        if 'why' in query.lower() and 'recommend' in query.lower():
            return f"{college_name} was recommended with a trust score of {trust_score} because it aligns well with your academic profile, preferences, and budget. It is considered a {category} school based on your qualifications. The recommendation takes into account factors like academic match, financial fit, location preferences, and emotional alignment based on your journal entries."
        
        elif 'how' in query.lower() and 'score' in query.lower():
            return f"The trust score of {trust_score} for {college_name} was calculated by evaluating multiple factors including academic match, financial fit, location preferences, and emotional alignment. Each factor is weighted based on its importance, with academic match and financial fit typically having higher weights. The overall score represents how well this college aligns with your profile and preferences."
        
        elif 'what' in query.lower() and 'factor' in query.lower():
            return f"The key factors in recommending {college_name} include academic match (how well your GPA and academic achievements align with the college's standards), financial fit (how the college's cost compares to your budget), location match (whether the college's setting matches your preferences), and emotional alignment (based on analysis of your journal entries). Each factor contributes to the overall trust score of {trust_score}."
        
        elif 'compare' in query.lower():
            return f"When comparing {college_name} to other recommendations, consider the trust score of {trust_score} and its category ({category}). You should also look at specific factors like cost, location, academic programs, and campus culture. The college comparison tool provides a detailed side-by-side comparison of multiple colleges to help you make an informed decision."
        
        else:
            return f"{college_name} received a trust score of {trust_score} and is categorized as a {category} school for you. This recommendation is based on a comprehensive analysis of your academic profile, preferences, and the college's characteristics. The trust score indicates the level of confidence in this recommendation, with higher scores representing stronger matches."
    
    def _generate_fallback_comparison(self, query, context, results):
        """
        Generate fallback comparison explanation when OpenAI API is unavailable.
        
        Args:
            query: User question
            context: Context for the explanation
            results: List of evaluation results with colleges
            
        Returns:
            str: Fallback comparison explanation
        """
        # Extract college names and scores
        college_info = []
        for result in results:
            college = result["college"]
            evaluation = result["evaluation"]
            college_info.append({
                "name": college.get('name', 'Unknown'),
                "score": evaluation.get('overall_score', 0),
                "category": evaluation.get('category', 'unknown')
            })
        
        # Sort by score
        college_info.sort(key=lambda x: x["score"], reverse=True)
        
        # Generate comparison
        if 'difference' in query.lower() or 'different' in query.lower():
            response = "Here's how these colleges differ:\n\n"
            for college in college_info:
                response += f"{college['name']} (Trust Score: {college['score']}, Category: {college['category']}): "
                
                if college['score'] >= 80:
                    response += "This college is an excellent match for your profile and preferences.\n"
                elif college['score'] >= 60:
                    response += "This college is a good match with some areas that could be better aligned.\n"
                else:
                    response += "This college has significant areas where it doesn't align well with your needs.\n"
            
            return response
        
        elif 'recommend' in query.lower() or 'best' in query.lower():
            best_college = college_info[0]
            response = f"Based on your profile, {best_college['name']} appears to be the strongest match with a trust score of {best_college['score']}. "
            response += "This recommendation takes into account your academic profile, preferences, and budget. "
            
            if len(college_info) > 1:
                second_best = college_info[1]
                response += f"{second_best['name']} is also a good option with a score of {second_best['score']}, but not as strong a match as {best_college['name']}. "
            
            response += "Remember that trust scores are just one factor to consider, and you should also think about specific programs, campus culture, and personal fit when making your decision."
            
            return response
        
        elif 'cost' in query.lower() or 'afford' in query.lower() or 'budget' in query.lower():
            response = "Regarding affordability of these colleges:\n\n"
            for result in results:
                college = result["college"]
                name = college.get('name', 'Unknown')
                price = college.get('avg_net_price', 'Unknown')
                
                response += f"{name}: The average net price is ${price:,} per year. "
                
                if price <= 15000:
                    response += "This is relatively affordable compared to national averages.\n"
                elif price <= 25000:
                    response += "This is in the mid-range of college costs nationally.\n"
                else:
                    response += "This is on the higher end of college costs nationally.\n"
            
            return response
        
        else:
            response = "Comparison of your selected colleges:\n\n"
            for college in college_info:
                response += f"{college['name']}: Trust Score {college['score']}, Category: {college['category']}\n"
            
            response += "\nThe trust scores indicate how well each college matches your profile and preferences. "
            response += "Higher scores represent stronger matches. The category (safety, target, reach) indicates your likelihood of acceptance based on your academic profile. "
            response += "Consider using the detailed college comparison tool to see side-by-side comparisons of specific factors."
            
            return response
    
    def _generate_mock_evaluation(self, student_profile, college):
        """
        Generate mock evaluation data for testing.
        
        Args:
            student_profile: Student profile data
            college: College data
            
        Returns:
            dict: Mock evaluation results
        """
        import numpy as np
        
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

# Flask routes for decision explainer
def register_decision_explainer_routes(app, db):
    """
    Register Flask routes for decision explainer.
    
    Args:
        app: Flask application
        db: SQLAlchemy database
    """
    from models import User, College
    from api_client import APIClient
    
    @app.route('/decision-explainer/<college_id>', methods=['GET', 'POST'])
    def decision_explainer(college_id):
        """Render decision explainer page for a specific college."""
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
        
        # Initialize explainer
        explainer = DecisionExplainer(api_client)
        
        # Default explanation
        explanation = None
        query = "Why was this college recommended for me?"
        
        if request.method == 'POST':
            # Get query from form
            query = request.form.get('query', '')
            
            # Generate explanation
            explanation = explainer.explain_decision(
                query=query,
                student_profile=user.profile.to_dict(),
                college=college
            )
        
        # Get suggested questions
        suggested_questions = [
            "Why was this college recommended for me?",
            "How was the trust score calculated?",
            "What factors contributed most to this recommendation?",
            "How does this college compare to other recommendations?",
            "Is this college a good financial fit for me?",
            "What are the strengths and weaknesses of this match?"
        ]
        
        return render_template(
            'decision_explainer.html',
            user=user,
            college=college,
            query=query,
            explanation=explanation,
            suggested_questions=suggested_questions
        )
    
    @app.route('/comparison-explainer', methods=['GET', 'POST'])
    def comparison_explainer():
        """Render comparison explainer page."""
        if 'user' not in session:
            return redirect(url_for('auth.login'))
            
        user = User.query.filter_by(username=session['user']).first()
        if not user:
            session.clear()
            return redirect(url_for('auth.login'))
        
        # Initialize API client
        api_client = APIClient()
        
        # Get selected college IDs from form or session
        selected_ids = []
        
        if request.method == 'POST' and 'college_ids' in request.form:
            # Get selected colleges from form
            selected_ids = request.form.getlist('college_ids')
            session['explainer_colleges'] = selected_ids
        elif 'explainer_colleges' in session:
            # Get selected colleges from session
            selected_ids = session['explainer_colleges']
        
        # Validate selected colleges (limit to 3)
        if len(selected_ids) > 3:
            selected_ids = selected_ids[:3]
            flash('Maximum of 3 colleges can be compared at once.')
        
        # Get college data
        colleges = []
        for college_id in selected_ids:
            college = api_client.get_college_details(college_id)
            if college:
                colleges.append(college)
        
        # Default explanation
        explanation = None
        query = "How do these colleges compare for me?"
        
        if request.method == 'POST' and 'query' in request.form and colleges:
            # Get query from form
            query = request.form.get('query', '')
            
            # Initialize explainer
            explainer = DecisionExplainer(api_client)
            
            # Generate explanation
            explanation = explainer.explain_comparison(
                query=query,
                student_profile=user.profile.to_dict(),
                colleges=colleges
            )
        
        # Get all colleges for selection
        all_colleges = api_client.get_college_recommendations(user.id)
        
        # Get suggested questions
        suggested_questions = [
            "How do these colleges compare for me?",
            "Which of these colleges is the best fit for me?",
            "What are the main differences between these colleges?",
            "How do the costs of these colleges compare?",
            "Which college has the strongest academic match?",
            "What are the trade-offs between these options?"
        ]
        
        return render_template(
            'comparison_explainer.html',
            user=user,
            all_colleges=all_colleges.get('recommendations', []),
            selected_ids=selected_ids,
            colleges=colleges,
            query=query,
            explanation=explanation,
            suggested_questions=suggested_questions
        )
    
    @app.route('/api/explain-decision', methods=['POST'])
    def api_explain_decision():
        """API endpoint for decision explanation."""
        if 'user' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
            
        user = User.query.filter_by(username=session['user']).first()
        if not user:
            session.clear()
            return jsonify({'error': 'User not found'}), 401
        
        # Get data from request
        data = request.get_json()
        query = data.get('query', '')
        college_id = data.get('college_id', '')
        
        if not query or not college_id:
            return jsonify({'error': 'Missing query or college_id'}), 400
        
        # Initialize API client
        api_client = APIClient()
        
        # Get college data
        college = api_client.get_college_details(college_id)
        
        if not college:
            return jsonify({'error': 'College not found'}), 404
        
        # Initialize explainer
        explainer = DecisionExplainer(api_client)
        
        # Generate explanation
        explanation = explainer.explain_decision(
            query=query,
            student_profile=user.profile.to_dict(),
            college=college
        )
        
        return jsonify({
            'query': query,
            'college_id': college_id,
            'college_name': college.get('name', ''),
            'explanation': explanation
        })
