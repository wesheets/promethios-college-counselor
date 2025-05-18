"""
Database configuration and testing for College Counselor application.

This module validates the database setup and ensures persistent storage is working correctly.
"""

import os
import sys
from flask import Flask
from models import db, User, UserProfile, JournalEntry, init_db

def create_test_app():
    """Create a test Flask application for database validation."""
    app = Flask(__name__)
    
    # Use SQLite for testing
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_college_counselor.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    
    return app

def validate_database_setup():
    """Validate database setup and model relationships."""
    app = create_test_app()
    
    with app.app_context():
        # Initialize database
        init_db(app)
        
        print("Database initialized successfully.")
        
        # Verify default users were created
        student = User.query.filter_by(username='student').first()
        counselor = User.query.filter_by(username='counselor').first()
        admin = User.query.filter_by(username='admin').first()
        
        if student and counselor and admin:
            print("Default users created successfully.")
        else:
            print("ERROR: Default users not created properly.")
            return False
        
        # Verify student profile was created
        if student.profile:
            print("Student profile created successfully.")
        else:
            print("ERROR: Student profile not created properly.")
            return False
        
        # Test creating a journal entry
        entry = JournalEntry(
            user_id=student.id,
            title="Test Entry",
            content="This is a test journal entry to validate database persistence.",
            sentiment_score=75,
            uncertainty_score=30,
            agitation_score=20,
            emotion_summary="Test emotional state analysis."
        )
        
        db.session.add(entry)
        db.session.commit()
        
        # Verify journal entry was saved
        saved_entry = JournalEntry.query.filter_by(title="Test Entry").first()
        if saved_entry and saved_entry.content == "This is a test journal entry to validate database persistence.":
            print("Journal entry created and retrieved successfully.")
        else:
            print("ERROR: Journal entry not saved or retrieved properly.")
            return False
        
        # Test updating user profile
        student.profile.gpa = 3.8
        student.profile.graduation_year = "2026"
        student.profile.intended_majors = "Computer Science,Mathematics"
        student.profile.location_preference = "California"
        student.profile.size_preference = "medium"
        student.profile.setting_preference = "urban"
        student.profile.budget = 50000
        
        db.session.commit()
        
        # Verify profile updates were saved
        updated_profile = UserProfile.query.filter_by(user_id=student.id).first()
        if (updated_profile.gpa == 3.8 and 
            updated_profile.graduation_year == "2026" and
            updated_profile.intended_majors == "Computer Science,Mathematics"):
            print("Profile updates saved successfully.")
        else:
            print("ERROR: Profile updates not saved properly.")
            return False
        
        # Test user authentication
        if student.check_password("password"):
            print("User authentication working correctly.")
        else:
            print("ERROR: User authentication not working properly.")
            return False
        
        print("\nAll database validation tests passed successfully!")
        return True

def setup_production_database(app):
    """Configure and initialize the production database."""
    # Set database URI based on environment
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url and database_url.startswith('postgres://'):
        # Heroku-style PostgreSQL URL needs to be updated for SQLAlchemy 1.4+
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    # Default to SQLite if no database URL is provided
    if not database_url:
        database_url = 'sqlite:///college_counselor.db'
        print(f"No DATABASE_URL found. Using SQLite: {database_url}")
    else:
        print(f"Using database: {database_url}")
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    init_db(app)
    
    print("Production database initialized successfully.")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "validate":
        success = validate_database_setup()
        sys.exit(0 if success else 1)
    else:
        print("Usage: python database_validation.py validate")
        sys.exit(1)
