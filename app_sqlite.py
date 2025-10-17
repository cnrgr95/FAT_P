from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Use SQLite for testing (change to PostgreSQL when ready)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cost_calculation.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('tour_programs', lazy=True))

# System Settings model
class SystemSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Context processor for translations
@app.context_processor
def inject_translations():
    lang = session.get('language', 'en')
    return dict(_=lambda key: get_translation(key, lang))

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
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
            user.last_login = datetime.utcnow()
            db.session.commit()
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
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
        cost = Cost(
            name=request.form['name'],
            description=request.form['description'],
            amount=request.form['amount'],
            category=request.form['category'],
            date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
            user_id=current_user.id
        )
        db.session.add(cost)
        db.session.commit()
        flash('Cost added successfully!', 'success')
        return redirect(url_for('costs'))
    
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
        tour = TourProgram(
            name=request.form['name'],
            description=request.form['description'],
            start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d').date(),
            destination=request.form['destination'],
            total_cost=request.form.get('total_cost') or 0,
            user_id=current_user.id
        )
        db.session.add(tour)
        db.session.commit()
        flash('Tour program added successfully!', 'success')
        return redirect(url_for('tour_programs'))
    
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
        language = request.form['language']
        session['language'] = language
        flash('Language changed successfully!', 'success')
        return redirect(url_for('settings_language'))
    
    current_lang = session.get('language', 'en')
    return render_template('settings/language.html', current_lang=current_lang)

# API routes for language switching
@app.route('/api/change-language', methods=['POST'])
@login_required
def change_language():
    data = request.get_json()
    language = data.get('language', 'en')
    session['language'] = language
    return jsonify({'status': 'success', 'language': language})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
