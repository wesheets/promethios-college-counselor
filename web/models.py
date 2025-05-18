"""
User model and authentication for College Counselor application.

This module provides user registration, authentication, and profile management.
"""

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication and profile management."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')
    name = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    journal_entries = db.relationship('JournalEntry', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, username, email, password, role='student', name=None):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.role = role
        self.name = name
    
    def check_password(self, password):
        """Verify the password against the stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Convert user to dictionary for API responses."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


class UserProfile(db.Model):
    """User profile with academic and preference information."""
    
    __tablename__ = 'user_profiles'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    gpa = db.Column(db.Float, nullable=True)
    graduation_year = db.Column(db.String(4), nullable=True)
    intended_majors = db.Column(db.String(255), nullable=True)  # Comma-separated list
    location_preference = db.Column(db.String(100), nullable=True)
    size_preference = db.Column(db.String(20), nullable=True)  # small, medium, large
    setting_preference = db.Column(db.String(20), nullable=True)  # urban, suburban, rural
    budget = db.Column(db.Integer, nullable=True)  # Annual budget in USD
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert profile to dictionary for API responses."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'gpa': self.gpa,
            'graduation_year': self.graduation_year,
            'intended_majors': self.intended_majors.split(',') if self.intended_majors else [],
            'location_preference': self.location_preference,
            'size_preference': self.size_preference,
            'setting_preference': self.setting_preference,
            'budget': self.budget,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<UserProfile {self.user_id}>'


class JournalEntry(db.Model):
    """Journal entries for emotional state tracking."""
    
    __tablename__ = 'journal_entries'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Emotional state analysis
    sentiment_score = db.Column(db.Integer, nullable=True)  # 0-100
    uncertainty_score = db.Column(db.Integer, nullable=True)  # 0-100
    agitation_score = db.Column(db.Integer, nullable=True)  # 0-100
    emotion_summary = db.Column(db.String(255), nullable=True)
    
    def to_dict(self):
        """Convert journal entry to dictionary for API responses."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'emotional_state': {
                'sentiment_score': self.sentiment_score,
                'uncertainty_score': self.uncertainty_score,
                'agitation_score': self.agitation_score,
                'summary': self.emotion_summary
            }
        }
    
    def __repr__(self):
        return f'<JournalEntry {self.id}>'


def init_db(app):
    """Initialize the database with the Flask app."""
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        
        # Create default users if they don't exist
        if not User.query.filter_by(username='student').first():
            student = User(
                username='student',
                email='student@example.com',
                password='password',
                role='student',
                name='John Smith'
            )
            db.session.add(student)
            
            # Create profile for student
            profile = UserProfile(user=student)
            db.session.add(profile)
            
        if not User.query.filter_by(username='counselor').first():
            counselor = User(
                username='counselor',
                email='counselor@example.com',
                password='password',
                role='counselor',
                name='Dr. Jane Doe'
            )
            db.session.add(counselor)
            
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                password='password',
                role='admin',
                name='Admin User'
            )
            db.session.add(admin)
            
        db.session.commit()
