from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

user_ministries = db.Table('user_ministries',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('ministry_id', db.Integer, db.ForeignKey('ministry.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False) # WhatsApp Number
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user') # 'user', 'admin'
    points = db.Column(db.Integer, default=0)
    stage = db.Column(db.String(50), default='Broto')
    badge = db.Column(db.String(50), default='🌱')
    
    # Relationships
    ministries = db.relationship('Ministry', secondary=user_ministries, lazy='subquery',
        backref=db.backref('users', lazy=True))
    
    # State Machine for Bot Navigation
    menu_state = db.Column(db.String(50), default='MAIN') # MAIN, LIST_ACTIONS, ACTION_DETAIL
    menu_context = db.Column(db.String(200), nullable=True) # Stores ID or temp data
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Ministry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

class ActionDefinition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_active = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default='approved') # 'approved', 'pending', 'rejected'
    ministry_id = db.Column(db.Integer, db.ForeignKey('ministry.id'), nullable=True)
    
    # Relationship
    ministry = db.relationship('Ministry', backref=db.backref('actions', lazy=True))

class Block(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    data = db.Column(db.Text, nullable=False) # JSON string of the action/event
    prev_hash = db.Column(db.String(64), nullable=False)
    hash = db.Column(db.String(64), nullable=False)
    
    # Metadata for quick query
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action_id = db.Column(db.Integer, db.ForeignKey('action_definition.id'), nullable=True)
