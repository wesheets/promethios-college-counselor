"""
API Entry Point - Main Flask App

This is the main entry point for the College Counselor API.
It handles all API routes and integrates with the counseling wrapper.
"""

from flask import Flask, request, jsonify
import os
import json
import logging
from datetime import datetime
import sys

# Add the current directory and parent directory to the path to ensure imports work correctly
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.dirname(current_dir))

# Import counseling wrapper
from college_counselor_api.counseling_wrapper import CounselingWrapper
from college_counselor_api.college_data_loader import DataSourceManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize data source manager
data_source_manager = DataSourceManager()

# Initialize counseling wrapper with data source manager
counseling_wrapper = CounselingWrapper(data_source_manager)

# In-memory storage for demo
students = {
    '1': {
        'id': '1',
        'name': 'John Smith',
        'email': 'john.smith@example.com',
        'gpa': 3.8,
        'intended_majors': ['Computer Science', 'Mathematics'],
        'location_preference': 'California',
        'budget': 50000,
        'created_at': '2025-05-01T10:00:00Z',
        'updated_at': '2025-05-01T10:00:00Z'
    }
}

journal_entries = {
    '1': [
        {
            'id': 1,
            'text': 'I\'m feeling anxious about college applications. There are so many options and I\'m not sure where to start.',
            'timestamp': '2025-05-05T14:30:00Z',
            'emotional_state': {
                'primary': 'anxious',
                'secondary': 'overwhelmed',
                'intensity': 0.7
            }
        },
        {
            'id': 2,
            'text': 'Visited State University today. The campus was beautiful and I really liked the computer science department.',
            'timestamp': '2025-05-10T18:45:00Z',
            'emotional_state': {
                'primary': 'excited',
                'secondary': 'hopeful',
                'intensity': 0.8
            }
        }
    ]
}

recommendations = {}
overrides = {}

# API routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/students', methods=['GET'])
def get_students():
    """Get a list of all students."""
    return jsonify(list(students.values()))

@app.route('/api/students', methods=['POST'])
def create_student():
    """Create a new student."""
    data = request.json
    if not data or 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400
    
    # Create student
    student_id = str(len(students) + 1)
    timestamp = counseling_wrapper.get_timestamp()
    
    student = {
        'id': student_id,
        'name': data['name'],
        'email': data.get('email', ''),
        'gpa': data.get('gpa', 0.0),
        'intended_majors': data.get('intended_majors', []),
        'location_preference': data.get('location_preference', ''),
        'budget': data.get('budget', 0),
        'created_at': timestamp,
        'updated_at': timestamp
    }
    
    students[student_id] = student
    
    return jsonify(student), 201

@app.route('/api/students/<student_id>', methods=['GET'])
def get_student(student_id):
    """Get a student by ID."""
    if student_id not in students:
        return jsonify({'error': 'Student not found'}), 404
    
    return jsonify(students[student_id])

@app.route('/api/students/<student_id>', methods=['PUT'])
def update_student(student_id):
    """Update a student."""
    if student_id not in students:
        return jsonify({'error': 'Student not found'}), 404
    
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    student = students[student_id]
    
    # Update fields
    student['name'] = data.get('name', student['name'])
    student['email'] = data.get('email', student['email'])
    student['gpa'] = data.get('gpa', student['gpa'])
    student['intended_majors'] = data.get('intended_majors', student['intended_majors'])
    student['location_preference'] = data.get('location_preference', student['location_preference'])
    student['budget'] = data.get('budget', student['budget'])
    student['updated_at'] = counseling_wrapper.get_timestamp()
    
    return jsonify(student)

@app.route('/api/students/<student_id>/journal', methods=['GET'])
def get_journal_entries(student_id):
    """Get all journal entries for a student."""
    if student_id not in students:
        return jsonify({'error': 'Student not found'}), 404
    
    return jsonify(journal_entries.get(student_id, []))

@app.route('/api/students/<student_id>/journal', methods=['POST'])
def create_journal_entry(student_id):
    """Create a new journal entry for a student."""
    if student_id not in students:
        return jsonify({'error': 'Student not found'}), 404
    
    data = request.json
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    
    # Create journal entry
    entry = {
        'id': len(journal_entries.get(student_id, [])) + 1,
        'text': data['text'],
        'timestamp': counseling_wrapper.get_timestamp()
    }
    
    # Analyze emotional state
    emotional_state = counseling_wrapper.analyze_emotional_state(data['text'])
    entry['emotional_state'] = emotional_state
    
    # Add to journal entries
    if student_id not in journal_entries:
        journal_entries[student_id] = []
    journal_entries[student_id].append(entry)
    
    return jsonify(entry), 201

@app.route('/api/colleges', methods=['GET'])
def get_colleges():
    """Get a list of colleges."""
    limit = request.args.get('limit', 25, type=int)
    data_source = data_source_manager.get_data_source('mock')
    colleges = data_source.get_colleges(limit=limit)
    return jsonify(colleges)

@app.route('/api/colleges/search', methods=['GET'])
def search_colleges():
    """Search for colleges by name or other criteria."""
    query = request.args.get('query', '')
    limit = request.args.get('limit', 25, type=int)
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    data_source = data_source_manager.get_data_source('mock')
    colleges = data_source.search_colleges(query, limit=limit)
    return jsonify(colleges)

@app.route('/api/students/<student_id>/recommendations', methods=['GET'])
def get_recommendations(student_id):
    """Get college recommendations for a student."""
    if student_id not in students:
        return jsonify({'error': 'Student not found'}), 404
    
    # Get recommendations from cache or generate new ones
    if student_id in recommendations:
        return jsonify(recommendations[student_id])
    
    # Get student profile
    student = students[student_id]
    
    # Get journal entries
    entries = journal_entries.get(student_id, [])
    
    # Generate recommendations
    student_recommendations = counseling_wrapper.generate_recommendations(
        student, entries
    )
    
    # Cache recommendations
    recommendations[student_id] = student_recommendations
    
    return jsonify(student_recommendations)

@app.route('/api/students/<student_id>/recommendations/<college_id>/override', methods=['POST'])
def create_override(student_id, college_id):
    """Create an override for a recommendation."""
    if student_id not in students:
        return jsonify({'error': 'Student not found'}), 404
    
    data = request.json
    if not data or 'justification' not in data or 'action' not in data:
        return jsonify({'error': 'Justification and action required'}), 400
    
    # Create override
    override_id = f"{student_id}_{college_id}_{len(overrides) + 1}"
    override = {
        'id': override_id,
        'student_id': student_id,
        'college_id': college_id,
        'action': data['action'],
        'justification': data['justification'],
        'timestamp': counseling_wrapper.get_timestamp()
    }
    
    # Add to overrides
    overrides[override_id] = override
    
    # Add to audit trail
    counseling_wrapper.record_override(student_id, college_id, override)
    
    return jsonify(override), 201

@app.route('/api/students/<student_id>/report', methods=['GET'])
def generate_report(student_id):
    """Generate a report for a student."""
    if student_id not in students:
        return jsonify({'error': 'Student not found'}), 404
    
    # Get student profile
    student = students[student_id]
    
    # Get journal entries
    entries = journal_entries.get(student_id, [])
    
    # Get recommendations
    student_recommendations = recommendations.get(student_id, [])
    
    # Get overrides
    student_overrides = [o for o in overrides.values() if o['student_id'] == student_id]
    
    # Generate report
    report = counseling_wrapper.generate_report(
        student, entries, student_recommendations, student_overrides
    )
    
    return jsonify(report)

if __name__ == '__main__':
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
