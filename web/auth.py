"""
Authentication routes and functionality for College Counselor application.

This module provides routes for user registration, login, logout, and password management.
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, UserProfile
import re
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        name = request.form.get('name')
        
        # Validation
        error = None
        
        if not username or not email or not password or not confirm_password:
            error = 'All fields are required.'
        elif not re.match(r'^[a-zA-Z0-9_]+$', username):
            error = 'Username can only contain letters, numbers, and underscores.'
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            error = 'Invalid email address.'
        elif password != confirm_password:
            error = 'Passwords do not match.'
        elif len(password) < 8:
            error = 'Password must be at least 8 characters long.'
        elif User.query.filter_by(username=username).first():
            error = 'Username already exists.'
        elif User.query.filter_by(email=email).first():
            error = 'Email already registered.'
            
        if error:
            flash(error)
            return render_template('register.html')
            
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password=password,
            role='student',
            name=name
        )
        
        # Create empty profile
        new_profile = UserProfile(user=new_user)
        
        # Save to database
        db.session.add(new_user)
        db.session.add(new_profile)
        db.session.commit()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('auth.login'))
        
    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Validation
        error = None
        
        if not username or not password:
            error = 'Username and password are required.'
            
        if not error:
            user = User.query.filter_by(username=username).first()
            
            if not user or not user.check_password(password):
                error = 'Invalid username or password.'
                
        if error:
            flash(error)
            return render_template('login.html', error=error)
            
        # Update last login time
        user.update_last_login()
        
        # Set session variables
        session['user'] = user.username
        session['role'] = user.role
        session['name'] = user.name
        session['user_id'] = user.id
        
        flash(f'Welcome back, {user.name or user.username}!')
        return redirect(url_for('profile'))
        
    return render_template('login.html')

@auth.route('/logout')
def logout():
    """Handle user logout."""
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('index'))

@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    """Handle password reset request."""
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('Email is required.')
            return render_template('reset_password_request.html')
            
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('Email not found.')
            return render_template('reset_password_request.html')
            
        # In a real app, send password reset email
        # For demo, just redirect to reset form
        flash('Password reset instructions sent to your email.')
        return redirect(url_for('auth.login'))
        
    return render_template('reset_password_request.html')

@auth.route('/profile/password', methods=['GET', 'POST'])
def change_password():
    """Handle password change."""
    if 'user' not in session:
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        error = None
        
        if not current_password or not new_password or not confirm_password:
            error = 'All fields are required.'
        elif new_password != confirm_password:
            error = 'New passwords do not match.'
        elif len(new_password) < 8:
            error = 'Password must be at least 8 characters long.'
            
        if not error:
            user = User.query.filter_by(username=session['user']).first()
            
            if not user or not user.check_password(current_password):
                error = 'Current password is incorrect.'
                
        if error:
            flash(error)
            return render_template('change_password.html')
            
        # Update password
        user = User.query.filter_by(username=session['user']).first()
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        flash('Password updated successfully.')
        return redirect(url_for('profile'))
        
    return render_template('change_password.html')
