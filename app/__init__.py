from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../app/static')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'careerassistant-dev-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///career_app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    from app.auth import auth_bp
    from app.routes import main_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    
    with app.app_context():
        db.create_all()
        _seed_questions()
    
    return app

def _seed_questions():
    from app.models import InterviewQuestion
    if InterviewQuestion.query.first():
        return
    
    default_questions = [
        # Software Engineer - Technical
        ('Software Engineer', 'Technical', 'Explain the difference between REST and GraphQL. When would you use each?'),
        ('Software Engineer', 'Technical', 'What is the time complexity of a hash table lookup? Explain collision resolution.'),
        ('Software Engineer', 'Technical', 'Describe how garbage collection works in your preferred language.'),
        ('Software Engineer', 'Technical', 'What are the SOLID principles? Give an example of each.'),
        ('Software Engineer', 'Technical', 'Explain database indexing. When should you add an index?'),
        ('Software Engineer', 'Technical', 'What is the difference between processes and threads?'),
        ('Software Engineer', 'Technical', 'Design a URL shortener like bit.ly.'),
        ('Software Engineer', 'Technical', 'How would you handle a race condition in a distributed system?'),
        
        # Software Engineer - Behavioral
        ('Software Engineer', 'Behavioral', 'Tell me about a time you had a conflict with a teammate. How did you resolve it?'),
        ('Software Engineer', 'Behavioral', 'Describe a project you are most proud of and your specific contributions.'),
        ('Software Engineer', 'Behavioral', 'Tell me about a time you missed a deadline. What happened and what did you learn?'),
        ('Software Engineer', 'Behavioral', 'How do you handle receiving critical feedback on your code?'),
        ('Software Engineer', 'Behavioral', 'Describe a time you had to learn a new technology quickly.'),
        ('Software Engineer', 'Behavioral', 'Tell me about a time you improved a process or system significantly.'),
        
        # Software Engineer - System Design
        ('Software Engineer', 'System Design', 'Design a real-time chat application like Slack or WhatsApp.'),
        ('Software Engineer', 'System Design', 'How would you design a distributed cache?'),
        ('Software Engineer', 'System Design', 'Design a rate limiter for an API.'),
        ('Software Engineer', 'System Design', 'How would you build a notification system that handles millions of users?'),
        
        # Data Scientist - Technical
        ('Data Scientist', 'Technical', 'Explain the bias-variance tradeoff.'),
        ('Data Scientist', 'Technical', 'What is the difference between supervised and unsupervised learning?'),
        ('Data Scientist', 'Technical', 'How do you handle missing data in a dataset?'),
        ('Data Scientist', 'Technical', 'Explain how gradient descent works.'),
        
        # Data Scientist - Behavioral
        ('Data Scientist', 'Behavioral', 'Tell me about a time you had to explain a complex model to a non-technical stakeholder.'),
        ('Data Scientist', 'Behavioral', 'Describe a project where the data quality was poor. How did you handle it?'),
        
        # General
        ('General', 'Behavioral', 'Why do you want to work at this company?'),
        ('General', 'Behavioral', 'Where do you see yourself in 5 years?'),
        ('General', 'Behavioral', 'What is your greatest professional strength? Weakness?'),
        ('General', 'Behavioral', 'Why are you leaving your current role?'),
        ('General', 'Behavioral', 'Do you have any questions for us?'),
    ]
    
    for role_type, category, question_text in default_questions:
        q = InterviewQuestion(role_type=role_type, category=category, question_text=question_text)
        db.session.add(q)
    
    db.session.commit()
