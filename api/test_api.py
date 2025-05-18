"""
API Endpoint Testing Script for College Counselor

This script tests the API endpoints for the College Counselor application.
"""

import sys
import json
import requests
from flask import Flask, jsonify
import unittest
from unittest.mock import patch

# Add the API directory to the path
sys.path.append('/home/ubuntu/promethios-college-counselor/api')

# Import the app
from college_counselor_api.app import app

class CollegeCounselorAPITest(unittest.TestCase):
    """Test case for the College Counselor API."""
    
    def setUp(self):
        """Set up the test client."""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_health_check(self):
        """Test the health check endpoint."""
        response = self.app.get('/api/health')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('version', data)
        
        print("✅ Health check endpoint test passed")
    
    def test_get_colleges(self):
        """Test the get colleges endpoint."""
        response = self.app.get('/api/colleges')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        
        # Check college structure
        college = data[0]
        self.assertIn('id', college)
        self.assertIn('name', college)
        self.assertIn('location', college)
        
        print(f"✅ Get colleges endpoint test passed - returned {len(data)} colleges")
    
    def test_search_colleges(self):
        """Test the search colleges endpoint."""
        # Test with a query
        response = self.app.get('/api/colleges/search?query=university')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        
        # Test with no query (should return error)
        response = self.app.get('/api/colleges/search')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
        
        print("✅ Search colleges endpoint test passed")
    
    def test_student_lifecycle(self):
        """Test the student lifecycle (create, get, update)."""
        # Create a student
        student_data = {
            'name': 'Test Student',
            'gpa': 3.8,
            'intended_majors': ['Computer Science', 'Mathematics'],
            'location_preference': 'CA',
            'budget': 50000
        }
        
        response = self.app.post('/api/students', 
                                json=student_data,
                                content_type='application/json')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', data)
        student_id = data['id']
        
        # Get the student
        response = self.app.get(f'/api/students/{student_id}')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['name'], 'Test Student')
        self.assertEqual(data['gpa'], 3.8)
        
        # Update the student
        update_data = {
            'name': 'Updated Student',
            'gpa': 4.0
        }
        
        response = self.app.put(f'/api/students/{student_id}',
                               json=update_data,
                               content_type='application/json')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['name'], 'Updated Student')
        self.assertEqual(data['gpa'], 4.0)
        
        # Get all students
        response = self.app.get('/api/students')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        
        print("✅ Student lifecycle test passed")
    
    def test_journal_entries(self):
        """Test the journal entries endpoints."""
        # Create a student first
        student_data = {
            'name': 'Journal Test Student',
            'gpa': 3.5
        }
        
        response = self.app.post('/api/students', 
                                json=student_data,
                                content_type='application/json')
        data = json.loads(response.data)
        student_id = data['id']
        
        # Create a journal entry
        journal_data = {
            'text': 'I am feeling excited about college applications but also a bit anxious.'
        }
        
        response = self.app.post(f'/api/students/{student_id}/journal',
                                json=journal_data,
                                content_type='application/json')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', data)
        self.assertIn('emotional_state', data)
        
        # Get journal entries
        response = self.app.get(f'/api/students/{student_id}/journal')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        
        print("✅ Journal entries test passed")
    
    def test_recommendations(self):
        """Test the recommendations endpoint."""
        # Create a student first
        student_data = {
            'name': 'Recommendation Test Student',
            'gpa': 3.9,
            'intended_majors': ['Computer Science'],
            'location_preference': 'MA',
            'budget': 70000
        }
        
        response = self.app.post('/api/students', 
                                json=student_data,
                                content_type='application/json')
        data = json.loads(response.data)
        student_id = data['id']
        
        # Get recommendations
        response = self.app.get(f'/api/students/{student_id}/recommendations')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        
        # Check recommendation structure
        recommendation = data[0]
        self.assertIn('college', recommendation)
        self.assertIn('trust_score', recommendation)
        self.assertIn('category', recommendation)
        self.assertIn('factors', recommendation)
        
        print(f"✅ Recommendations test passed - returned {len(data)} recommendations")
    
    def test_override(self):
        """Test the override endpoint."""
        # Create a student first
        student_data = {
            'name': 'Override Test Student',
            'gpa': 3.7
        }
        
        response = self.app.post('/api/students', 
                                json=student_data,
                                content_type='application/json')
        data = json.loads(response.data)
        student_id = data['id']
        
        # Create an override
        override_data = {
            'action': 'include',
            'justification': 'This college has a special program that matches the student\'s interests.'
        }
        
        response = self.app.post(f'/api/students/{student_id}/recommendations/1/override',
                                json=override_data,
                                content_type='application/json')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', data)
        self.assertEqual(data['student_id'], student_id)
        self.assertEqual(data['college_id'], '1')
        self.assertEqual(data['action'], 'include')
        
        print("✅ Override test passed")
    
    def test_report(self):
        """Test the report generation endpoint."""
        # Create a student first
        student_data = {
            'name': 'Report Test Student',
            'gpa': 3.6
        }
        
        response = self.app.post('/api/students', 
                                json=student_data,
                                content_type='application/json')
        data = json.loads(response.data)
        student_id = data['id']
        
        # Generate a report
        response = self.app.get(f'/api/students/{student_id}/report')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('student', data)
        self.assertIn('generated_at', data)
        self.assertIn('recommendations', data)
        self.assertIn('audit_trail', data)
        
        print("✅ Report generation test passed")
    
    def test_error_handling(self):
        """Test error handling for non-existent resources."""
        # Test non-existent student
        response = self.app.get('/api/students/999999')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', data)
        
        # Test journal entries for non-existent student
        response = self.app.get('/api/students/999999/journal')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', data)
        
        print("✅ Error handling test passed")

if __name__ == '__main__':
    # Run the tests
    print("Starting API endpoint tests...")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    print("API endpoint tests completed.")
