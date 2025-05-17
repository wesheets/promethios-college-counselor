"""
College Counselor API - Main Application

This module serves as the entry point for the College Counselor API,
providing endpoints for student profiles, journal entries, college recommendations,
and report generation.
"""

import os
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from .counseling_wrapper import CounselingWrapper
from .college_data_loader import DataSourceManager, MockDataSource

# Load environment variables
load_dotenv()

# Initialize Flask application
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Initialize data source manager
data_source_manager = DataSourceManager()
data_source_manager.register_data_source('mock', MockDataSource())

# Initialize counseling wrapper
counseling_wrapper = CounselingWrapper(data_source_manager)

# In-memory storage for demo
students = {}
journal_entries = {}
recommendations = {}
overrides = {}

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'version': '0.1.0'
    })

@app.route('/api/students', methods=['GET'])
def get_students():
    """Get all students."""
    return jsonify(list(students.values()))

@app.route('/api/students/<student_id>', methods=['GET'])
def get_student(student_id):
    """Get a specific student by ID."""
    if student_id not in students:
        return jsonify({'error': 'Student not found'}), 404
    return jsonify(students[student_id])

@app.route('/api/students', methods=['POST'])
def create_student():
    """Create a new student."""
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Generate a simple ID
    student_id = str(len(students) + 1)
    
    # Create student record
    students[student_id] = {
        'id': student_id,
        'name': data.get('name', ''),
        'gpa': data.get('gpa', 0.0),
        'intended_majors': data.get('intended_majors', []),
        'location_preference': data.get('location_preference', ''),
        'budget': data.get('budget', 0.0),
        'created_at': counseling_wrapper.get_timestamp()
    }
    
    # Initialize journal entries for this student
    journal_entries[student_id] = []
    
    return jsonify(students[student_id]), 201

@app.route('/api/students/<student_id>', methods=['PUT'])
def update_student(student_id):
    """Update a specific student by ID."""
    if student_id not in students:
        return jsonify({'error': 'Student not found'}), 404
    
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Update student record
    student = students[student_id]
    student['name'] = data.get('name', student['name'])
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
