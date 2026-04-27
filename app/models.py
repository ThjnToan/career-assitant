from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), default='')
    title = db.Column(db.String(100), default='')
    location = db.Column(db.String(100), default='')
    phone = db.Column(db.String(50), default='')
    linkedin = db.Column(db.String(200), default='')
    portfolio = db.Column(db.String(200), default='')
    weekly_apps_goal = db.Column(db.Integer, default=5)
    weekly_net_goal = db.Column(db.Integer, default=2)
    target_roles = db.Column(db.String(500), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    applications = db.relationship('Application', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    contacts = db.relationship('Contact', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    activities = db.relationship('Activity', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_target_roles_list(self):
        return [r.strip() for r in self.target_roles.split(',') if r.strip()]

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), default='')
    salary_range = db.Column(db.String(50), default='')
    job_url = db.Column(db.String(500), default='')
    description = db.Column(db.Text, default='')
    status = db.Column(db.String(50), default='Applied')
    source = db.Column(db.String(50), default='')
    applied_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    follow_up_date = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, default='')
    resume_path = db.Column(db.String(500), nullable=True)
    cover_letter_path = db.Column(db.String(500), nullable=True)
    
    interviews = db.relationship('Interview', backref='application', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'company': self.company,
            'role': self.role,
            'status': self.status,
            'location': self.location,
            'salary_range': self.salary_range,
            'source': self.source,
            'applied_date': self.applied_date.isoformat() if self.applied_date else None,
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else None,
            'notes': self.notes,
            'job_url': self.job_url
        }

class Interview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable=False)
    round_num = db.Column(db.Integer, default=1)
    interview_type = db.Column(db.String(50), nullable=False)
    scheduled_date = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    interviewer_name = db.Column(db.String(100), default='')
    interviewer_title = db.Column(db.String(100), default='')
    location = db.Column(db.String(100), default='')
    video_link = db.Column(db.String(500), default='')
    status = db.Column(db.String(20), default='Scheduled')
    questions = db.Column(db.Text, default='')
    notes = db.Column(db.Text, default='')
    rating = db.Column(db.Integer, nullable=True)
    feedback = db.Column(db.Text, default='')
    
    def to_dict(self):
        return {
            'id': self.id,
            'round': self.round_num,
            'type': self.interview_type,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'interviewer_name': self.interviewer_name,
            'interviewer_title': self.interviewer_title,
            'location': self.location,
            'video_link': self.video_link,
            'status': self.status,
            'notes': self.notes,
            'rating': self.rating
        }

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), default='')
    title = db.Column(db.String(100), default='')
    email = db.Column(db.String(120), default='')
    linkedin = db.Column(db.String(200), default='')
    relationship = db.Column(db.String(50), default='')
    last_contact_date = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, default='')
    tags = db.Column(db.String(200), default='')

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    entity_type = db.Column(db.String(50), default='')
    entity_id = db.Column(db.Integer, default=0)
    description = db.Column(db.String(500), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
