"""
Database validation script for SQLAlchemy 2.x compatibility.

This script validates the database configuration and tables for the College Counselor application.
"""

import os
import sys
from flask import Flask
from sqlalchemy.sql import text
from models import db, init_db, User, UserProfile, JournalEntry

def create_test_app():
    """Create a test Flask application for database validation."""
    app = Flask(__name__)
    
    # Database configuration
    # Handle Render's PostgreSQL connection string if present
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        # Convert postgres:// to postgresql:// for SQLAlchemy 1.4+
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # For Render deployment, use a writable directory in /tmp
        if os.environ.get('RENDER'):
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/college_counselor_test.db'
        else:
            # For local development
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/college_counselor_test.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    return app

def validate_database():
    """Validate database configuration and tables."""
    app = create_test_app()
    init_db(app)
    
    with app.app_context():
        # Check if tables exist
        tables = ['users', 'user_profiles', 'journal_entries']
        for table in tables:
            try:
                # Use SQLAlchemy 2.x compatible method to check if table exists
                result = db.session.execute(text(f"SELECT 1 FROM {table} LIMIT 1"))
                print(f"✅ Table '{table}' exists and is accessible")
            except Exception as e:
                print(f"❌ Error accessing table '{table}': {str(e)}")
                return False
        
        # Check if default users exist
        default_users = ['student', 'counselor', 'admin']
        for username in default_users:
            user = User.query.filter_by(username=username).first()
            if user:
                print(f"✅ Default user '{username}' exists")
            else:
                print(f"❌ Default user '{username}' does not exist")
                return False
        
        # Check if student profile exists
        student = User.query.filter_by(username='student').first()
        if student and student.profile:
            print(f"✅ Student profile exists")
        else:
            print(f"❌ Student profile does not exist")
            return False
        
        # Create a test journal entry
        try:
            test_entry = JournalEntry(
                user_id=student.id,
                title="Test Journal Entry",
                content="This is a test journal entry for database validation.",
                sentiment_score=75,
                uncertainty_score=30,
                agitation_score=20,
                emotion_summary="Test emotion summary"
            )
            db.session.add(test_entry)
            db.session.commit()
            print(f"✅ Successfully created test journal entry")
            
            # Retrieve the test entry
            retrieved_entry = JournalEntry.query.filter_by(title="Test Journal Entry").first()
            if retrieved_entry and retrieved_entry.content == "This is a test journal entry for database validation.":
                print(f"✅ Successfully retrieved test journal entry")
            else:
                print(f"❌ Failed to retrieve test journal entry")
                return False
            
            # Clean up test entry
            db.session.delete(retrieved_entry)
            db.session.commit()
            print(f"✅ Successfully cleaned up test journal entry")
        except Exception as e:
            print(f"❌ Error during journal entry test: {str(e)}")
            return False
        
        # Update student profile
        try:
            student.profile.gpa = 3.8
            student.profile.graduation_year = "2025"
            student.profile.intended_majors = "Computer Science,Mathematics"
            db.session.commit()
            print(f"✅ Successfully updated student profile")
            
            # Verify update
            updated_student = User.query.filter_by(username='student').first()
            if updated_student.profile.gpa == 3.8 and updated_student.profile.graduation_year == "2025":
                print(f"✅ Successfully verified student profile update")
            else:
                print(f"❌ Failed to verify student profile update")
                return False
        except Exception as e:
            print(f"❌ Error during profile update test: {str(e)}")
            return False
        
        # Test user authentication
        try:
            if student.check_password('password'):
                print(f"✅ User authentication works correctly")
            else:
                print(f"❌ User authentication failed")
                return False
        except Exception as e:
            print(f"❌ Error during authentication test: {str(e)}")
            return False
        
        print("\n✅ All database validation tests passed successfully!")
        return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "validate":
        success = validate_database()
        if not success:
            print("\n❌ Database validation failed!")
            sys.exit(1)
    else:
        print("Usage: python database_validation.py validate")
        sys.exit(1)
