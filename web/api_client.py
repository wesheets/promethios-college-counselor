"""
API integration module for College Counselor application.

This module provides the connection between the web frontend and backend API services.
"""

import os
import requests
import json
from flask import current_app, session
from functools import wraps

# API configuration
API_URL = os.environ.get('API_URL', 'https://promethios-college-counselor-api-v1.onrender.com')
API_TIMEOUT = 10  # seconds

class APIClient:
    """Client for interacting with the College Counselor API."""
    
    def __init__(self, base_url=None):
        """Initialize the API client with base URL."""
        self.base_url = base_url or API_URL
        self.session = requests.Session()
    
    def _handle_response(self, response):
        """Handle API response and errors."""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            current_app.logger.error(f"API HTTP error: {e}")
            return {'error': True, 'message': str(e), 'status_code': response.status_code}
        except requests.exceptions.ConnectionError as e:
            current_app.logger.error(f"API connection error: {e}")
            return {'error': True, 'message': 'Connection to API failed', 'status_code': 503}
        except requests.exceptions.Timeout as e:
            current_app.logger.error(f"API timeout error: {e}")
            return {'error': True, 'message': 'API request timed out', 'status_code': 504}
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"API request error: {e}")
            return {'error': True, 'message': 'API request failed', 'status_code': 500}
        except json.JSONDecodeError as e:
            current_app.logger.error(f"API JSON decode error: {e}")
            return {'error': True, 'message': 'Invalid response from API', 'status_code': 500}
    
    def get(self, endpoint, params=None):
        """Make a GET request to the API."""
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = self.session.get(url, params=params, timeout=API_TIMEOUT)
            return self._handle_response(response)
        except Exception as e:
            current_app.logger.error(f"Unexpected error in API GET request: {e}")
            return {'error': True, 'message': 'Unexpected error occurred', 'status_code': 500}
    
    def post(self, endpoint, data=None):
        """Make a POST request to the API."""
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = self.session.post(url, json=data, timeout=API_TIMEOUT)
            return self._handle_response(response)
        except Exception as e:
            current_app.logger.error(f"Unexpected error in API POST request: {e}")
            return {'error': True, 'message': 'Unexpected error occurred', 'status_code': 500}
    
    def put(self, endpoint, data=None):
        """Make a PUT request to the API."""
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = self.session.put(url, json=data, timeout=API_TIMEOUT)
            return self._handle_response(response)
        except Exception as e:
            current_app.logger.error(f"Unexpected error in API PUT request: {e}")
            return {'error': True, 'message': 'Unexpected error occurred', 'status_code': 500}
    
    def delete(self, endpoint):
        """Make a DELETE request to the API."""
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = self.session.delete(url, timeout=API_TIMEOUT)
            return self._handle_response(response)
        except Exception as e:
            current_app.logger.error(f"Unexpected error in API DELETE request: {e}")
            return {'error': True, 'message': 'Unexpected error occurred', 'status_code': 500}

# API service functions
def get_college_recommendations(user_id, profile_data=None):
    """Get college recommendations for a user."""
    client = APIClient()
    
    # If profile data is provided, use it directly
    if profile_data:
        return client.post('/recommendations', {
            'user_id': user_id,
            'profile': profile_data
        })
    
    # Otherwise, get recommendations based on user ID
    return client.get(f'/recommendations/{user_id}')

def analyze_journal_entry(user_id, entry_text):
    """Analyze a journal entry for emotional state."""
    client = APIClient()
    return client.post('/analyze/journal', {
        'user_id': user_id,
        'text': entry_text
    })

def get_college_details(college_id):
    """Get detailed information about a college."""
    client = APIClient()
    return client.get(f'/colleges/{college_id}')

def search_colleges(query, filters=None):
    """Search for colleges based on query and filters."""
    client = APIClient()
    params = {'query': query}
    if filters:
        params.update(filters)
    return client.get('/colleges/search', params=params)

def generate_report(user_id):
    """Generate a comprehensive report for a user."""
    client = APIClient()
    return client.get(f'/report/{user_id}')

def get_emotional_state_history(user_id, days=30):
    """Get emotional state history for a user."""
    client = APIClient()
    return client.get(f'/emotional-state/{user_id}', {'days': days})

def get_trust_score_explanation(college_id, user_id):
    """Get explanation for a college's trust score."""
    client = APIClient()
    return client.get(f'/trust-score/{college_id}/{user_id}')

# Mock data for fallback when API is unavailable
def get_mock_data(endpoint, user_id=None):
    """Get mock data for API endpoints when the real API is unavailable."""
    mock_data = {
        'recommendations': [
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
            },
            {
                'id': 4,
                'name': 'Tech Institute',
                'location': 'California',
                'trust_score': 88,
                'category': 'Reach'
            },
            {
                'id': 5,
                'name': 'Community College',
                'location': 'New York',
                'trust_score': 95,
                'category': 'Safety'
            }
        ],
        'journal_analysis': {
            'sentiment_score': 75,
            'uncertainty_score': 30,
            'agitation_score': 20,
            'emotion_summary': "You seem generally positive about your college prospects."
        },
        'emotional_state_history': [
            {'date': '2025-05-01', 'sentiment': 65, 'uncertainty': 45, 'agitation': 30},
            {'date': '2025-05-05', 'sentiment': 70, 'uncertainty': 40, 'agitation': 25},
            {'date': '2025-05-10', 'sentiment': 60, 'uncertainty': 50, 'agitation': 35},
            {'date': '2025-05-15', 'sentiment': 75, 'uncertainty': 30, 'agitation': 20}
        ],
        'report': {
            'student': {
                'name': 'John Smith',
                'gpa': 3.8,
                'intended_majors': ['Computer Science', 'Mathematics'],
                'location_preference': 'California',
                'budget': 50000
            },
            'emotional_state': {
                'sentiment': 75,
                'certainty': 70,
                'calmness': 80,
                'summary': 'Your emotional state appears balanced for decision-making.'
            },
            'recommendations': [
                {
                    'college': 'Ivy University',
                    'category': 'Reach',
                    'trust_score': 85,
                    'academic_match': 80,
                    'budget_match': 70
                },
                {
                    'college': 'State University',
                    'category': 'Target',
                    'trust_score': 92,
                    'academic_match': 90,
                    'budget_match': 85
                }
            ]
        },
        'trust_score_explanation': {
            'college': 'State University',
            'overall_score': 92,
            'factors': [
                {'name': 'Data Freshness', 'score': 95, 'description': 'College data was updated within the last month'},
                {'name': 'Profile Match', 'score': 90, 'description': 'Your academic profile closely matches successful applicants'},
                {'name': 'Budget Alignment', 'score': 85, 'description': 'College costs are within your specified budget'},
                {'name': 'Emotional Fit', 'score': 88, 'description': 'Based on your journal entries, this college aligns with your preferences'}
            ]
        }
    }
    
    if endpoint == 'recommendations':
        return {'recommendations': mock_data['recommendations']}
    elif endpoint == 'journal_analysis':
        return mock_data['journal_analysis']
    elif endpoint == 'emotional_state_history':
        return {'history': mock_data['emotional_state_history']}
    elif endpoint == 'report':
        return mock_data['report']
    elif endpoint == 'trust_score_explanation':
        return mock_data['trust_score_explanation']
    else:
        return {'error': True, 'message': 'Unknown endpoint for mock data'}

# API request decorator with fallback to mock data
def api_request_with_fallback(endpoint):
    """Decorator for API requests with fallback to mock data."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                # Check if there was an error in the API response
                if result.get('error'):
                    current_app.logger.warning(f"API error, using mock data for {endpoint}: {result.get('message')}")
                    return get_mock_data(endpoint, kwargs.get('user_id'))
                return result
            except Exception as e:
                current_app.logger.error(f"API request failed, using mock data for {endpoint}: {e}")
                return get_mock_data(endpoint, kwargs.get('user_id'))
        return wrapper
    return decorator

# Apply the decorator to API service functions
get_college_recommendations = api_request_with_fallback('recommendations')(get_college_recommendations)
analyze_journal_entry = api_request_with_fallback('journal_analysis')(analyze_journal_entry)
get_emotional_state_history = api_request_with_fallback('emotional_state_history')(get_emotional_state_history)
generate_report = api_request_with_fallback('report')(generate_report)
get_trust_score_explanation = api_request_with_fallback('trust_score_explanation')(get_trust_score_explanation)
