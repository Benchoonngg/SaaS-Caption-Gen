import logging
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(level=logging.DEBUG)

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
from werkzeug.security import generate_password_hash
from functools import wraps
from models.user import db, User
from controllers.caption_controller import CaptionController
from flask_migrate import Migrate

# Initialize Flask app
app = Flask(__name__)

# Config
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def home():
    # If user is authenticated, show different nav
    return render_template('index.html', current_user=current_user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already registered')
            return redirect(url_for('register'))
        
        # Create new user
        new_user = User(email=email)
        new_user.set_password(password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed')
            return redirect(url_for('register'))
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('dashboard'))
            
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Admin routes
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    users = User.query.all()
    return render_template('admin/dashboard.html', users=users)

@app.route('/admin/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.email = request.form.get('email')
        user.credits = int(request.form.get('credits', 0))
        user.is_admin = bool(request.form.get('is_admin'))
        
        try:
            db.session.commit()
            flash('User updated successfully')
        except Exception as e:
            db.session.rollback()
            flash('Error updating user')
            
    return render_template('admin/edit_user.html', user=user)

@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Cannot delete your own account')
        return redirect(url_for('admin_dashboard'))
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting user')
        
    return redirect(url_for('admin_dashboard'))

@app.route('/generate-caption', methods=['POST'])
@login_required
def generate_caption():
    data = request.get_json()
    category = data.get('category')
    prompt = data.get('prompt')
    
    if not prompt or not category:
        return jsonify({"error": "Category and prompt are required"}), 400
    
    # Debug logging
    logging.debug(f"Category from frontend: '{category}'")
    logging.debug(f"Prompt: {prompt}")
    
    try:
        # Pass category directly instead of creating instruction
        result = CaptionController.generate(current_user.id, prompt, category)
        logging.debug(f"Controller response: {result}")
        
        # If result is a tuple (error case), return it directly
        if isinstance(result, tuple):
            return jsonify(result[0]), result[1]
        # If result is a dict (success case), return it as JSON
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error in generate_caption route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/update_ai_settings', methods=['POST'])
@login_required
def update_ai_settings():
    try:
        current_user.max_tokens = int(request.form.get('max_tokens', 256))
        current_user.temperature = float(request.form.get('temperature', 0.7))
        current_user.top_p = float(request.form.get('top_p', 0.7))
        current_user.top_k = int(request.form.get('top_k', 50))
        
        db.session.commit()
        flash('Settings updated successfully!', 'success')
    except Exception as e:
        print(f"Debug - Error updating settings: {str(e)}")
        flash('Error updating settings', 'error')
        db.session.rollback()
    
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 