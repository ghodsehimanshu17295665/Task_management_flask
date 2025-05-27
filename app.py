from dotenv import load_dotenv
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin
from models import db, User
from views import auth_bp, dashboard_bp, home_bp, user_bp, task_bp
from flask_mail import Mail

load_dotenv()
app = Flask(__name__)

# App Configuration
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "f8e99f19e2df4df1b2a5d032bd83b44b316d5e9c76779f8244ec9c8eee1412fe")  # CSRF Protection
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///site.db')

# Fix PostgreSQL URI issue
if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False


# Initialize Extensions
db.init_app(app)  # Initialize database
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = "auth.login"
mail = Mail(app)

# Fix: Add user_loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Load user from database using primary key

# Register Blueprints
app.register_blueprint(home_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(user_bp, url_prefix='/users')
app.register_blueprint(task_bp, url_prefix='/task')

# Ensure the database is created if it doesn't exist
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
