from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    company_code = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    filepath = db.Column(db.String(200), nullable=False)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), nullable=False)

    def __init__(self, position, name, phone):
        self.position = position
        self.name = name
        self.phone = phone