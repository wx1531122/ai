# Prepend these imports if they don't exist (some might overlap)
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os # For a better secret key if not set

# Ensure app config has a decent secret key
# This code will be part of what's injected into app.py's scope where 'app' is defined.
# It needs to be executed after 'app = Flask(__name__)'
# The modifier script will place this block of code correctly.

# Flask-Login setup
login_manager = LoginManager()
# login_manager.init_app(app) # This will be handled by the modifier script after app is available
login_manager.login_view = 'admin_bp.login' # Route name for the login page
login_manager.login_message_category = 'info'

# In-memory user store (for simplicity in this step)
users = {
    "admin": {"password_hash": generate_password_hash("adminpass")}
}

class User(UserMixin):
    def __init__(self, id):
        self.id = id
        self.password_hash = users.get(id, {}).get("password_hash")

    @staticmethod
    def get(user_id):
        if user_id in users:
            return User(user_id)
        return None

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Admin Blueprint
admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin', template_folder='templates/admin')

@admin_bp.route('/')
@login_required
def dashboard():
    return render_template('admin_dashboard.html', title="Admin Dashboard")

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_bp.dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.get(username)
        if user and user.password_hash and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin_bp.dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title="Admin Login")

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin_bp.login'))

# Register blueprint with the app (ensure this is done after app is defined)
# This line will be added separately by the modifier script:
# app.register_blueprint(admin_bp)

# Code to ensure SECRET_KEY is set and LoginManager is initialized with app
# This needs to be run in the context of app.py where 'app' is defined.
# The modifier script will take this block and place it appropriately after app init.
# For now, it's conceptually part of what admin_setup_changes.py provides.
# --- Begin App Context Block ---
# if not app.config.get('SECRET_KEY') or app.config.get('SECRET_KEY') == 'your_secret_key':
#     print("WARNING: Using a default or weak SECRET_KEY. Generating a new one for this session.")
#     app.config['SECRET_KEY'] = os.urandom(24).hex()
# login_manager.init_app(app)
# --- End App Context Block ---
