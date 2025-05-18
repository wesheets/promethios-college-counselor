"""
Database validation script for College Counselor application.

This script validates database connectivity and persistence.
"""

import os
import sys
from flask import Flask
from models import db, User, UserProfile, JournalEntry
from sqlalchemy import text

def create_test_app():
    """Create a test Flask application for database validation."""
    app = Flask(__name__)
    
    # Database configuration
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        # Convert postgres:// to postgresql:// for SQLAlchemy 1.4+
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Use absolute path for SQLite
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:////home/ubuntu/promethios-college-counselor/web/instance/college_counselor.db')
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    return app

def initialize_database(app):
    """Initialize database tables."""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            return False

def validate_database_connection(app):
    """Validate database connection."""
    with app.app_context():
        try:
            # Check if connection works using SQLAlchemy 2.x compatible method
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                conn.commit()
            print("✅ Database connection successful")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False

def validate_user_creation(app):
    """Validate user creation and retrieval."""
    with app.app_context():
        try:
            # Create test user
            test_user = User(
                username=f"test_user_{os.urandom(4).hex()}",
                email=f"test_{os.urandom(4).hex()}@example.com",
                password="test_password"
            )
            db.session.add(test_user)
            db.session.commit()
            
            # Retrieve user
            user_id = test_user.id
            retrieved_user = User.query.get(user_id)
            
            if retrieved_user and retrieved_user.username == test_user.username:
                print(f"✅ User creation and retrieval successful (ID: {user_id})")
                return user_id
            else:
                print("❌ User retrieval failed")
                return None
        except Exception as e:
            print(f"❌ User creation failed: {e}")
            return None

def validate_profile_creation(app, user_id):
    """Validate profile creation and update."""
    if not user_id:
        print("❌ Profile validation skipped (no user)")
        return False
    
    with app.app_context():
        try:
            # Get user
            user = User.query.get(user_id)
            
            # Create profile
            profile = UserProfile(user=user)
            profile.gpa = 3.8
            profile.graduation_year = "2023"
            profile.intended_majors = "Computer Science,Mathematics"
            profile.location_preference = "West Coast"
            profile.size_preference = "medium"
            profile.setting_preference = "urban"
            profile.budget = 25000
            
            db.session.add(profile)
            db.session.commit()
            
            # Retrieve profile
            profile_id = profile.id
            retrieved_profile = UserProfile.query.get(profile_id)
            
            if (retrieved_profile and 
                retrieved_profile.gpa == 3.8 and
                retrieved_profile.budget == 25000):
                print(f"✅ Profile creation and retrieval successful (ID: {profile_id})")
                
                # Test update
                retrieved_profile.gpa = 3.9
                db.session.commit()
                
                updated_profile = UserProfile.query.get(profile_id)
                if updated_profile.gpa == 3.9:
                    print("✅ Profile update successful")
                    return True
                else:
                    print("❌ Profile update failed")
                    return False
            else:
                print("❌ Profile retrieval failed")
                return False
        except Exception as e:
            print(f"❌ Profile creation failed: {e}")
            return False

def validate_journal_entry(app, user_id):
    """Validate journal entry creation and retrieval."""
    if not user_id:
        print("❌ Journal validation skipped (no user)")
        return False
    
    with app.app_context():
        try:
            # Create journal entry
            entry = JournalEntry(
                user_id=user_id,
                title="Test Journal Entry",
                content="This is a test journal entry to validate database persistence.",
                sentiment_score=75,
                uncertainty_score=30,
                agitation_score=20,
                emotion_summary="Neutral with slight positive sentiment."
            )
            
            db.session.add(entry)
            db.session.commit()
            
            # Retrieve entry
            entry_id = entry.id
            retrieved_entry = JournalEntry.query.get(entry_id)
            
            if (retrieved_entry and 
                retrieved_entry.title == "Test Journal Entry" and
                retrieved_entry.sentiment_score == 75):
                print(f"✅ Journal entry creation and retrieval successful (ID: {entry_id})")
                return True
            else:
                print("❌ Journal entry retrieval failed")
                return False
        except Exception as e:
            print(f"❌ Journal entry creation failed: {e}")
            return False

def cleanup_test_data(app, user_id):
    """Clean up test data."""
    if not user_id:
        return
    
    with app.app_context():
        try:
            user = User.query.get(user_id)
            if user:
                db.session.delete(user)
                db.session.commit()
                print(f"✅ Test data cleanup successful (User ID: {user_id})")
        except Exception as e:
            print(f"❌ Test data cleanup failed: {e}")

def main():
    """Main validation function."""
    print("\n=== Database Validation ===\n")
    
    # Create test app
    app = create_test_app()
    
    # Initialize database tables
    if not initialize_database(app):
        sys.exit(1)
    
    # Validate database connection
    if not validate_database_connection(app):
        sys.exit(1)
    
    # Validate user creation
    user_id = validate_user_creation(app)
    
    # Validate profile creation
    profile_success = validate_profile_creation(app, user_id)
    
    # Validate journal entry
    journal_success = validate_journal_entry(app, user_id)
    
    # Clean up test data
    cleanup_test_data(app, user_id)
    
    # Print summary
    print("\n=== Validation Summary ===\n")
    print(f"Database Connection: {'✅ Success' if user_id else '❌ Failed'}")
    print(f"User Creation/Retrieval: {'✅ Success' if user_id else '❌ Failed'}")
    print(f"Profile Creation/Update: {'✅ Success' if profile_success else '❌ Failed'}")
    print(f"Journal Entry Creation/Retrieval: {'✅ Success' if journal_success else '❌ Failed'}")
    
    if user_id and profile_success and journal_success:
        print("\n✅ All database validations passed! Data persistence is working correctly.")
        return 0
    else:
        print("\n❌ Some database validations failed. Please check the logs above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
