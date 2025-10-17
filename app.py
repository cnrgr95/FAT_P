from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
import json
from config import config
import re
from functools import wraps
import logging
from logging.handlers import RotatingFileHandler

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Load configuration
config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# Configure logging
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/cost_calculation.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Cost Calculation System startup')

# Initialize extensions
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Security headers
@app.after_request
def after_request(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://code.jquery.com https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; img-src 'self' data:; font-src 'self' https://cdnjs.cloudflare.com;"
    return response

# Input validation functions
def validate_input(data, field_type='text', max_length=255):
    """Validate and sanitize input data"""
    if not data:
        return None
    
    # Remove leading/trailing whitespace
    data = str(data).strip()
    
    # Check length
    if len(data) > max_length:
        raise ValueError(f"Input too long. Maximum {max_length} characters allowed.")
    
    # Type-specific validation
    if field_type == 'email':
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data):
            raise ValueError("Invalid email format")
    elif field_type == 'numeric':
        try:
            float(data)
        except ValueError:
            raise ValueError("Invalid numeric value")
    elif field_type == 'date':
        try:
            datetime.strptime(data, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")
    
    # Basic XSS protection
    dangerous_chars = ['<', '>', '"', "'", '&']
    for char in dangerous_chars:
        if char in data:
            data = data.replace(char, '')
    
    return data

def validate_cost_data(form_data):
    """Validate cost form data"""
    errors = []
    
    try:
        name = validate_input(form_data.get('name'), 'text', 200)
        if not name:
            errors.append('Name is required')
    except ValueError as e:
        errors.append(f'Name: {str(e)}')
    
    try:
        amount = validate_input(form_data.get('amount'), 'numeric')
        if not amount or float(amount) < 0:
            errors.append('Amount must be a positive number')
    except ValueError as e:
        errors.append(f'Amount: {str(e)}')
    
    try:
        date = validate_input(form_data.get('date'), 'date')
        if not date:
            errors.append('Date is required')
    except ValueError as e:
        errors.append(f'Date: {str(e)}')
    
    description = validate_input(form_data.get('description'), 'text', 1000)
    category = validate_input(form_data.get('category'), 'text', 100)
    
    return errors, {
        'name': name,
        'amount': amount,
        'date': date,
        'description': description,
        'category': category
    }

def validate_tour_data(form_data):
    """Validate tour program form data"""
    errors = []
    
    try:
        name = validate_input(form_data.get('name'), 'text', 200)
        if not name:
            errors.append('Name is required')
    except ValueError as e:
        errors.append(f'Name: {str(e)}')
    
    try:
        start_date = validate_input(form_data.get('start_date'), 'date')
        if not start_date:
            errors.append('Start date is required')
    except ValueError as e:
        errors.append(f'Start date: {str(e)}')
    
    try:
        end_date = validate_input(form_data.get('end_date'), 'date')
        if not end_date:
            errors.append('End date is required')
    except ValueError as e:
        errors.append(f'End date: {str(e)}')
    
    # Check date logic
    if start_date and end_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            if end_dt <= start_dt:
                errors.append('End date must be after start date')
        except ValueError:
            pass
    
    total_cost = validate_input(form_data.get('total_cost'), 'numeric') or '0'
    if float(total_cost) < 0:
        errors.append('Total cost must be a positive number')
    
    description = validate_input(form_data.get('description'), 'text', 1000)
    destination = validate_input(form_data.get('destination'), 'text', 200)
    
    return errors, {
        'name': name,
        'start_date': start_date,
        'end_date': end_date,
        'total_cost': total_cost,
        'description': description,
        'destination': destination
    }

# Load language files
def load_language(lang_code):
    """Load language file for given language code"""
    try:
        with open(f'languages/{lang_code}.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback to English if language file not found
        with open('languages/en.json', 'r', encoding='utf-8') as f:
            return json.load(f)

def get_translation(key, lang='en'):
    """Get translation for given key and language"""
    translations = load_language(lang)
    return translations.get(key, key)

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(100))
    position = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<User {self.username}>'

# Cost model
class Cost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.String(100))
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = db.relationship('User', backref=db.backref('costs', lazy=True))

# Tour Program model
class TourProgram(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    destination = db.Column(db.String(200))
    total_cost = db.Column(db.Numeric(10, 2))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = db.relationship('User', backref=db.backref('tour_programs', lazy=True))

# System Settings model
class SystemSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Context processor for translations
@app.context_processor
def inject_translations():
    lang = session.get('language', 'en')
    return dict(_=lambda key: get_translation(key, lang))

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # Basic validation
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('auth/login.html')
        
        # Rate limiting (simple implementation)
        if not hasattr(session, 'login_attempts'):
            session['login_attempts'] = 0
            session['last_attempt'] = datetime.now(timezone.utc)
        
        # Check if too many attempts
        if session['login_attempts'] >= 5:
            time_diff = datetime.utcnow() - session['last_attempt']
            if time_diff.total_seconds() < 300:  # 5 minutes lockout
                flash('Too many login attempts. Please try again in 5 minutes.', 'error')
                return render_template('auth/login.html')
            else:
                session['login_attempts'] = 0
        
        # For now, using test user (in production, this would be LDAP)
        if username == 'admin' and password == 'admin123':
            user = User.query.filter_by(username=username).first()
            if not user:
                # Create test user if doesn't exist
                user = User(
                    username='admin',
                    email='admin@example.com',
                    first_name='Admin',
                    last_name='User',
                    department='IT',
                    position='System Administrator'
                )
                db.session.add(user)
                db.session.commit()
            
            login_user(user)
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            session['login_attempts'] = 0  # Reset on successful login
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            session['login_attempts'] += 1
            session['last_attempt'] = datetime.now(timezone.utc)
            flash('Invalid username or password', 'error')
    
    return render_template('auth/login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

# Main routes
@app.route('/')
@login_required
def dashboard():
    # Get dashboard statistics
    total_costs = db.session.query(db.func.sum(Cost.amount)).scalar() or 0
    total_tours = TourProgram.query.count()
    recent_costs = Cost.query.order_by(Cost.created_at.desc()).limit(5).all()
    recent_tours = TourProgram.query.order_by(TourProgram.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         total_costs=total_costs,
                         total_tours=total_tours,
                         recent_costs=recent_costs,
                         recent_tours=recent_tours)

@app.route('/costs')
@login_required
def costs():
    page = request.args.get('page', 1, type=int)
    costs = Cost.query.filter_by(user_id=current_user.id).order_by(Cost.date.desc()).paginate(
        page=page, per_page=10, error_out=False)
    return render_template('costs/index.html', costs=costs)

@app.route('/costs/add', methods=['GET', 'POST'])
@login_required
def add_cost():
    if request.method == 'POST':
        # Validate form data
        errors, validated_data = validate_cost_data(request.form)
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('costs/add.html')
        
        try:
            cost = Cost(
                name=validated_data['name'],
                description=validated_data['description'],
                amount=float(validated_data['amount']),
                category=validated_data['category'],
                date=datetime.strptime(validated_data['date'], '%Y-%m-%d').date(),
                user_id=current_user.id
            )
            db.session.add(cost)
            db.session.commit()
            flash('Cost added successfully!', 'success')
            return redirect(url_for('costs'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding cost. Please try again.', 'error')
            return render_template('costs/add.html')
    
    return render_template('costs/add.html')

@app.route('/tour-programs')
@login_required
def tour_programs():
    page = request.args.get('page', 1, type=int)
    tours = TourProgram.query.filter_by(user_id=current_user.id).order_by(TourProgram.start_date.desc()).paginate(
        page=page, per_page=10, error_out=False)
    return render_template('tour_programs/index.html', tours=tours)

@app.route('/tour-programs/add', methods=['GET', 'POST'])
@login_required
def add_tour_program():
    if request.method == 'POST':
        # Validate form data
        errors, validated_data = validate_tour_data(request.form)
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('tour_programs/add.html')
        
        try:
            tour = TourProgram(
                name=validated_data['name'],
                description=validated_data['description'],
                start_date=datetime.strptime(validated_data['start_date'], '%Y-%m-%d').date(),
                end_date=datetime.strptime(validated_data['end_date'], '%Y-%m-%d').date(),
                destination=validated_data['destination'],
                total_cost=float(validated_data['total_cost']),
                user_id=current_user.id
            )
            db.session.add(tour)
            db.session.commit()
            flash('Tour program added successfully!', 'success')
            return redirect(url_for('tour_programs'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding tour program. Please try again.', 'error')
            return render_template('tour_programs/add.html')
    
    return render_template('tour_programs/add.html')

@app.route('/settings')
@login_required
def settings():
    return render_template('settings/index.html')

@app.route('/settings/users')
@login_required
def settings_users():
    users = User.query.all()
    return render_template('settings/users.html', users=users)

@app.route('/settings/language', methods=['GET', 'POST'])
@login_required
def settings_language():
    if request.method == 'POST':
        language = request.form.get('language', 'en').strip()
        
        # Validate language code
        allowed_languages = ['en', 'tr']
        if language not in allowed_languages:
            flash('Invalid language selection', 'error')
            return redirect(url_for('settings_language'))
        
        session['language'] = language
        flash('Language changed successfully!', 'success')
        return redirect(url_for('settings_language'))
    
    current_lang = session.get('language', 'en')
    return render_template('settings/language.html', current_lang=current_lang)

# API routes for language switching
@app.route('/api/change-language', methods=['POST'])
@login_required
def change_language():
    try:
        # Debug: Log request details
        app.logger.info(f"Language change request from user {current_user.id}")
        app.logger.info(f"Request headers: {dict(request.headers)}")
        app.logger.info(f"Request data: {request.get_data()}")
        
        data = request.get_json()
        if not data:
            app.logger.warning("No JSON data provided")
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        language = data.get('language', 'en').strip()
        app.logger.info(f"Requested language: {language}")
        
        # Validate language code
        allowed_languages = ['en', 'tr']
        if language not in allowed_languages:
            app.logger.warning(f"Invalid language code: {language}")
            return jsonify({'status': 'error', 'message': 'Invalid language'}), 400
        
        session['language'] = language
        app.logger.info(f"Language changed to: {language}")
        return jsonify({'status': 'success', 'language': language})
    except Exception as e:
        app.logger.error(f"Language change error: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Server error'}), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
